---
title: "Auto mode is a sensor too"
date: 2026-05-17T20:00:00+02:00
draft: false
tags: ["agentic-ai", "security", "claude-code", "prompt-injection", "developer-tooling"]
keywords: ["Claude Code auto mode", "dangerously-skip-permissions", "prompt injection developer", "agentic IDE security", "AI coding assistant attack", "MCP supply chain"]
description: "Claude Code's auto mode replaces a manual flag with a classifier that decides which tool calls are safe. That is useful. It is not a security boundary, for the same reason input-side prompt-injection detection is not."
summary: "The third time this year I have written down the same epistemic mistake. Auto-accept loops in agentic IDEs trust a classifier to be a control. Real bypasses already exist. The sufficiently motivated attacker problem is now sitting on your laptop, deciding which files to edit while you make coffee."
canonicalURL: "https://hupfauer.one/posts/auto-mode-is-a-sensor-too/"
cover:
  image: "/covers/auto-mode-is-a-sensor-too.jpg"
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

**3. Overprivileged runtime — the part auto mode does not fix.** Malicious skills, compromised MCP servers, and packages that load instructions into context. Snyk's *ToxicSkills* survey reported prompt injection in roughly a third of the agent skills it sampled (sample-dependent, but directionally consistent with other supply-chain studies); coordinated campaigns have distributed malicious skills through community hubs. Anything the agent loads into context becomes an instruction channel by default; some systems preserve data/instruction separation more carefully than others, but in the typical case the boundary is thin. A classifier reviewing actions cannot retroactively un-load the prompt that shaped them.

Categories 1 and 2 are arms races at the input layer — patched monthly, reappearing monthly, the defender can keep running. Category 3 is a different kind of race: supply-chain and provenance work that runs in parallel and never quite finishes. What it is not is something the auto-mode classifier can decide. Ambient authority granted at install time is not revoked by inspecting the tool call later.

## Who bears the cognitive load

The honest read of auto mode is about cognitive load. The original design — permission prompt for every action — put the load on the human, predictably produced alert fatigue, and trained developers to click yes. Auto mode shifts the load: the model bears it on the easy cases, the human is summoned only for the hard ones. As a UX improvement that is genuine. As a security claim it depends on a property that is hard to establish — that "the hard cases" the human will be summoned for include the irreversible ones, reliably, under adversarial input.

That property is the one the bypasses above keep falsifying. So the more useful framing is not about motive but about a predictable consequence: when the model bears the routine cognitive load on tool calls, the human stops developing a calibrated sense of what the agent is doing. The trust gradient that used to come from clicking yes a hundred times — and occasionally clicking no — flattens out. The first irreversible action a developer actually has to evaluate, they evaluate cold.

Worth saying explicitly as an intuition pump, not as evidence: a reasonably competent, non-malicious employee does not `terraform destroy` the production tenant because a chatbot suggested it. They hesitate, check the subscription, ask a colleague. An agent in auto mode hesitates less than a human and acts faster than the human can read the proposal. The relevant property is not whose headline error rate is higher. It is that the human's failure mode includes friction — second-guessing, asking around, the small delays that catch the obviously-wrong action on the way out — and the agent's does not. Auto mode optimizes those frictions away on the routine path, which is exactly the path the adversarial input was crafted to ride.

The uncomfortable shape of the problem: the only honest solutions to "agent with standing privilege taking irreversible actions on adversarial input" are (a) genuinely shrink the agent's standing privilege so the dangerous actions become structurally unavailable, or (b) genuinely review the irreversible ones. Auto mode does neither. Each individual design decision in it is reasonable. Together they shift load away from the human in exactly the place where the human's slowness was the feature.

## Where this lands in the trilogy

The agent runs with your shell, your repo, your dependencies, your secrets, your CI tokens, and a license to type. Other layers exist in principle — OS permissions, repo ACLs, container boundaries, network egress policy, cloud IAM, enterprise EDR — and on a hardened setup they are meaningful. In the default developer workflow they are typically configured at coarser granularity than a single agent action: a credential that exists at all is a credential the agent can use. The policy engine is the gate that actually decides per-action; the layers around it decide what the agent *could* do in principle, not what it does this turn.

Different environments give you different amounts of leverage. Roughly:

| Environment | Enforceable controls | Where auto mode actually fits |
|---|---|---|
| Local laptop | Container, ephemeral working dir, opt-in egress, non-user UID | Convenience layer inside the sandbox |
| CI / repo agent | Short-lived OIDC tokens, branch protections, secret scoping | Should not exist for irreversible actions on `main` |
| Remote dev container | Same as local + tighter network policy, no host credentials | Reasonable default for routine edits |
| Plugin / skill / MCP | Per-source provenance, capability-style permissions, no implicit secret access | Auto mode does not address this layer at all |

A concrete minimum for a local setup that actually constrains the agent rather than relying on the classifier: run the agent in a container under a non-user UID, with the working tree mounted, the host home directory not mounted, network egress allowlisted, and any cloud credential delivered through a per-task short-lived token rather than a long-lived file. That is the shape of "the call fails before the classifier matters" — and it is unglamorous enough that almost no one ships it by default.

This is not an argument against auto mode. Auto mode is genuinely useful, and the manual-permission-prompt loop has its own failure mode — alert fatigue produces exactly the same "click yes to everything" outcome with worse UX. The argument is that auto mode is a *sensor and a convenience*, not a control, and treating it as a control is the same mistake the industry already made with input-side detection and the same mistake defenders are about to make with defensive prompt injection.

The controls that hold up are unglamorous and run in the same direction the trilogy has been pointing all along:

- **Scope the agent's identity, not its behavior.** Run the agent under a credential that cannot read `~/.aws/credentials`, cannot push to `main`, cannot publish packages, cannot exfiltrate to non-allowlisted destinations. If the model proposes the bad action, the call fails before the classifier matters.
- **Sandbox the blast radius.** The minimum architecture from above — container, non-user UID, no host home, allowlisted egress, per-task short-lived credentials. The classifier becomes a useful early-warning sensor inside that sandbox; outside it, an apology in advance.
- **Keep the human in the loop on irreversible actions specifically.** Auto mode is fine for "edit this file" and "run this test." It is not fine for `git push --force`, `aws s3 rm`, `npm publish`, `gh secret set`, or anything that touches a system you cannot reset. The right granularity is by-blast-radius, not by-classifier-confidence.

The bumper sticker, for the third time: *the model can refuse the bad action, or fail to. Identity, scope, and sandbox decide whether the refusal matters.* Auto mode does not change that. It just makes it cheaper to forget.
