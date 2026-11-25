/**
 * Browser half of the maybe-agentic setup panel.
 *
 * Two tabs under Settings → Plugins:
 * - Setup reads the Host snapshot from `GET /maybe-agentic/status`.
 * - Jig renders the same primitives with live knobs, so the design can be
 *   adjusted without editing the panel between reloads.
 *
 * Both tabs render from one set of primitives and one design store, so what the
 * jig shows is what the panel uses. Styling goes through theme tokens only.
 */
window.__ModuleLoader__.load({
  id: '@local/dsh-maybe-agentic-setup',
  factory(require) {
    const React = require('react')
    const h = React.createElement

    /** Locale namespace owned by this plugin. */
    const NS = 'maybe-agentic.setup'
    /** Host route carrying the snapshot. */
    const ENDPOINT = '/maybe-agentic/status'
    /** Rows rendered before a list collapses into "+N more". */
    const VISIBLE = 6
    /** Where the jig stores the chosen design. */
    const DESIGN_KEY = 'dsh.maybe-agentic.design'

    const C = {
      text: 'var(--dsw-alias-label-primary)',
      dim: 'var(--dsw-alias-label-secondary)',
      border: 'var(--dsw-alias-border-l1)',
      card: 'var(--dsw-alias-bg-layer-1)',
      layer: 'var(--dsw-alias-bg-layer-2)',
      accent: 'var(--dsw-alias-brand-primary)',
      ok: 'var(--dsw-alias-state-success-primary)',
      warn: 'var(--dsw-alias-state-warn-primary)',
      error: 'var(--dsw-alias-state-error-primary)',
      idle: 'var(--dsw-alias-state-idle-primary)',
    }

    /** Tone names the primitives accept, mapped onto palette entries. */
    const TONES = { ok: C.ok, warn: C.warn, error: C.error, idle: C.idle }

    // ---------------------------------------------------------------- design

    const DESIGN_DEFAULTS = { density: 'comfortable', radius: 'medium', type: 'default' }

    let designState = null
    const designListeners = new Set()

    function readDesign() {
      try {
        const raw = window.localStorage.getItem(DESIGN_KEY)
        if (raw === null) return { ...DESIGN_DEFAULTS }
        const parsed = JSON.parse(raw)
        return {
          density: parsed.density === 'compact' ? 'compact' : 'comfortable',
          radius: parsed.radius === 'soft' || parsed.radius === 'round' ? parsed.radius : 'medium',
          type: parsed.type === 'small' || parsed.type === 'large' ? parsed.type : 'default',
        }
      } catch {
        return { ...DESIGN_DEFAULTS }
      }
    }

    function currentDesign() {
      if (designState === null) designState = readDesign()
      return designState
    }

    function subscribeDesign(listener) {
      designListeners.add(listener)
      return () => designListeners.delete(listener)
    }

    function writeDesign(patch) {
      designState = { ...currentDesign(), ...patch }
      try {
        window.localStorage.setItem(DESIGN_KEY, JSON.stringify(designState))
      } catch {
        // A blocked storage still keeps the in-memory choice for this page.
      }
      for (const listener of [...designListeners]) listener()
    }

    function useDesign() {
      return React.useSyncExternalStore(subscribeDesign, currentDesign, currentDesign)
    }

    /** One scale object per design choice; primitives read it instead of hard numbers. */
    function scale(design) {
      const compact = design.density === 'compact'
      const body = design.type === 'small' ? 12 : design.type === 'large' ? 14 : 13
      return {
        compact,
        radius: design.radius === 'soft' ? 6 : design.radius === 'round' ? 12 : 9,
        padX: compact ? 10 : 12,
        padY: compact ? 6 : 9,
        rowGap: compact ? 8 : 10,
        rootGap: compact ? 14 : 18,
        body,
        metricValue: body + 3,
      }
    }

    function cardStyle(k) {
      return {
        border: `1px solid ${C.border}`,
        borderRadius: k.radius,
        background: C.card,
        overflow: 'hidden',
      }
    }

    function rootStyle(k) {
      return {
        display: 'flex',
        flexDirection: 'column',
        gap: k.rootGap,
        padding: '4px 2px 24px',
        color: C.text,
        font: `${k.body}px/1.5 ui-sans-serif, system-ui, -apple-system, sans-serif`,
      }
    }

    // ------------------------------------------------------------ primitives

    function Button(props) {
      const k = scale(useDesign())
      const busy = props.busy === true
      const disabled = busy || props.disabled === true
      return h(
        'button',
        {
          type: 'button',
          disabled,
          onClick: props.onClick,
          style: {
            appearance: 'none',
            border: `1px solid ${C.border}`,
            background: 'transparent',
            color: C.text,
            borderRadius: k.radius,
            padding: `${k.compact ? 4 : 5}px ${k.compact ? 9 : 11}px`,
            font: 'inherit',
            fontSize: k.body - 0.5,
            cursor: disabled ? 'default' : 'pointer',
            opacity: disabled ? 0.55 : 1,
          },
        },
        props.label,
      )
    }

    function Pill(props) {
      const k = scale(useDesign())
      const tone = props.tone ?? 'idle'
      const color = TONES[tone] ?? C.dim
      return h(
        'span',
        {
          style: {
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            padding: `2px ${k.compact ? 6 : 8}px`,
            borderRadius: 999,
            fontSize: k.body - 1.5,
            border: `1px solid ${tone === 'idle' ? C.border : color}`,
            color: tone === 'idle' ? C.dim : color,
            whiteSpace: 'nowrap',
          },
        },
        props.dot === true
          ? h('span', {
              style: {
                width: 6,
                height: 6,
                borderRadius: 3,
                flex: '0 0 auto',
                background: tone === 'idle' ? C.idle : color,
              },
            })
          : null,
        props.label,
      )
    }

    function Metric(props) {
      const k = scale(useDesign())
      return h(
        'div',
        {
          style: {
            background: C.card,
            padding: `${k.compact ? 8 : 10}px ${k.padX}px`,
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
          },
        },
        h(
          'div',
          {
            style: {
              fontSize: k.metricValue,
              fontWeight: 600,
              letterSpacing: '-0.02em',
              color: props.tone === 'error' ? C.error : C.text,
            },
          },
          props.value,
        ),
        h(
          'div',
          {
            style: {
              fontSize: 11,
              color: C.dim,
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
            },
          },
          props.label,
          props.hint === undefined
            ? null
            : h('span', { style: { textTransform: 'none', letterSpacing: 0 } }, ` · ${props.hint}`),
        ),
      )
    }

    function Metrics(props) {
      const k = scale(useDesign())
      return h(
        'div',
        {
          style: {
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
            gap: 1,
            background: C.border,
            border: `1px solid ${C.border}`,
            borderRadius: k.radius,
            overflow: 'hidden',
          },
        },
        props.children,
      )
    }

    function Section(props) {
      const k = scale(useDesign())
      return h(
        'section',
        { style: { display: 'flex', flexDirection: 'column', gap: k.compact ? 6 : 7 } },
        h(
          'div',
          { style: { display: 'flex', alignItems: 'baseline', gap: 8 } },
          h('span', { style: { fontSize: 12, fontWeight: 600 } }, props.title),
          props.note === undefined
            ? null
            : h('span', { style: { fontSize: 11.5, color: C.dim } }, props.note),
        ),
        props.children,
      )
    }

    function Row(props) {
      const k = scale(useDesign())
      return h(
        'div',
        {
          style: {
            display: 'flex',
            alignItems: 'baseline',
            gap: k.rowGap,
            padding: `${k.padY}px ${k.padX}px`,
            borderTop: props.first === true ? 'none' : `1px solid ${C.border}`,
          },
        },
        h(
          'span',
          {
            title: props.title ?? props.name,
            style: {
              fontSize: k.body - 0.5,
              minWidth: 0,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            },
          },
          props.name,
        ),
        props.extra === undefined
          ? null
          : h('span', { style: { fontSize: 11, color: C.dim, flex: '0 0 auto' } }, props.extra),
        h(
          'span',
          { style: { marginLeft: 'auto', fontSize: 12, color: C.dim, whiteSpace: 'nowrap' } },
          props.value,
        ),
      )
    }

    function Empty(props) {
      const k = scale(useDesign())
      return h(
        'div',
        {
          style: {
            padding: `${k.padY + 1}px ${k.padX}px`,
            color: C.dim,
            fontSize: k.body - 0.5,
          },
        },
        props.text,
      )
    }

    function List(props) {
      const k = scale(useDesign())
      if (props.rows.length === 0) return h('div', { style: cardStyle(k) }, h(Empty, { text: props.empty }))
      const visible = props.rows.slice(0, VISIBLE)
      const rest = props.rows.length - visible.length
      return h(
        'div',
        { style: cardStyle(k) },
        visible.map((row, index) =>
          props.render !== undefined ? props.render(row, index) : h(Row, { key: row.name, ...row, first: index === 0 }),
        ),
        rest > 0 ? h(Empty, { text: `+${rest} more` }) : null,
      )
    }

    function Banner(props) {
      const k = scale(useDesign())
      return h(
        'div',
        {
          style: {
            border: `1px solid ${props.tone === 'error' ? C.error : C.border}`,
            borderRadius: k.radius,
            padding: `${k.padY + 1}px ${k.padX}px`,
            background: C.layer,
            color: C.text,
            fontSize: k.body - 0.5,
          },
        },
        props.children,
      )
    }

    function Mono(props) {
      return h(
        'span',
        {
          style: {
            fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
            fontSize: props.size ?? 11.5,
          },
        },
        props.children,
      )
    }

    function Skeleton(props) {
      return h('div', {
        style: {
          width: props.width ?? '100%',
          height: props.height ?? 10,
          borderRadius: 999,
          background: C.idle,
          opacity: 0.35,
        },
      })
    }

    function Segmented(props) {
      const k = scale(useDesign())
      return h(
        'div',
        {
          style: {
            display: 'inline-flex',
            gap: 2,
            padding: 2,
            border: `1px solid ${C.border}`,
            borderRadius: k.radius + 1,
          },
        },
        props.options.map((option) =>
          h(
            'button',
            {
              key: option.id,
              type: 'button',
              onClick: () => props.onChange(option.id),
              style: {
                appearance: 'none',
                border: 'none',
                background: option.id === props.value ? C.layer : 'transparent',
                color: option.id === props.value ? C.text : C.dim,
                borderRadius: k.radius,
                padding: `3px ${k.compact ? 8 : 10}px`,
                font: 'inherit',
                fontSize: k.body - 1,
                cursor: option.id === props.value ? 'default' : 'pointer',
              },
            },
            option.label,
          ),
        ),
      )
    }

    // -------------------------------------------------------------- helpers

    function clock(iso) {
      if (iso === null || iso === undefined) return ''
      const then = new Date(iso).getTime()
      if (Number.isNaN(then)) return ''
      return new Date(then).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      })
    }

    function issueTone(level) {
      if (level === 'error') return C.error
      if (level === 'warn') return C.warn
      return C.idle
    }

    // ----------------------------------------------------------- setup panel

    function makePanel(t) {
      function Panel() {
        const [state, setState] = React.useState({ status: 'loading' })
        const [busy, setBusy] = React.useState(true)
        const k = scale(useDesign())

        const load = React.useCallback((force, signal) => {
          setBusy(true)
          setState((current) => (current.data === undefined ? { status: 'loading' } : current))
          const url = force ? `${ENDPOINT}?refresh=1` : ENDPOINT
          fetch(url, { credentials: 'same-origin', headers: { accept: 'application/json' }, signal })
            .then((response) => {
              if (!response.ok) throw new Error(`HTTP ${response.status}`)
              return response.json()
            })
            .then((data) => {
              if (signal !== undefined && signal.aborted) return
              setState({ status: 'ready', data })
              setBusy(false)
            })
            .catch((error) => {
              if (signal !== undefined && signal.aborted) return
              setState((current) => ({
                status: 'error',
                data: current.data,
                error: error instanceof Error ? error.message : String(error),
              }))
              setBusy(false)
            })
        }, [])

        React.useEffect(() => {
          const controller = new AbortController()
          load(false, controller.signal)
          return () => controller.abort()
        }, [load])

        const data = state.data
        const issues = data?.issues ?? []
        const errors = issues.filter((issue) => issue.level === 'error').length
        const warnings = issues.filter((issue) => issue.level === 'warn').length

        const head = h(
          'div',
          { style: { display: 'flex', alignItems: 'flex-start', gap: 12 } },
          h(
            'div',
            { style: { display: 'flex', flexDirection: 'column', gap: 3, minWidth: 0, flex: 1 } },
            h(
              'div',
              { style: { display: 'flex', alignItems: 'center', gap: 9, flexWrap: 'wrap' } },
              h('span', { style: { fontSize: 15, fontWeight: 600, letterSpacing: '-0.01em' } }, t('title')),
              data === undefined
                ? null
                : h(Pill, {
                    tone: data.ok === true ? 'ok' : 'error',
                    dot: true,
                    label:
                      data.ok === true
                        ? t('state.healthy')
                        : `${errors} ${errors === 1 ? 'error' : 'errors'}`,
                  }),
            ),
            h(
              'div',
              { style: { display: 'flex', flexWrap: 'wrap', gap: '2px 10px', color: C.dim, fontSize: 12 } },
              h(Mono, null, data?.repoPath ?? '~/Development/Personal/maybe-agentic'),
              data?.repo?.exists === true && data.repo.branch !== null
                ? h(
                    Mono,
                    null,
                    `${data.repo.branch}${data.repo.commit === null ? '' : ` @ ${data.repo.commit}`}`,
                  )
                : null,
              data === undefined ? null : h('span', {}, `${t('checked')} ${clock(data.generatedAt)}`),
            ),
          ),
          h(Button, { label: busy ? t('action.checking') : t('action.refresh'), busy, onClick: () => load(true) }),
        )

        if (state.status === 'error' && data === undefined) {
          return h(
            'div',
            { style: rootStyle(k) },
            head,
            h(Banner, { tone: 'error' }, `${t('state.error')} ${state.error}`),
          )
        }

        if (data === undefined) {
          return h(
            'div',
            { style: rootStyle(k) },
            head,
            h('div', { style: { display: 'flex', flexDirection: 'column', gap: 7, maxWidth: 260 } },
              h(Skeleton, { width: '70%' }),
              h(Skeleton, { width: '45%' }),
            ),
            h('div', { style: { color: C.dim, fontSize: 12.5 } }, t('state.loading')),
          )
        }

        const skills = data.skills ?? { installed: 0, declared: 0, missing: [], extraCount: 0 }
        const profiles = data.profiles ?? []
        const links = data.links ?? []
        const mcp = data.mcp ?? { count: 0, servers: [], skipped: [] }
        const presentLinks = links.filter((client) => client.exists === true).length
        const skippedServers = mcp.servers.filter((server) => server.skipped === true).length

        return h(
          'div',
          { style: rootStyle(k) },
          head,
          state.status === 'error' ? h(Banner, { tone: 'error' }, `${t('state.error')} ${state.error}`) : null,
          h(
            Metrics,
            null,
            h(Metric, {
              value: `${skills.installed} / ${skills.declared}`,
              label: t('metric.skills'),
              hint: t('metric.skillsHint'),
            }),
            h(Metric, {
              value: String(profiles.length),
              label: t('metric.profiles'),
              hint: t('metric.profilesHint'),
            }),
            h(Metric, {
              value: `${presentLinks} / ${links.length}`,
              label: t('metric.links'),
              hint: t('metric.linksHint'),
            }),
            h(Metric, {
              value: String(mcp.count),
              label: t('metric.mcp'),
              hint: `${skippedServers} ${t('metric.mcpHint')}`,
            }),
          ),
          h(
            Section,
            {
              title: t('section.issues'),
              note: errors + warnings === 0 ? undefined : `${errors} errors · ${warnings} warnings`,
            },
            issues.length === 0
              ? h('div', { style: cardStyle(k) }, h(Empty, { text: t('section.issuesNone') }))
              : h(
                  'div',
                  { style: cardStyle(k) },
                  issues.slice(0, 12).map((issue, index) =>
                    h(
                      'div',
                      {
                        key: `${index}-${issue.text}`,
                        style: {
                          display: 'flex',
                          gap: 9,
                          alignItems: 'baseline',
                          padding: `${k.padY}px ${k.padX}px`,
                          borderTop: index === 0 ? 'none' : `1px solid ${C.border}`,
                        },
                      },
                      h('span', {
                        style: {
                          width: 6,
                          height: 6,
                          borderRadius: 3,
                          flex: '0 0 auto',
                          marginTop: 5,
                          background: issueTone(issue.level),
                        },
                      }),
                      h('span', { style: { fontSize: k.body - 0.5, minWidth: 0 } }, issue.text),
                    ),
                  ),
                  issues.length > 12 ? h(Empty, { text: `+${issues.length - 12} more` }) : null,
                ),
          ),
          h(
            Section,
            { title: t('section.skills'), note: t('section.skillsNote') },
            skills.missing.length > 0
              ? h(List, { rows: skills.missing.map((skill) => ({ name: skill, value: t('label.missing') })), empty: '' })
              : h(
                  'div',
                  { style: cardStyle(k) },
                  h(Row, {
                    first: true,
                    name: `${skills.installed} installed`,
                    value: skills.extraCount === 0 ? 'no extras' : `${skills.extraCount} ${t('label.extra')}`,
                  }),
                ),
          ),
          h(
            Section,
            { title: t('section.profiles'), note: t('section.profilesNote') },
            profiles.length === 0
              ? h('div', { style: cardStyle(k) }, h(Empty, { text: 'No profile files found.' }))
              : h(List, {
                  rows: profiles.map((profile) => ({
                    name: profile.name,
                    title: profile.name,
                    extra: profile.extends.length === 0 ? t('label.noExtends') : `+${profile.extends.join(', +')}`,
                    value:
                      profile.unknown.length > 0
                        ? `${profile.skillCount} · ${profile.unknown.length} unknown`
                        : `${profile.skillCount} skills`,
                  })),
                  empty: '',
                }),
          ),
          h(
            Section,
            { title: t('section.links'), note: t('section.linksNote') },
            h(List, {
              rows: links.map((client) => ({
                name: client.label,
                title: client.dir,
                extra: client.dir.replace(/^.*\/\./, '~/.').slice(0, 42),
                value:
                  client.exists !== true
                    ? t('label.absent')
                    : client.broken.length > 0
                      ? `${client.entries} · ${client.broken.length} ${t('label.broken')}`
                      : `${client.entries} linked`,
              })),
              empty: 'No client directories found.',
            }),
          ),
          h(
            Section,
            { title: t('section.mcp'), note: t('section.mcpNote') },
            mcp.servers.length === 0
              ? h('div', { style: cardStyle(k) }, h(Empty, { text: 'No MCP manifest found.' }))
              : h(List, {
                  rows: mcp.servers.map((server) => ({
                    name: server.name,
                    title: server.name,
                    extra: [
                      server.kind,
                      server.optional === true ? t('label.optional') : null,
                      server.templated === true ? t('label.templated') : null,
                    ]
                      .filter(Boolean)
                      .join(' · '),
                    value:
                      server.missingRequires.length > 0
                        ? `${server.missingRequires.length} missing path${server.missingRequires.length === 1 ? '' : 's'}`
                        : server.skipped === true
                          ? t('label.skipped')
                          : '',
                  })),
                  empty: '',
                }),
          ),
          h(
            'div',
            { style: { color: C.dim, fontSize: 11 } },
            `${data.durationMs ?? 0} ms scan`,
          ),
        )
      }

      return Panel
    }

    // ------------------------------------------------------------- jig panel

    function makeJig(t) {
      function Jig() {
        const design = useDesign()
        const k = scale(design)

        const densityOptions = [
          { id: 'comfortable', label: t('jig.density.comfortable') },
          { id: 'compact', label: t('jig.density.compact') },
        ]
        const radiusOptions = [
          { id: 'soft', label: t('jig.radius.soft') },
          { id: 'medium', label: t('jig.radius.medium') },
          { id: 'round', label: t('jig.radius.round') },
        ]
        const typeOptions = [
          { id: 'small', label: t('jig.type.small') },
          { id: 'default', label: t('jig.type.default') },
          { id: 'large', label: t('jig.type.large') },
        ]

        const knobRow = (first, label, control) =>
          h(
            'div',
            {
              style: {
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                flexWrap: 'wrap',
                padding: `${k.padY}px ${k.padX}px`,
                borderTop: first === true ? 'none' : `1px solid ${C.border}`,
              },
            },
            h(
              'span',
              {
                style: {
                  fontSize: 11,
                  color: C.dim,
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                  minWidth: 64,
                },
              },
              label,
            ),
            control,
          )

        const sampleRows = [
          { name: 'chrome-devtools', extra: 'source', value: '4 paths' },
          { name: 'vsware', extra: 'local · optional · per-agent', value: 'skipped' },
          {
            name: 'cloudflare-observability-with-an-unreasonable-name',
            extra: 'remote',
            value: '2 missing paths',
          },
        ]

        return h(
          'div',
          { style: rootStyle(k) },
          h(
            'div',
            { style: { display: 'flex', flexDirection: 'column', gap: 3 } },
            h('span', { style: { fontSize: 15, fontWeight: 600, letterSpacing: '-0.01em' } }, t('jig.title')),
            h('span', { style: { fontSize: 12, color: C.dim } }, t('jig.intro')),
          ),
          h(
            'div',
            { style: cardStyle(k) },
            knobRow(true, t('jig.density'), h(Segmented, {
              options: densityOptions,
              value: design.density,
              onChange: (value) => writeDesign({ density: value }),
            })),
            knobRow(false, t('jig.radius'), h(Segmented, {
              options: radiusOptions,
              value: design.radius,
              onChange: (value) => writeDesign({ radius: value }),
            })),
            knobRow(false, t('jig.type'), h(Segmented, {
              options: typeOptions,
              value: design.type,
              onChange: (value) => writeDesign({ type: value }),
            })),
            knobRow(false, '', h(Button, {
              label: t('jig.reset'),
              onClick: () => writeDesign(DESIGN_DEFAULTS),
            })),
          ),
          h(
            Section,
            { title: t('jig.metrics'), note: t('jig.metricsNote') },
            h(
              Metrics,
              null,
              h(Metric, { value: '68 / 39', label: t('metric.skills'), hint: t('metric.skillsHint') }),
              h(Metric, { value: '4', label: t('metric.profiles'), hint: t('metric.profilesHint') }),
              h(Metric, { value: '4 / 4', label: t('metric.links'), hint: t('metric.linksHint') }),
              h(Metric, { value: '11', label: t('metric.mcp'), hint: `0 ${t('metric.mcpHint')}` }),
            ),
            h(
              Metrics,
              null,
              h(Metric, { value: '1,234 / 5,678', label: t('jig.longValue'), hint: t('jig.longHint') }),
              h(Metric, { value: '0', label: t('jig.zeroValue') }),
              h(Metric, { value: '3 errors', label: t('jig.errorValue'), tone: 'error' }),
            ),
          ),
          h(
            Section,
            { title: t('jig.pills') },
            h(
              'div',
              { style: { display: 'flex', gap: 8, flexWrap: 'wrap' } },
              h(Pill, { tone: 'ok', dot: true, label: t('state.healthy') }),
              h(Pill, { tone: 'warn', dot: true, label: '2 warnings' }),
              h(Pill, { tone: 'error', dot: true, label: '1 error' }),
              h(Pill, { tone: 'idle', label: t('jig.idle') }),
            ),
          ),
          h(
            Section,
            { title: t('jig.buttons') },
            h(
              'div',
              { style: { display: 'flex', gap: 8, flexWrap: 'wrap' } },
              h(Button, { label: t('action.refresh'), onClick: () => {} }),
              h(Button, { label: t('action.checking'), busy: true }),
              h(Button, { label: t('jig.disabled'), disabled: true }),
            ),
          ),
          h(
            Section,
            { title: t('jig.rows'), note: t('jig.rowsNote') },
            h(List, { rows: sampleRows, empty: '' }),
          ),
          h(
            Section,
            { title: t('jig.banner') },
            h(Banner, null, t('jig.bannerText')),
            h('div', { style: { height: 8 } }),
            h(Banner, { tone: 'error' }, t('jig.bannerError')),
          ),
          h(
            Section,
            { title: t('jig.loading') },
            h(
              'div',
              { style: { display: 'flex', flexDirection: 'column', gap: 7, maxWidth: 260 } },
              h(Skeleton, { width: '70%' }),
              h(Skeleton, { width: '45%' }),
              h(Skeleton, { width: '58%' }),
            ),
          ),
          h('div', { style: { fontSize: 11, color: C.dim } }, t('jig.note')),
        )
      }

      return Jig
    }

    // --------------------------------------------------------------- locale

    const DICT = {
      en: {
        'tab.label': 'Setup',
        'title': 'Agentic setup',
        'action.refresh': 'Refresh',
        'action.checking': 'Checking…',
        'state.healthy': 'Healthy',
        'state.loading': 'Checking the setup…',
        'state.error': 'Could not read the setup from the Host.',
        'metric.skills': 'Skills',
        'metric.skillsHint': 'installed / declared',
        'metric.profiles': 'Profiles',
        'metric.profilesHint': 'files',
        'metric.links': 'Client links',
        'metric.linksHint': 'present',
        'metric.mcp': 'MCP servers',
        'metric.mcpHint': 'skipped',
        'section.issues': 'Findings',
        'section.issuesNone': 'Nothing out of sync.',
        'section.skills': 'Skill manifest',
        'section.skillsNote': 'declared in skills.txt',
        'section.profiles': 'Profiles',
        'section.profilesNote': 'profiles/*.json',
        'section.links': 'Client links',
        'section.linksNote': 'skills linked into each client',
        'section.mcp': 'MCP servers',
        'section.mcpNote': 'mcp/servers.json',
        'label.missing': 'missing',
        'label.extra': 'extra installed',
        'label.broken': 'broken',
        'label.skipped': 'skipped',
        'label.optional': 'optional',
        'label.templated': 'per-agent',
        'label.noExtends': 'no parent',
        'label.absent': 'not installed',
        'checked': 'Checked',
        'jig.tab.label': 'Jig',
        'jig.title': 'Design jig',
        'jig.intro': 'Adjust the primitives here, then open Setup to see them in place. The choice stays in this browser.',
        'jig.density': 'Density',
        'jig.density.comfortable': 'Comfortable',
        'jig.density.compact': 'Compact',
        'jig.radius': 'Corners',
        'jig.radius.soft': 'Soft',
        'jig.radius.medium': 'Medium',
        'jig.radius.round': 'Round',
        'jig.type': 'Type',
        'jig.type.small': 'Small',
        'jig.type.default': 'Default',
        'jig.type.large': 'Large',
        'jig.reset': 'Reset',
        'jig.metrics': 'Metrics',
        'jig.metricsNote': 'normal, long and zero values',
        'jig.longValue': 'Long value',
        'jig.longHint': 'thousands',
        'jig.zeroValue': 'Zero',
        'jig.errorValue': 'Error tone',
        'jig.pills': 'Status pills',
        'jig.idle': 'Idle',
        'jig.buttons': 'Buttons',
        'jig.disabled': 'Disabled',
        'jig.rows': 'Rows',
        'jig.rowsNote': 'long names truncate, values stay right',
        'jig.banner': 'Banners',
        'jig.bannerText': 'This is an informational banner. It carries a sentence that needs reading.',
        'jig.bannerError': 'This is an error banner. The Host refused the request.',
        'jig.loading': 'Loading',
        'jig.note': 'These are the same primitives the Setup tab renders.',
      },
    }

    return {
      inject: ['slots', 'locale'],
      apply(ctx) {
        ctx.effect(
          () => ctx.locale.register(NS, { en: DICT.en }),
          'maybe-agentic-setup: dictionaries',
        )
        const t = ctx.locale.bind(NS)

        ctx.slots.inject('settings.plugins.tab', () =>
          ctx.slots.register(
            {
              name: 'settings.plugins.tab',
              id: 'maybe-agentic',
              order: 50,
              locale: NS,
              label: () => t('tab.label'),
            },
            makePanel(t),
          ),
        )

        ctx.slots.inject('settings.plugins.tab', () =>
          ctx.slots.register(
            {
              name: 'settings.plugins.tab',
              id: 'maybe-agentic-jig',
              order: 51,
              locale: NS,
              label: () => t('jig.tab.label'),
            },
            makeJig(t),
          ),
        )
      },
    }
  },
})
