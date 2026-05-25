---
title: "The registry is the control plane"
date: 2026-05-25T12:00:00+02:00
draft: false
tags: ["agentic-ai", "security", "governance", "windows-11", "skills", "supply-chain"]
keywords: ["agent skills governance", "npx skills", "Vercel agent skills", "Windows 11 On-Device Registry", "ODR", "Agent Launchers", "Agent Workspace", "skill bill of materials", "Skill-BOM", "MCP gateway", "CaMeL", "JFrog MCP Registry", "CycloneDX ML-BOM", "tool ordering policy"]
description: "Skills became a distribution format. That makes the registry a natural attachment point for the controls that already exist for every other package format — signing, manifests, allowlists — and the place where capabilities acquire identities operators can govern."
summary: "When npx skills add ships an agent capability the same way npm install ships a library, a large part of governance stops looking novel and starts looking like supply chain. The muscle to handle this exists. The OS just started cooperating. The missing pieces are a real capability manifest and stateful execution policy — and someone needs to ship them."
canonicalURL: "https://hupfauer.one/posts/the-registry-is-the-control-plane/"
cover:
  image: "the-registry-is-the-control-plane.jpg"
  alt: "Stacked horizontal shelves in off-white with one rust-colored shelf offset out of line"
  hidden: false
  relative: false
---

The previous three posts on this site argued that probabilistic recognizers — input-side prompt-injection detection, defensive prompt injection, the auto-mode classifier — are sensors, not controls, and that identity scoping, sandboxing, and human-in-the-loop on irreversible actions are the actual controls. This post is the same argument one layer up. The capability surface itself just became distributable, which changes where the controls have a place to bind.

## The npx moment

In the last few months, "skills" went from a Claude Code convention to a plausible distribution format. Anthropic's SKILL.md — a folder with a markdown file, optional scripts, progressive disclosure on activation — got pulled out into an open spec at [agentskills.io](https://agentskills.io/specification) with early support across roughly 30 runtimes at varying fidelity, from native handling in Claude Code, Cursor, and the Gemini CLI down to community adapters. Vercel Labs published [`npx skills`](https://github.com/vercel-labs/skills), a package-manager-shaped CLI that reads GitHub repos as a registry and writes SKILL.md files into the agent's config directory. JFrog [shipped MCP Registry](https://jfrog.com/ai-catalog/mcp-registry/) inside its AI Catalog. The shape is suddenly familiar: agent capabilities are named, installable, versioned artifacts.

A note on taxonomy before going further, because the next few sections need it. I will use "skill" loosely to mean any installable agent capability — a SKILL.md package, an MCP server, a runtime-specific plugin, an OS-registered agent action. They are not the same thing. SKILL.md is mostly instruction plus optional scripts; MCP servers expose callable tools over a protocol; Windows On-Device Registry holds agent action manifests. The supply-chain argument applies to all of them precisely because they have collapsed into the same operational category: named, installable, redistributable capabilities. Where the differences matter — and they will — I will say which one.

When a capability becomes a published artifact, a large part of agent governance stops looking novel and starts looking like software supply chain. Not all of it. Model behavior still determines when a skill fires and how its parameters are formed, which is the entire reason ordering and runtime policy matter later in this post. But the *control surface* becomes much more familiar, and every muscle the industry built for npm, Maven, PyPI, and container registries becomes applicable — along with every failure mode.

## Skills are dependencies. Treat them like dependencies.

If a skill is a dependency, the first question a security-literate org asks is: where does it come from, who else can change it, and what does the artifact actually claim to do. The current answer is mostly: a GitHub repo, pinned to a commit SHA if you are lucky, auto-updating from `main` if you are not. Anthropic's own documentation is admirably blunt — plugins and marketplaces are "highly trusted components that can execute arbitrary code on your machine with your user privileges" and the platform "cannot verify that they work as intended." Translated: trust is a property of the source, not the artifact. That is the posture mainstream package ecosystems sat in before lockfiles, before signed provenance, before anyone took attestation seriously. Skills are running through that same arc compressed into a year.

The unglamorous fix is well understood. Orgs run a private registry that proxies the public one, mirrors only what passes policy, attaches a signature, and locks down which sources users can add. JFrog is early in treating MCP servers and adjacent artifacts as governable rather than as URLs; other registry vendors have the same buyer problem in front of them and will likely test the same market. Claude Code's managed-settings layer already exposes the consumer-side primitives: `extraKnownMarketplaces` lets admins push a private marketplace, `enabledPlugins` constrains what can be active, and `disableSkillShellExecution` blocks the dynamic-context-injection feature that lets a skill execute shell at activation. The plumbing exists. Cryptographic signing of the artifact does not, on any mainstream skill runtime. Until it does, the private registry is a name resolver, not a trust boundary.

## Skill-BOM is not AI-BOM

The instinct here is to reach for an existing standard. The relevant ones — CycloneDX [ML-BOM](https://cyclonedx.org/capabilities/mlbom/) and the SPDX 3.0 AI profile — describe the model artifact and its training lineage. They have fields for energy consumption, hyperparameters, training data, evaluation, fairness. They do not have first-class fields for what a runtime agent capability is actually allowed to do. Existing AI-BOM work, including the CISA tiger team output and the OWASP AI BOM Guide, centers on models, datasets, software components, and system documentation; it does not give operators a standard, enforceable manifest of agent capability permissions. EU AI Act Annex IV will increase the *documentation* pressure on high-risk systems substantially, but it does not mandate a machine-readable runtime permission manifest, and pretending it does by year-end weakens the actual argument.

The actual argument is that a useful capability manifest answers a different question than SBOM or AI-BOM. SBOM answers what is inside. AI-BOM answers what it was trained on. The agent layer needs to answer: *what is this capability allowed to do at runtime, under whose identity, with what reversibility, and what does it bring along transitively*. The minimum surface is concrete enough to write down:

```yaml
skill:
  name: vendor.salesforce-export
  version: 1.4.2
  digest: sha256:7b4f...
  signedBy: cosign:acme-security
  testedAgainst:
    - anthropic/claude-sonnet-4.6
  runtime:
    host: claude-code
    minVersion: 1.2.0
  tools:
    - name: salesforce.query
      paramsSchema: schemas/sf-query.json
      reads: [salesforce.account/*]
      writes: []
      egress: []
    - name: csv.write
      writes: [workspace:/exports/*.csv]
  identity:
    mode: delegated-oauth
    provider: salesforce
    scopes: [read:accounts]
  hitl:
    requiredFor: [external_egress, destructive_write]
  ordering:
    deny: [web.fetch]
    afterReads: [classification:confidential]
  activation:
    triggers: ["export accounts", "salesforce csv"]
  composition:
    skills: []
    mcpServers:
      - name: salesforce-mcp
        version: 0.9.1
        digest: sha256:c1a3...
```

None of those fields are exotic. Several runtimes already carry pieces — SKILL.md frontmatter has `allowed-tools`, MCP server manifests declare prompts/resources/tools, Anthropic's managed settings express plugin allowlists. The point is that they are scattered, none is enforceable across hosts, and none of them captures the transitive composition graph that matters most. Skills do not generally call other skills directly, but they regularly invoke MCP servers, which call other tools, which call APIs that the host has authority over. Public specs rarely model that second-hop egress, which is exactly where the interesting failures happen.

A pragmatic implementation does not have to be a new standard. A CycloneDX profile or SPDX extension for agent capabilities would do most of the job. The schema is what matters: runtime permissions, identity delegation, the tool graph, egress, reversibility, ordering constraints, transitive servers, and the host runtime the skill was validated against. The other thing that matters is what reads the manifest. A registry manifest is not a control by itself. If the host runtime can silently ignore the declared tool set, identity mode, or egress list, the manifest is a nicer README. The control exists when registry metadata is bound to runtime enforcement and, where possible, to an OS-recognized identity. Which brings us to the runtime layer.

## Tiered execution is the missing control

Static allow/deny lists are the admission layer. They are necessary. They are also insufficient, because the interesting policies for agents are about how values *flow* through a session, not whether a tool is permitted in the abstract. Current MCP gateways — Portkey, MCP Manager, LiteLLM, the various security vendors — do tool-level RBAC, audit, payload scanning, and rate limiting well. Those are table stakes. They are not stateful in the way the next class of policy needs.

Concrete shape. An assistant has a web-search tool that reaches the public internet and a pull-internal-data tool that retrieves classified material from an internal store. The policy is straightforward to state: a tool that can leak data must not run after a tool that has put sensitive data into context. That is the actual control. The symmetric case is worth naming — untrusted public content reaching the model before a privileged internal query is an indirect prompt-injection path, and the same machinery handles it. Both rules are ordering rules expressed over data-sensitivity classes rather than over tool names. Value provenance is the mechanism that makes the ordering enforceable across a session, not a replacement for the ordering frame.

The minimal mechanism is taint tracking at the tool-result level. Every tool response carries a label set — `{source: internal, class: confidential, egress: blocked}` — and downstream tool invocations are checked against the accumulated context state. The policy is not "deny web-search." It is "deny any network egress tool after the context contains values labeled `class: confidential`, unless a human approves a redaction step." Symmetrically: "values derived from untrusted web content cannot drive privileged internal queries without mediation." Labels come from the Skill-BOM declarations, from gateway-side DLP classifiers, or from explicit declassification points an operator defines. The state is per session, with the option to scope tighter for short-lived plans.

This is Bell-LaPadula-adjacent, not Bell-LaPadula verbatim. It is closer to information-flow control with explicit declassification, which has decades of formal work behind it. DeepMind's [CaMeL](https://arxiv.org/pdf/2503.18813) is the closest recent published work for LLMs specifically: a privileged planner emits restricted Python, a quarantined reader handles untrusted data, and capability metadata is attached to every value flowing through the system. In the authors' evaluation on the AgentDojo benchmark, it reduces successful prompt-injection attacks substantially at roughly two to three times the token overhead, with results varying by workload. The numbers matter less than the architecture: separate privilege domains, tainted values, capability metadata enforced by the runtime. That is the shape of the next product. RBAC and rate limits at the tool boundary are not the differentiator. Whoever ships stateful value-provenance policy across a session, hooked to the manifests above, is selling something different.

## The OS finally cares

The piece that genuinely changes the equation is that the operating system started cooperating. Microsoft's [Agent Launchers framework](https://learn.microsoft.com/en-us/windows/ai/agent-launchers/) on Windows 11 — currently preview, surfaced via the Windows Experimental Agentic Features toggle — sits on top of App Actions and an [On-Device Registry](https://learn.microsoft.com/en-us/windows/ai/agent-launchers/agents-get-started). The `odr.exe` CLI manages registrations; the manifest declares the agent's name, action ID, package identity, and icon. Dynamic registration via `agent-info add` is gated on MSIX package identity — unpackaged tools cannot register directly, which is a constraint, not a virtue, but it does mean any registered agent on a Win11 machine has an OS-recognized identity to attach policy to.

Above that sits the contained agent session — Microsoft's developer docs call it that; the user-facing name, per the [Experimental agentic features](https://support.microsoft.com/en-us/windows/experimental-agentic-features-a25ede8a-e4c2-4841-85a8-44839191dfb3) support page, is Agent Workspace. It is not a Hyper-V VM; Microsoft positions the isolation as comparable to Windows Sandbox but lighter-weight, implemented as a separate Windows session under a dedicated low-privilege agent account with its own files and its own registry hive. The guarantees are the boring kind: separate token, separate ACLs, no default access to the user's profile, settings, credentials, or running app windows; network egress open by default; file access scoped by default to the six known folders — Documents, Downloads, Desktop, Music, Pictures, Videos — and only when the host app's MSIX declares the capability and the user consents at prompt time. Per-agent permission levels (Allow Always / Ask every time / Never allow) landed in build 26100.7344. The feature is off by default, admin-only to enable, and applies device-wide once on. Intune sits on top, with admin-controls documentation still partial in preview.

The consequence worth pulling out explicitly is that OS-level authorization finally detaches from application-level authorization. On a developer laptop today, Claude Code, Cursor, or any agent host runs inside the user's interactive session under the user's token. When the agent triggers anything that needs elevation, the UAC prompt the user dismisses is against the host application — which is also the trust boundary the user crossed when they first launched it. Application-side guardrails ("ask before running shell," "confirm destructive actions") and OS-side authorization collapse into the same plane. Agent Workspace breaks that by making the agent its own non-admin principal: any elevation request is arbitrated by Windows against the agent's standard token, not the host's, and the host cannot self-elevate the agent past UAC. The application keeps its own approval prompts for its own reasons, but they stop being the only thing standing between a prompt-injected agent and the user's admin authority. The OS sees the agent as someone else, which is the entire point.

What is new here is not OS identity in general. Windows has had app identity, package identity, app containers, and brokered capabilities for years. What is new is that Microsoft is surfacing those primitives explicitly for local AI agents, wiring them into admin tooling, and giving orgs a per-agent principal — separate from the user — that managed policy can target. That is the missing primitive that lets a private registry's signed manifest and a runtime gateway's value-provenance policy actually attach to something on the laptop. It is not equivalent to an AD service principal, and the analogy will mislead if pushed too hard. It is similar in the one respect that matters: policy can bind to a named principal instead of a pile of files.

There are two footguns worth naming. The first is that file-access consent on Win11 is granted *per host app*, not *per skill or per server*. Once you grant File access to host X, every server X uses inherits it. Mitigation: run one host per trust domain on managed endpoints, and treat the host as the policy boundary, not the skill. The second is the "Reduce protections for agent connectors" toggle, which exists explicitly to allow unpackaged servers to bypass containment. Lock it via Intune on managed devices, and refuse unpackaged servers in the registry. Both are places where a real boundary degrades into ambient authority, which is the failure pattern the earlier posts kept hitting: when identity and isolation disappear, you are left hoping a recognizer notices the bad thing in time.

## What to build, what to demand

The pattern is short, and I will resist the urge to dress it up.

If you are an org, the sequence is: centralize acquisition through a private registry, even if it starts as a thin proxy in front of GitHub; pin by digest, not by branch; block auto-update from mutable refs; require signatures for internal artifacts now and for external ones the moment the ecosystem supports verification; bind registry metadata to runtime allowlists rather than treating the manifest as documentation; enforce per-agent OS identity where the platform supports it; require human approval for irreversible writes and external sends; and disable unpackaged or bypass modes on managed endpoints. Fail closed on unsigned artifacts in CI, not only at install time. Break-glass paths require human approval plus session recording. A concrete starting point on the CLI side: I opened [vercel-labs/skills#1254](https://github.com/vercel-labs/skills/pull/1254), an RFC plus implementation that defaults `.well-known` resolution to deny, adds an admin-managed `skills-policy.json` with per-provider rules and an internal mirror-only mode, and writes a machine-readable inventory manifest at a stable path for fleet tooling to read.

If you are building governance products, the open ground is stateful value-provenance policy across a session. Tool-level RBAC, rate limits, audit, and payload scanning are commodities. Track value labels across calls. Support "no egress after sensitive read" and "untrusted content cannot drive privileged query" as first-class rules. Make declassification explicit and auditable. Hook the policy to the manifest, so the registry and the runtime are arguing about the same artifact.

If you publish skills, sign your releases, publish digests, declare your tools and scripts and egress and writable destinations and identity scopes, state the runtimes and models you have tested against, list the transitive MCP servers you call, and avoid requiring ambient user authority where a delegated identity will do. Some of this is annoying. Some of it will expose that the skill is doing too much. Good.

The trilogy on this site argued that identity is the control plane for agents. That argument has not changed. The registry is not a competing answer; it is where capabilities acquire identities operators can govern. It is the natural attachment point for signatures, manifests, ordering policy, runtime allowlists, and OS principals. It only becomes a control plane when those bindings are real — when signing is enforced, when runtimes honor the manifest, when the OS recognizes the principal, when gateways track provenance. Right now the industry has maybe half of that stack. The only choice is whether to assemble the other half before the incidents arrive or after.
