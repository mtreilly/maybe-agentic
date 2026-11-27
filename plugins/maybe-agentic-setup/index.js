/**
 * Host half of the maybe-agentic setup panel.
 *
 * Reads the maybe-agentic repository and the global skill installation, then
 * answers two callers from one snapshot: the `agentic_setup_status` tool and the
 * `GET /maybe-agentic/status` route the browser panel fetches.
 *
 * Everything here is read-only. Nothing shells out, so a missing `git` or a
 * sandboxed shell never changes the answer. Failures are returned as data
 * (`ok: false` plus the reason) rather than thrown, because the panel renders
 * them and the tool reports them.
 *
 * @module @local/dsh-maybe-agentic-setup
 */
import { readFile, readdir, stat } from 'node:fs/promises'
import path from 'node:path'
import os from 'node:os'

export const name = 'maybe-agentic-setup'
export const inject = ['tools', 'webServer', 'connection']

/** Route the browser panel reads. Exact path, so the SPA fallback never sees it. */
const ROUTE_PATH = '/maybe-agentic/status'
/** Snapshots are cheap but not free; one cache keeps a page refresh from rescanning. */
const CACHE_MS = 15_000

/**
 * Register the status route and the model-facing tool.
 * @param ctx - Host plugin context carrying tools, webServer and connection.
 * @param config - Optional row config: `repoPath`.
 */
export function apply(ctx, config = {}) {
  const repoPath =
    (typeof config.repoPath === 'string' && config.repoPath) ||
    process.env.MAYBE_AGENTIC_DIR ||
    path.join(os.homedir(), 'Development', 'Personal', 'maybe-agentic')

  let cached = null
  let cachedAt = 0
  let inFlight = null

  const snapshot = (force) => {
    const fresh = Date.now() - cachedAt < CACHE_MS
    if (!force && cached !== null && fresh) return Promise.resolve(cached)
    if (inFlight !== null) return inFlight
    inFlight = collect(repoPath)
      .catch((error) => ({
        ok: false,
        generatedAt: new Date().toISOString(),
        repoPath,
        error: describeError(error),
        issues: [{ level: 'error', text: `Could not read the setup: ${describeError(error)}` }],
      }))
      .then((value) => {
        cached = value
        cachedAt = Date.now()
        inFlight = null
        return value
      })
    return inFlight
  }

  ctx.effect(
    () =>
      ctx.webServer.register({
        kind: 'exact',
        path: ROUTE_PATH,
        async handler(req, res) {
          const rejection = ctx.connection.requestRejection({ headers: req.headers })
          if (rejection !== undefined) {
            res.writeHead(rejection, { 'content-type': 'text/plain' })
            res.end()
            return
          }
          const force = typeof req.url === 'string' && req.url.includes('refresh=1')
          try {
            const value = await snapshot(force)
            const body = JSON.stringify(value)
            res.writeHead(200, {
              'content-type': 'application/json',
              'cache-control': 'no-store',
            })
            res.end(body)
          } catch (error) {
            res.writeHead(500, { 'content-type': 'application/json' })
            res.end(JSON.stringify({ ok: false, error: describeError(error) }))
          }
        },
      }),
    'maybe-agentic-setup: status route',
  )

  ctx.effect(
    () =>
      ctx.tools.register({
        name: 'agentic_setup_status',
        description:
          'Check the maybe-agentic agent setup: whether core and profile skills declared in skills.txt are installed, whether profile files parse cleanly and reference known skills, whether client skill links are intact, and whether MCP servers in mcp/servers.json have their required local paths present. Use when the user asks about their agent setup, skill drift, or a skill that should exist but does not.',
        parameters: {
          refresh: {
            type: 'boolean',
            description: 'Ignore the 15 second cache and rescan now.',
          },
        },
        output: {
          schema: {
            type: 'object',
            additionalProperties: false,
            required: ['ok', 'repoPath', 'summary', 'issues'],
            properties: {
              ok: { type: 'boolean' },
              repoPath: { type: 'string' },
              summary: { type: 'string' },
              issues: {
                type: 'array',
                items: {
                  type: 'object',
                  additionalProperties: false,
                  required: ['level', 'text'],
                  properties: {
                    level: { type: 'string' },
                    text: { type: 'string' },
                  },
                },
              },
            },
          },
          render: (_args, value) => [{ type: 'text', text: value.summary }],
        },
        async execute(args = {}) {
          const value = await snapshot(args.refresh === true)
          return {
            ok: value.ok === true,
            repoPath: value.repoPath,
            summary: summarize(value),
            issues: (value.issues ?? []).slice(0, 40),
          }
        },
      }),
    'maybe-agentic-setup: status tool',
  )
}

/** Build one snapshot from disk. */
async function collect(repoPath) {
  const started = Date.now()
  const issues = []
  const repo = await readRepoIdentity(repoPath)
  const manifest = await readManifest(repoPath, issues)
  const installed = await readInstalledSkills()
  const profileFiles = await readProfiles(repoPath)
  const links = await readLinks()
  const lock = await readLock()
  const mcp = await readMcp(repoPath, issues)

  const declared = manifest.names
  const installedNames = new Set(installed.names)
  const declaredSet = new Set(declared)
  const coreProfile = profileFiles.find((profile) => profile.name === 'core' && !profile.invalid)
  const coreSet = new Set(coreProfile ? coreProfile.skills : [])
  const missingCore = [...coreSet].filter((skill) => declaredSet.has(skill) && !installedNames.has(skill))
  const missing = declared.filter((skill) => !installedNames.has(skill))
  const extra = installed.names.filter((skill) => !declaredSet.has(skill))

  if (repo.exists && missingCore.length > 0) {
    issues.push({
      level: 'error',
      text: `${missingCore.length} core skill${missingCore.length === 1 ? ' is' : 's are'} not installed: ${preview(missingCore)}`,
    })
  } else if (repo.exists && missing.length > 0) {
    issues.push({
      level: 'warn',
      text: `${missing.length} optional manifest skill${missing.length === 1 ? ' is' : 's are'} not installed (core is complete): ${preview(missing)}`,
    })
  }

  const profiles = profileFiles.map((profile) => {
    if (profile.invalid) {
      issues.push({
        level: 'error',
        text: `Profile "${profile.name}" could not be parsed: ${profile.error}`,
      })
      return {
        name: profile.name,
        extends: [],
        skillCount: 0,
        unknown: [],
        invalid: true,
      }
    }
    const unknown = profile.skills.filter((skill) => !declaredSet.has(skill))
    const notInstalled = profile.skills.filter((skill) => !installedNames.has(skill))
    if (unknown.length > 0) {
      issues.push({
        level: 'error',
        text: `Profile "${profile.name}" names ${unknown.length} skill${unknown.length === 1 ? '' : 's'} missing from skills.txt: ${preview(unknown)}`,
      })
    } else if (notInstalled.length > 0) {
      issues.push({
        level: 'warn',
        text: `Profile "${profile.name}" names ${notInstalled.length} skill${notInstalled.length === 1 ? '' : 's'} that ${notInstalled.length === 1 ? 'is' : 'are'} not installed: ${preview(notInstalled)}`,
      })
    }
    return {
      name: profile.name,
      extends: profile.extends,
      skillCount: profile.skills.length,
      unknown,
    }
  })

  for (const client of links) {
    if (!client.exists) continue
    if (client.broken.length > 0) {
      issues.push({
        level: 'error',
        text: `${client.label}: ${client.broken.length} broken skill link${client.broken.length === 1 ? '' : 's'} (${preview(client.broken)})`,
      })
    }
  }

  if (!lock.exists) {
    issues.push({ level: 'warn', text: 'No global skill lockfile at ~/.agents/.skill-lock.json.' })
  }

  if (!repo.exists) {
    issues.push({ level: 'error', text: `Repository not found at ${repoPath}.` })
  } else if (!manifest.found) {
    issues.push({ level: 'error', text: 'skills.txt is missing, so the manifest cannot be checked.' })
  }

  for (const server of mcp.servers) {
    if (server.missingRequires.length > 0) {
      issues.push({
        level: 'warn',
        text: `MCP "${server.name}" is skipped because ${server.missingRequires.join(', ')} does not exist.`,
      })
    }
  }

  const ok = issues.every((issue) => issue.level !== 'error')

  return {
    ok,
    generatedAt: new Date().toISOString(),
    durationMs: Date.now() - started,
    repoPath,
    repo: { path: repoPath, ...repo },
    skills: {
      declared: declared.length,
      installed: installed.names.length,
      missing,
      extraCount: extra.length,
      manifestMtime: manifest.mtime,
    },
    profiles,
    links,
    lock,
    mcp,
    issues,
  }
}

/** Branch and short commit, read straight from the git directory. */
async function readRepoIdentity(repoPath) {
  try {
    const info = await stat(repoPath)
    if (!info.isDirectory()) return { exists: false, branch: null, commit: null }
  } catch {
    return { exists: false, branch: null, commit: null }
  }

  let gitDir = path.join(repoPath, '.git')
  try {
    const dotGit = await stat(gitDir)
    if (dotGit.isFile()) {
      const pointer = (await readFile(gitDir, 'utf8')).trim()
      const match = /^gitdir:\s*(.+)$/.exec(pointer)
      if (match !== null) gitDir = path.resolve(repoPath, match[1])
    }
  } catch {
    return { exists: true, branch: null, commit: null }
  }

  let head
  try {
    head = (await readFile(path.join(gitDir, 'HEAD'), 'utf8')).trim()
  } catch {
    return { exists: true, branch: null, commit: null }
  }

  if (!head.startsWith('ref: ')) {
    return { exists: true, branch: '(detached)', commit: head.slice(0, 7) }
  }

  const ref = head.slice(5).trim()
  const branch = ref.startsWith('refs/heads/') ? ref.slice('refs/heads/'.length) : ref
  let commit = null
  try {
    commit = (await readFile(path.join(gitDir, ref), 'utf8')).trim().slice(0, 7)
  } catch {
    try {
      const packed = await readFile(path.join(gitDir, 'packed-refs'), 'utf8')
      const line = packed.split('\n').find((entry) => entry.endsWith(` ${ref}`))
      if (line !== undefined) commit = line.slice(0, 7)
    } catch {
      commit = null
    }
  }
  return { exists: true, branch, commit }
}

/** Parse skills.txt: the last token on each line is the skill name. */
async function readManifest(repoPath, issues) {
  const file = path.join(repoPath, 'skills.txt')
  try {
    const text = await readFile(file, 'utf8')
    const info = await stat(file)
    const names = []
    for (const raw of text.split('\n')) {
      const line = raw.trim()
      if (line === '' || line.startsWith('#')) continue
      const parts = line.split(/\s+/)
      const skill = parts[parts.length - 1]
      if (skill !== '' && !names.includes(skill)) names.push(skill)
    }
    return { found: true, names, mtime: info.mtime.toISOString() }
  } catch {
    return { found: false, names: [], mtime: null }
  }
}

/** Installed skills are directories under ~/.agents/skills that carry a SKILL.md. */
async function readInstalledSkills() {
  const root = path.join(os.homedir(), '.agents', 'skills')
  const names = []
  let entries
  try {
    entries = await readdir(root, { withFileTypes: true })
  } catch {
    return { root, names }
  }
  for (const entry of entries) {
    if (entry.name.startsWith('.')) continue
    const dir = path.join(root, entry.name)
    try {
      const skillFile = await stat(path.join(dir, 'SKILL.md'))
      if (skillFile.isFile()) names.push(entry.name)
    } catch {
      // A folder without SKILL.md is not an installed skill.
    }
  }
  names.sort((a, b) => (a < b ? -1 : a > b ? 1 : 0))
  return { root, names }
}

/** One row per profiles/*.json file, with `extends` normalised to an array. */
async function readProfiles(repoPath) {
  const dir = path.join(repoPath, 'profiles')
  let entries
  try {
    entries = await readdir(dir)
  } catch {
    return []
  }
  const profiles = []
  for (const file of entries.filter((entry) => entry.endsWith('.json')).sort()) {
    const name = file.replace(/\.json$/, '')
    try {
      const parsed = JSON.parse(await readFile(path.join(dir, file), 'utf8'))
      if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
        profiles.push({ name, extends: [], skills: [], invalid: true, error: 'root value must be a JSON object' })
        continue
      }
      if (parsed.skills !== undefined && (!Array.isArray(parsed.skills) || parsed.skills.some((s) => typeof s !== 'string'))) {
        profiles.push({ name, extends: [], skills: [], invalid: true, error: 'skills must be an array of strings' })
        continue
      }
      if (parsed.extends !== undefined && (!Array.isArray(parsed.extends) || parsed.extends.some((s) => typeof s !== 'string'))) {
        profiles.push({ name, extends: [], skills: [], invalid: true, error: 'extends must be an array of strings' })
        continue
      }
      const skills = Array.isArray(parsed.skills) ? parsed.skills : []
      const parents = Array.isArray(parsed.extends) ? parsed.extends : []
      profiles.push({ name, extends: parents, skills, invalid: false })
    } catch (error) {
      profiles.push({ name, extends: [], skills: [], invalid: true, error: describeError(error) })
    }
  }
  return profiles
}

/** Client skill directories, honouring the env overrides the clients themselves use. */
async function readLinks() {
  const home = os.homedir()
  const claudeRoot = process.env.CLAUDE_CONFIG_DIR || path.join(home, '.claude')
  const codexRoot = process.env.CODEX_HOME || path.join(home, '.codex')
  const xdg = process.env.XDG_CONFIG_HOME || path.join(home, '.config')
  const piRoot = process.env.PI_CODING_AGENT_DIR || path.join(home, '.pi', 'agent')

  const clients = [
    { id: 'claude', label: 'Claude Code', dir: path.join(claudeRoot, 'skills') },
    { id: 'codex', label: 'Codex', dir: path.join(codexRoot, 'skills') },
    { id: 'opencode', label: 'OpenCode', dir: path.join(xdg, 'opencode', 'skills') },
    { id: 'pi', label: 'Pi', dir: path.join(piRoot, 'skills') },
  ]

  const results = []
  for (const client of clients) {
    results.push({ ...client, ...(await scanLinkDir(client.dir)) })
  }
  return results
}

/** Count skill entries and broken symlinks in one client directory. */
async function scanLinkDir(dir) {
  let entries
  try {
    entries = await readdir(dir, { withFileTypes: true })
  } catch {
    return { exists: false, entries: 0, broken: [] }
  }
  let count = 0
  const broken = []
  for (const entry of entries) {
    if (entry.name.startsWith('.')) continue
    const target = path.join(dir, entry.name)
    if (entry.isSymbolicLink()) {
      count += 1
      try {
        await stat(target)
      } catch {
        broken.push(entry.name)
      }
      continue
    }
    if (entry.isDirectory()) count += 1
  }
  return { exists: true, entries: count, broken }
}

/** Lockfile presence and size. Local-source skills legitimately have no record. */
async function readLock() {
  const file = path.join(os.homedir(), '.agents', '.skill-lock.json')
  try {
    const text = await readFile(file, 'utf8')
    const info = await stat(file)
    const parsed = JSON.parse(text)
    const entries = parsed !== null && typeof parsed.skills === 'object' && parsed.skills !== null
      ? Object.keys(parsed.skills).length
      : 0
    return { path: file, exists: true, entries, updatedAt: info.mtime.toISOString() }
  } catch {
    return { path: file, exists: false, entries: 0, updatedAt: null }
  }
}

/** The MCP manifest, plus the per-machine skips in mcp/local.json. */
async function readMcp(repoPath, issues) {
  const file = path.join(repoPath, 'mcp', 'servers.json')
  const empty = { path: file, exists: false, count: 0, skipped: [], servers: [] }
  let parsed
  try {
    parsed = JSON.parse(await readFile(file, 'utf8'))
  } catch {
    if (repoPath !== '' ) {
      issues.push({ level: 'warn', text: `No readable MCP manifest at ${file}.` })
    }
    return empty
  }

  const skips = await readLocalSkips(repoPath)
  const raw = parsed !== null && typeof parsed.servers === 'object' && parsed.servers !== null ? parsed.servers : {}
  const servers = []
  for (const [serverName, definition] of Object.entries(raw)) {
    const value = definition !== null && typeof definition === 'object' ? definition : {}
    const requires = Array.isArray(value.requires) ? value.requires : []
    const missingRequires = []
    for (const required of requires) {
      const expanded = String(required).replace(/^~(?=$|\/)/, os.homedir())
      try {
        await stat(expanded)
      } catch {
        missingRequires.push(String(required))
      }
    }
    const kind = typeof value.url === 'string' ? 'remote' : typeof value.source === 'object' && value.source !== null ? 'source' : 'local'
    const templated = JSON.stringify(value).includes('{agent}')
    servers.push({
      name: serverName,
      kind,
      optional: value.optional === true,
      templated,
      skipped: skips.includes(serverName),
      missingRequires,
      requires,
    })
  }
  servers.sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0))
  return {
    path: file,
    exists: true,
    count: servers.length,
    skipped: skips,
    servers,
  }
}

/** Per-machine skips; the file is untracked and optional. */
async function readLocalSkips(repoPath) {
  try {
    const parsed = JSON.parse(await readFile(path.join(repoPath, 'mcp', 'local.json'), 'utf8'))
    return Array.isArray(parsed?.skip) ? parsed.skip.filter((entry) => typeof entry === 'string') : []
  } catch {
    return []
  }
}

/** A one-paragraph summary for the tool result. */
function summarize(value) {
  if (value.ok !== true && value.repo === undefined) {
    return `Setup check failed: ${value.error ?? 'unknown error'}`
  }
  const errors = (value.issues ?? []).filter((issue) => issue.level === 'error').length
  const warnings = (value.issues ?? []).filter((issue) => issue.level === 'warn').length
  if (value.ok === true) {
    return `Setup healthy: ${value.skills.installed} skills installed, ${value.skills.declared} declared, ${value.profiles.length} profiles, ${value.mcp.count} MCP servers. ${warnings} warning${warnings === 1 ? '' : 's'}.`
  }
  const first = (value.issues ?? []).find((issue) => issue.level === 'error')
  return `Setup has ${errors} error${errors === 1 ? '' : 's'} and ${warnings} warning${warnings === 1 ? '' : 's'} at ${value.repoPath}. First: ${first?.text ?? 'unknown'}.`
}

function preview(list, limit = 4) {
  const shown = list.slice(0, limit).join(', ')
  return list.length > limit ? `${shown} and ${list.length - limit} more` : shown
}

function describeError(error) {
  if (error instanceof Error) return error.message
  return String(error)
}
