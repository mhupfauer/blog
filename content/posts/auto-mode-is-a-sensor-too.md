---
title: "Auto mode is a sensor too"
date: 2026-05-18
draft: false
tags: ["agentic-ai", "security", "claude-code", "prompt-injection", "developer-tooling"]
keywords: ["Claude Code auto mode", "dangerously-skip-permissions", "prompt injection developer", "agentic IDE security", "AI coding assistant attack", "MCP supply chain"]
description: "Claude Code's auto mode replaces a manual flag with a classifier that decides which tool calls are safe. That is useful. It is not a security boundary, for the same reason input-side prompt-injection detection is not."
summary: "The third time this year I have written down the same epistemic mistake. Auto-accept loops in agentic IDEs trust a classifier to be a control. Real bypasses already exist. The sufficiently motivated attacker problem is now sitting on your laptop, deciding which files to edit while you make coffee."
canonicalURL: "https://hupfauer.one/posts/auto-mode-is-a-sensor-too/"
cover:
  image: "/covers/auto-mode-is-a-sensor-too.png"
  alt: "Automated gate opens for expected form while off-shape form slips past"
  hidden: false
  relative: false
---

In [the first post](/posts/identity-is-the-control-plane/) I argued that prompt-injection detection is a sensor on one input channel, and the real decisive control for agentic systems is identity scoping. In [the second](/posts/salting-your-own-well/) I argued the symmetric case — defensive prompt injection is also a sensor, useful as a tripwire, dangerous as a wall. This is the third instance of the same problem shape, now installed on every developer's laptop: the auto-accept loop in agentic coding tools, specifically Claude Code's auto mode and its cousins.

## The pitch

Auto mode is presented, fairly, as the responsible replacement for `--dangerously-skip-permissions`. The old flag suppressed every permission prompt unconditionally; the new mode keeps a model in the loop. Before each tool call, a dedicated safety classifier reviews the action. Safe actions execute without bothering the developer; risky ones are blocked or escalated; a session that accumulates three consecutive denials or twenty total stops and asks for a human. There is also a return-side check: when a subagent finishes, the classifier reviews its action history before the result is passed back to the orchestrator, on the assumption that a benign delegation could have been hijacked mid-run by injected content.

This is a real engineering improvement over the unconditional flag. The classifier catches some real harm. The denial counter catches some classes of stuck loops. None of that is the problem.

## The mistake

The pitch quietly upgrades a *heuristic policy engine* into a *security boundary*. To be fair to the implementation, that engine is more than a single classifier — it includes policy code, allow/deny lists, structured tool schemas, and (in some configurations) deterministic guards like path restrictions or command parsing, alongside the learned components. But the composition does not save it. The sharper claim is the one to argue: *a composed decision layer with learned components is not a reliable authorization boundary when the attacker controls part of the input*. The classifier and its surrounding scaffolding are good enough, often enough, that the developer stops watching. That is the entire feature. And the moment the developer stops watching, the system property "human reviews destructive actions" silently becomes "heuristic policy engine reviews destructive actions, then a model decides what to do next."

The published failures in agentic coding tools cluster into three categories. Auto mode partially addresses the first two and structurally cannot address the third:

**1. Prompt injection through legitimate content channels.** The attacker controls *some* inputs the agent will read — a PR title, a document body, a tool result — and the system collapses the boundary between data and instruction.

- A security researcher put a crafted instruction in a pull request title and the Claude Code Security Review GitHub Action posted a sensitive token to the PR; the same shape of attack reportedly worked against Gemini CLI Action and GitHub Copilot Agent in similar configurations. The exact secret leaked depends on which token the action was configured with — the lesson is not "Anthropic API key leaked" specifically but "agent running with whatever credential CI handed it does whatever the PR title says."
- Hidden text in a `.docx` (1-point, white-on-white, invisible to a human reader, parsed cleanly by the model) has been used to make a coding agent upload local files through an allowlisted API endpoint.

**2. Implementation bugs in the policy layer.** The decision engine has parser or threshold flaws an attacker can exploit. Notably, these do not always *bypass to silent execution* — sometimes they *degrade to prompt* instead, which is a subtler failure mode worth distinguishing.

- The 50-subcommand cap in Claude Code's bash permission analyzer. Past the limit, the agent fell back to *ask the user* rather than *deny*. Adversa demonstrated this with 50 no-ops followed by a `curl`; patched in v2.1.90. This is genuinely not a "classifier bypass to execution" — it is an attention attack on the human. Which still works, because asking a developer who turned on auto mode is asking the wrong person.

**3. Overprivileged runtime — the part auto mode does not fix.** Malicious skills, compromised MCP servers, and packages that load instructions into context. Snyk's *ToxicSkills* survey reported prompt injection in roughly a third of sampled agent skills; coordinated campaigns have distributed malicious skills through community hubs. Anything the agent loads into context is an instruction channel, and a classifier on actions cannot retroactively un-load it.

Each individual bypass in categories 1 and 2 gets patched. The next one appears the following month. This is what an arms race looks like at the input layer, and it is a race the defender can run indefinitely. Category 3 is not a race. It is the design choice to give the agent ambient authority that the classifier can only ever observe, never revoke.

## Where this lands in the trilogy

The agent now runs with your shell, your repo, your dependencies, your secrets, your CI tokens, and a license to type. There are other layers in principle — OS permissions, repo ACLs, container boundaries, network egress policy — but in the default developer workflow they are typically absent or too coarse to matter at the granularity of a single agent action. In practice, the policy engine is the only meaningful gate where, six months ago, your own attention used to stand.

The threat surfaces are not all the same, and the controls below apply differently to each:

- **Local developer laptop.** Identity scoping is hardest here because the agent inherits the developer's full credential context; sandboxing (containers, ephemeral homes, opt-in network) does most of the work.
- **CI / repo agent.** The classic overprivileged-runtime case — short-lived OIDC tokens with narrow scopes are both available and necessary.
- **Plugin / skill / MCP ecosystem.** Treat third-party agent extensions like browser extensions, not like libraries: they should run with the minimum context they need and should not see your secrets by default.

This is not an argument against auto mode. Auto mode is genuinely useful, and the manual-permission-prompt loop has its own failure mode — alert fatigue produces exactly the same "click yes to everything" outcome with worse UX. The argument is that auto mode is a *sensor and a convenience*, not a control, and treating it as a control is the same mistake the industry already made with input-side detection and the same mistake defenders are about to make with defensive prompt injection.

What the actual controls look like is unglamorous and goes in the same direction the trilogy has been pointing all along:

- **Scope the agent's identity, not the agent's behavior.** Run Claude Code under a credential that cannot read `~/.aws/credentials`, cannot push to `main`, cannot publish packages, cannot exfiltrate to non-allowlisted destinations. If the model proposes the bad action, the call fails before the classifier matters.
- **Sandbox the blast radius.** Containers, ephemeral working directories, networking off by default, file write scopes that exclude anything you have not opted into. The classifier becomes a useful early-warning sensor inside a sandbox; outside one, it is an apology in advance.
- **Keep the human in the loop on irreversible actions specifically.** Auto mode is fine for "edit this file" and "run this test." It is not fine for `git push --force`, `aws s3 rm`, `npm publish`, `gh secret set`, or anything that touches a system you cannot reset. The right granularity is by-blast-radius, not by-classifier-confidence.

The bumper sticker, for the third time: *the model can refuse the bad action, or fail to. Identity, scope, and sandbox decide whether the refusal matters.* Auto mode does not change that. It just makes it cheaper to forget.
