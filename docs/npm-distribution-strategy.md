# Kei-Agents npm Distribution Strategy

**Status:** Proposal — not approved, nothing implemented
**Scope:** Publishing a JavaScript/TypeScript consumable of `kei-agents` to the npm registry
**Audience:** Kei-Agents maintainers (see [CONTRIBUTORS](../CONTRIBUTORS))

## Summary

`kei-agents` is a Python package. There is no JavaScript or TypeScript in this
repository today, so "publish to npm" is not a packaging change — it is a
decision to take on a second language runtime, a second release pipeline, and a
second set of consumers whose bug reports land on this repo.

This document exists so that decision is made deliberately. It records the
prerequisite question first, then everything that must be settled before a
single `npm publish` runs.

**Recommendation: publish a schema-only package (Option B below), or defer.**
Do not port the Python behavior to TypeScript.

## 1. Prerequisite decision: what is the JS/TS package?

**This is the blocking question. Nothing else in this document matters until it
is answered, and the answer changes every later section.**

The current public surface splits cleanly into two halves, and only one of them
can cross a language boundary.

**Portable (declarative).** `ToolDefinition` and `ToolParameter` are plain
dataclasses. `render_openai_tools`, `render_anthropic_tools`, and
`render_ollama_tools` are pure functions from those dataclasses to JSON dicts —
`render_ollama_tools` is literally a call through to the OpenAI renderer.
`ModelFormat`, `Permission`, and `ToolCategory` are string enums.
`detect_model_format` maps a model name to a format. None of this touches the
network, the filesystem, or Python-specific runtime behavior. It is data and a
few total functions over that data.

**Not portable (behavioral).** `ToolDefinition.handler` holds a Python callable
— it has no meaning in JavaScript. `PolicyEngine` and the `check_tool_access` /
`filter_accessible_tools` helpers are the enforcement path for permissions.
`CRMAdapter` and `MockGitHubAdapter` are stateful, and the CRM tools keep a
module-global adapter singleton (`_crm_adapter_instance`, with `set_crm_adapter`
and `reset_crm_adapter` for tests). Reimplementing this half means maintaining
two independent implementations of an access-control decision.

Given that split, there are four honest options.

### Option A — Do not publish to npm

Consumers call Kei through a service boundary instead. Zero new surface, zero
new pipeline, zero drift.

Choose this if no concrete JS consumer exists yet. "It might be useful someday"
is not sufficient justification for a permanent second release channel.

### Option B — Schema-only package (recommended, if we publish)

Publish the declarative half only: the tool definitions as JSON, the enums, and
the three renderers. No handlers, no adapters, no policy engine.

- The Python package stays the single source of truth.
- A build step exports `TOOL_DEFINITIONS` to JSON; the npm package ships that
  JSON plus thin typed accessors.
- The renderers are ~30 lines each and pure, so a TS reimplementation is
  tractable and testable against Python-generated golden fixtures.
- **The permission model ships as metadata, not as enforcement.** Each tool
  keeps its `permission` field so a JS consumer can display or route on it, but
  `PolicyEngine` does not cross over. This must be stated in the package README
  in plain language: *these strings describe required permissions; they do not
  enforce anything. Enforcement happens server-side.* Shipping a JS
  `check_tool_access` invites a caller to trust a client-side access-control
  decision, and creates a second implementation that can silently diverge from
  the Python one. That is a security-relevant divergence, not a maintenance
  inconvenience.

### Option C — Full behavioral port

Reimplement policy, CRM, and GitHub adapters in TypeScript.

Two implementations of authorization logic, kept in sync by hand, forever. Every
policy change becomes a two-repo, two-review, two-release change, and a missed
sync is a permission bug. **Not recommended.**

### Option D — Transpiled/bridged package

Ship Python-to-JS transpilation or a WASM-packaged interpreter.

Large artifacts, a difficult debugging story for consumers, and the Python
runtime becomes a hard dependency of a Node process. Poor fit for what is
essentially a schema library. **Not recommended.**

### Decision required

| Question | Owner | Blocks |
|---|---|---|
| Is there a named JS/TS consumer with a real use case? | Maintainers | Everything |
| Option A, B, C, or D? | Maintainers | Everything |
| If B: does the JS side ever need enforcement, or is metadata enough? | Maintainers | §2, §3 |
| Same repo or separate repo? | Maintainers | §8, §9 |

**Everything below assumes Option B.** Under A there is no work; under C or D
the artifact contract, the test matrix, and the risk register all change
materially and this document must be rewritten.

## 2. Artifact contract

What the tarball contains, and what consumers may rely on.

**Package name:** `@haikei/kei-agents-schemas`. Scoped, and named for what it is.
An unscoped `kei-agents` on npm would imply parity with the PyPI package and
invite bug reports about missing adapters. The name should not promise the
behavioral half.

**Contents:**

| Path | Purpose |
|---|---|
| `dist/index.js` | ESM entry |
| `dist/index.cjs` | CJS entry |
| `dist/index.d.ts` | Type declarations |
| `dist/tool-definitions.json` | Generated from Python `TOOL_DEFINITIONS` |
| `README.md` | Includes the enforcement disclaimer from §1 |
| `LICENSE` | MIT, matching the Python package |

**Exports:** dual ESM/CJS via conditional `exports`, with `types` first in each
condition. `dist/tool-definitions.json` is exported as a subpath so consumers can
import the raw data without the accessors.

**Public API (frozen at 1.0):**

- `TOOL_DEFINITIONS` — the tool array
- `ToolDefinition`, `ToolParameter` — types
- `ModelFormat`, `Permission`, `ToolCategory` — string union types plus const
  objects, mirroring the Python enum values exactly
- `renderTools`, `renderOpenAITools`, `renderAnthropicTools`, `renderOllamaTools`
- `detectModelFormat`, `getToolByName`, `getToolsByCategory`,
  `getToolsByPermission`, `getToolsForModel`

**Explicitly not exported:** anything touching `handler`, `PolicyEngine`,
`CRMAdapter`, `MockGitHubAdapter`, or adapter state.

**Runtime dependencies: zero.** A schema package with a dependency tree is a
supply-chain liability for every consumer. This is a hard constraint, not a
preference.

**Generation, not translation.** `dist/tool-definitions.json` is produced by a
script that imports the installed Python package and serializes
`TOOL_DEFINITIONS`, dropping `handler`. It is never hand-edited. The generator
runs in CI and the build fails if the committed JSON differs from freshly
generated output — that check is what actually prevents drift between the two
packages, and it is the single most important piece of automation in this
proposal.

## 3. Versioning and SemVer

The npm package version tracks the Python package version **exactly**: PyPI
`0.1.0` corresponds to npm `0.1.0`. One number to reason about, and a consumer
filing a bug names one version.

The cost is real and should be accepted knowingly: a Python-only release still
publishes an npm version whose JS content is byte-identical, and vice versa. The
alternative — independent version lines with a compatibility matrix — is worse
for a package this small.

**What SemVer means here**, given the artifact is mostly data:

- **Major** — removing or renaming a tool; removing or renaming a tool
  parameter; making an optional parameter required; removing an enum value;
  changing renderer output shape; removing an export.
- **Minor** — adding a tool; adding an optional parameter; adding an enum value;
  adding an export.
- **Patch** — description text, typo fixes, internal refactors, type-declaration
  fixes with no shape change.

Two cases that are easy to get wrong and must be treated as **major**:

- **Changing a tool's `permission` field.** A consumer routing on that value
  breaks silently, and the failure mode is an authorization surprise.
- **Adding a value to `Permission` or `ModelFormat` when a consumer switches
  exhaustively over it.** Additive at runtime, but a compile error under
  TypeScript's exhaustiveness checking. Treat enum additions as minor only if
  the union is documented as open; otherwise major.

Pre-1.0 (`0.x`), the package is explicitly unstable and the npm convention that
`^0.1.0` does not admit `0.2.0` applies. The 1.0 release is the point at which
the API in §2 is frozen; do not reach 1.0 until at least one real consumer has
integrated.

## 4. Node support

**Supported:** Node 20 LTS and Node 22 LTS. Declared as
`"engines": { "node": ">=20" }`.

Node 18 reached end-of-life in April 2025 and is excluded. The package is pure
data and pure functions with no runtime dependencies, so the practical floor is
just ESM plus `exports` support — Node 20 is a comfortable margin, and matching
active LTS keeps the CI matrix small.

**Policy:** drop a Node major from the matrix when it leaves Maintenance LTS. A
drop is a **major** version bump, since it can break a consumer's install.

**Module systems:** both ESM and CJS are supported per §2. TypeScript consumers
are supported at `moduleResolution: "node16"`/`"bundler"`; the declaration files
must resolve correctly under both, which is a common dual-package failure and is
covered by the tests in §5.

**Not supported (non-goals, stated so they are not assumed):** Deno, Bun,
browser bundles. The package will likely work in all three — it is dependency-free
data — but working is not the same as tested and supported.

## 5. npm tarball tests

The failure this section exists to prevent: a package whose source tests pass
and whose *published tarball* is broken. Every check below runs against
`npm pack` output, not the working tree.

**Pre-publish, in CI, on the packed tarball:**

1. **Contents manifest.** `npm pack --dry-run` output is asserted against an
   expected file list. Fails on unexpected additions (stray source, test
   fixtures, `.env`, CI config) and on missing required files. Same intent as
   the existing `tests/test_packaging.py`, applied to the npm artifact.
2. **Install-and-import smoke tests.** Install the tarball into throwaway
   fixture projects — ESM, CJS, and TypeScript — and assert the documented
   exports import and execute. This catches broken `exports` maps, which unit
   tests structurally cannot.
3. **Node matrix.** Run those smoke tests on every supported Node major from §4.
4. **Type resolution.** Verify `.d.ts` resolves under `node16` and `bundler`
   module resolution, and that the package's own types typecheck in a consumer
   project.
5. **Cross-language golden fixtures.** The Python test suite serializes renderer
   output for a fixed set of tool definitions across all three formats; the JS
   suite asserts byte-identical output for the same inputs. **This is the check
   that makes Option B safe** — it is the mechanical guarantee that the two
   implementations have not diverged.
6. **Generated-JSON freshness.** Regenerate `tool-definitions.json` from the
   Python package and fail if it differs from the committed copy (§2).
7. **Zero-dependency assertion.** Fail if the manifest declares any runtime
   dependency.
8. **Size budget.** Fail if the tarball exceeds a set threshold. A schema
   package that suddenly grows is a signal something was included by accident.

**Post-publish:** install the published version from the registry in a clean
container and re-run the smoke tests. Registry propagation and publish-time
transforms have broken packages that passed every pre-publish check.

## 6. Provenance and supply-chain integrity

The Python pipeline already establishes the pattern to match: builds run on the
`kei-agents-runner` private runner, publishing is gated behind the `release`
GitHub environment, and workflow permissions are scoped per job.

**Requirements for npm publishing:**

- **Trusted publishing (OIDC), not long-lived tokens.** npm supports OIDC-based
  publishing from GitHub Actions, which removes the stored-credential problem
  entirely. Prefer it over an `NPM_TOKEN`.
- **If a token is unavoidable:** granular access token, scoped to this package
  only, stored as an environment secret on the `release` environment, with a
  documented rotation interval and a named rotation owner.
- **npm provenance attestations.** Publish with `--provenance` so the registry
  records the source commit and build workflow, and consumers can verify the
  tarball came from this repository.
- **Environment protection.** Publishing requires the `release` environment with
  required reviewers, matching the PyPI job.
- **Pinned actions.** Pin third-party actions by commit SHA in the npm workflow.
- **Publish only from tags.** No publishing from branch pushes or manual
  dispatch without a tag.
- **2FA on the npm org**, with publish rights restricted to CI automation rather
  than individual maintainer accounts.
- **`.npmignore` / `files` allowlist.** Use an explicit `files` allowlist in the
  manifest rather than a denylist. A denylist fails open — a new file is
  published unless someone remembers to exclude it. The manifest check in §5
  enforces this.

## 7. Rollback

npm's unpublish rules are restrictive by design: a version can be removed within
72 hours of publish, and after that only under narrow conditions. **Assume you
cannot unpublish.** Rollback is therefore roll-*forward* plus deprecation.

**Procedure for a bad release:**

1. **Deprecate** the bad version with a message pointing at the fix:
   `npm deprecate @haikei/kei-agents-schemas@<bad> "<reason>; use <good>"`.
   Consumers see this on install.
2. **Repoint `latest`** to the last known-good version with `npm dist-tag add`,
   so new installs stop picking up the bad release immediately. This is the
   fastest mitigation and should happen first if the fix is not ready.
3. **Publish a patch** with the fix. This, not unpublish, is the actual
   remediation path.
4. **Unpublish only** within the 72-hour window and only for a release that
   leaks a secret or is otherwise unsafe to leave available.
5. **Write up** what the pre-publish checks in §5 missed, and add the check.

**Additional requirements:**

- **A `next` dist-tag** for release candidates, so a risky change can be
  validated by a real consumer before `latest` moves.
- **Rollback must be rehearsed.** An untested rollback procedure is a document,
  not a capability. Exercise it once against the `next` tag before the first
  `latest` publish.
- **Yanking a PyPI release does not affect npm**, and vice versa. Because §3 ties
  the versions together, a bad shared version requires action in both registries;
  the release runbook must say so explicitly.

## 8. Ownership

An unowned publishing pipeline is how supply-chain incidents start.

| Responsibility | Owner |
|---|---|
| npm org and package ownership | Named maintainer + one backup, both with 2FA |
| Release approvals (`release` environment reviewers) | Existing Kei-Agents maintainers |
| Publish credential rotation | Named owner, documented interval |
| Cross-language parity fixtures (§5.5) | Whoever changes tool definitions |
| JS consumer issue triage | Named maintainer |

**Constraints:**

- **No single point of failure.** At least two people hold npm ownership. A
  package whose only owner is unavailable cannot be patched during an incident.
- **Contributor approval still applies.** Per [CONTRIBUTING.md](../CONTRIBUTING.md),
  contributors are approved by existing maintainers; that gate extends to anyone
  with npm publish rights.
- **A tool-definition change is now a two-artifact change.** Whoever edits
  `TOOL_DEFINITIONS` owns regenerating the JSON and keeping the parity fixtures
  green. This must be in CONTRIBUTING.md before the first publish, or it will be
  missed.
- **Security reports** follow [SECURITY.md](../SECURITY.md), which should be
  updated to name the npm package in scope.

## 9. Rollout

Each phase has an exit criterion. Do not begin a phase until the previous one
has met it.

**Phase 0 — Decision.** Resolve §1. Identify a named consumer. *Exit: written
decision recorded in this document.*

**Phase 1 — Prototype, unpublished.** Build the generator, the TS package, and
the parity fixtures. Validate with `npm pack` and local installs. *Exit: all §5
checks pass locally; parity fixtures green.*

**Phase 2 — Private validation.** Publish `0.x` under the `next` dist-tag. The
named consumer from Phase 0 integrates against it. *Exit: consumer confirms the
API is sufficient; rollback rehearsed per §7.*

**Phase 3 — Public `latest`.** Move `latest` to a `0.x` release. Announce as
unstable. Add the npm workflow to the release runbook. *Exit: two consecutive
releases with no manual intervention.*

**Phase 4 — 1.0.** Freeze the §2 API. *Exit: at least one production consumer
and a stable API across two releases.*

**Explicit stop condition:** if Phase 0 produces no named consumer, stop.
Publishing a package nobody has asked for creates permanent maintenance and
supply-chain obligations in exchange for nothing.

## 10. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| **Implementation drift** between Python and TS renderers | Silent wrong tool schemas sent to a model | Generated JSON + cross-language golden fixtures (§5.5, §2); CI-blocking |
| **Client-side permission enforcement** | A consumer trusts a JS access-control decision | Ship permissions as metadata only; explicit README disclaimer (§1) |
| **Version-lockstep friction** | Empty releases; pressure to decouple | Accepted cost (§3); revisit only with evidence |
| **Publish credential compromise** | Malicious version under our name | OIDC trusted publishing, provenance, environment gates, 2FA (§6) |
| **Name-squatting / typosquatting** | Users install a hostile lookalike | Scoped name; consider defensive registration of near-misses |
| **Unpublish restrictions surprise the team** | Slow incident response | Rehearsed deprecate + dist-tag rollback (§7) |
| **Maintainer bandwidth** | Stale package, unanswered JS issues | Named owners (§8); stop condition (§9) |
| **Dependency creep** | Supply-chain exposure for all consumers | Zero-dependency assertion in CI (§5.7) |
| **Scope creep toward Option C** | Duplicated authorization logic | Requires an explicit documented decision to change §1 |
| **Consumers expect PyPI parity** | Misleading; bad reports | Package name and README scope it as schemas only (§2) |

## 11. Go: separate binaries, not npm

Go is occasionally raised alongside npm. **Go must not be distributed through
npm.** They are unrelated problems with unrelated solutions, and conflating them
produces a worse answer to both.

**Go's distribution model is the module proxy.** `go install` and `go get`
resolve from the source repository via `proxy.golang.org`, with checksum
verification through `sum.golang.org`. There is no publish step and no registry
upload — the version tag in the repository *is* the release. Wrapping a Go
binary in an npm package discards that model and replaces it with a
`postinstall` script that downloads a platform-specific binary, which is exactly
the pattern security-conscious consumers disable and enterprise proxies block.

**If Kei ships Go components, distribute them as:**

- **Go modules** for library consumption, versioned by `vX.Y.Z` git tags, following
  Go's semantic import versioning (a `v2+` major requires a `/v2` module path
  suffix — a real constraint, distinct from the npm SemVer in §3).
- **Signed, platform-specific binaries** attached to GitHub Releases, with
  checksums and signatures, for CLI consumption. The existing build workflow
  already publishes release artifacts, so this extends a pattern the repo has.
- **Container images**, if the consumption model is a service rather than a CLI.

**A Go binary in an npm package would mean:** platform detection in
`postinstall`, a per-platform artifact matrix, binary download over the network
at install time, and every Go release becoming an npm release. It couples two
independent release cadences and adds an install-time network dependency to a
package tree that is otherwise pure data.

**Ownership note:** Go binary signing and release infrastructure is a separate
workstream from §8, with its own owner. It should not be folded into the npm
rollout in §9.

## Open questions

1. Is there a named JS/TS consumer? *(Blocks everything — §1, §9 Phase 0)*
2. Option A, B, C, or D? *(Blocks everything)*
3. Same repo or a separate repo for the JS package? *(§8, §9)*
4. Who are the two npm owners? *(§8)*
5. Is OIDC trusted publishing available for the npm org, or is a granular token
   required? *(§6)*
6. Does version lockstep (§3) hold, or does the team prefer independent lines
   with a compatibility matrix?
7. Are there Go components planned at all, or is §11 pre-emptive?
