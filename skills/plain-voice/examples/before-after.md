# Before and after

Real comments and constructed examples rewritten in this voice. Facts unchanged. The examples about information order below are constructed.

## A security scanner reply on a merge request

**Before**

> Confirmed true positive. Fixed in a7f8300b: parents can no longer update an entry they do not own (404), the persisted owner is never overwritten on update, and the caller tenant must match the entry; the attachment guard keeps its own check as defence in depth. ITs added for the PUT hijack and the follow-up attachment access.

What is wrong with it: one 45-word sentence with a semicolon, "persisted owner" and "defence in depth" are jargon, and it never says what a person could do before the fix.

**After**

> Yes, this is real. Before the fix a parent could send an update with another family's application id and become its owner, which then let them see and delete that family's documents. Fixed in `a7f8300b`. A parent can now only update their own application, an update never changes the owner, and the caller's tenant has to match. The document check stays as a second line of defence. Tests cover the takeover and the document access after it.

## A ticket status comment

**Before**

> Bundle updated: `INT-9255` in both repos now also carries master (incl. INT-9257's admin delete permission) and everything from INT-9265 (convert JWT renewal, Parent/Guardian wording, AEN wording, recap PDF redesign, attachment scoping). Pipelines for these heads are running; the previous builds predate this merge. qa56-nspace31 needs a redeploy of both apps once the new builds publish.

**After**

> I've merged master and INT-9265 into the bundle, so it now has the convert fix, the Parent/Guardian wording, the new recap PDF and the document permission changes. The builds are running. The versions on nspace31 are from before this merge, so both apps need a redeploy once the new builds land. I'll post the versions here when they're ready.

## A review finding

**Before**

> The new helper mixes attachment transport, mutation hooks, JWT parsing, token renewal, and conversion error formatting. Bulk conversion utilities now import a React hook module for ordinary request functions. It also introduces a barrel import forbidden by the frontend's AGENTS.md.

**After**

> This file does too many jobs. It holds the upload and delete requests, the React hooks, the token expiry check and the error wording, so the bulk pages end up importing a hook file just to call a plain function. It also imports from the `@root/packages/api` barrel, which our frontend guide says not to do. Split it into a request file, a hook file and a small token helper, with direct imports.

## Information order: a request

**Before**

> The release is scheduled for Thursday. QA passed, and the migration takes about ten minutes. We need your approval by Wednesday noon to deploy.

**After**

> Please approve the deployment by Wednesday noon for Thursday's release. QA passed. The migration takes about ten minutes.

The request and deadline come first. The evidence follows.

## Information order: a status update

**Before**

> I merged the fix and ran the tests. The build then failed because the signing certificate expired. The release is blocked until we renew it.

**After**

> The release is blocked until we renew the expired signing certificate. The build failed. I merged the fix and ran the tests.

The blocker matters first. The work history supports it.

## Information order: a conditional recommendation

**Before**

> The queue change passed local tests. We have not checked it under production load. I think we can deploy if the load test passes.

**After**

> I think we can deploy if the load test passes. The queue change passed local tests. We have not checked it under production load.

The recommendation comes first. Its condition and uncertainty stay attached.

## What stayed the same in every rewrite

- Every fact, hash and status code.
- Every hedge. Nothing became more certain.
- The length is similar. The point is clarity, not compression.
