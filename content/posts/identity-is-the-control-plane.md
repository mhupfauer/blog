---
title: "Identity is the control plane. Detection is a sensor."
slug: "identity-is-the-control-plane"
date: 2026-05-17
draft: false
tags: ["agentic-ai", "identity", "security", "prompt-injection"]
keywords: ["agentic AI security", "non-human identity", "prompt injection", "OWASP LLM Top 10", "excessive agency", "AI authorization", "agent identity"]
description: "Prompt injection detection is a sensor on one input channel. Identity is the decision layer. Why the agentic AI security industry is optimizing the wrong control."
summary: "Detection asks 'is this input adversarial?' Identity asks 'what is this principal allowed to do, on whose behalf, right now?' The first is probabilistic and bypassable. The second is enforceable and auditable."
canonicalURL: "https://hupfauer.one/posts/identity-is-the-control-plane/"
cover:
  image: "identity-is-the-control-plane.jpg"
  alt: "Identity perimeter deflecting one vector, permitting a credentialed one"
  caption: ""
  relative: false
  hidden: false
---

Walking the vendor floor at RSAC this year, the count was roughly 40% prompt injection detection products, maybe 5% anything resembling agentic identity. That ratio is inverted from where the risk actually sits — and the gap is widening as agents move from demos into systems that do things on people's behalf.

Let me try to explain why I think most of the industry is optimizing the wrong control.

## The obvious part first

Prompt injection is real. It is not going away. Detection has its place — as a sensor, alongside other sensors, feeding a decision layer. I am not arguing against building detectors. I am arguing against the implicit claim, encoded in how budgets are being spent, that detection is the *decisive* control for agentic systems.

It is not. It cannot be. And the reason has nothing to do with how good any particular classifier gets.

## Reframe: injection only matters because of what comes next

A prompt injection is a string. By itself it does nothing. It matters only because some agent, after reading it, can *do something* — call a tool, move money, send an email, write to a database, escalate to another agent. The injection is the trigger. The blast radius is the vulnerability.

If the agent has no standing privilege, no long-lived credentials, no inherited scope from the user, and every tool call requires fresh authorization bound to a declared intent — the injection has nowhere to land. The attacker can convince the model of anything they like. The model still cannot do anything it was not authorized to do at that moment, for that task, on behalf of that principal.

This is not theoretical. It is the same shift we made twenty years ago when we stopped trying to filter SQL injection at the input layer and started using parameterized queries. The fix was not better detection. The fix was a principal model that made the dangerous thing structurally impossible.

## What each control actually answers

| Control | The question it answers |
|---|---|
| Prompt injection detection | "Is this input adversarial?" |
| Agentic identity | "What is this principal allowed to do, on whose behalf, right now?" |

The first is probabilistic and bypassable — any sufficiently determined attacker, given access to the model's outputs, will find a phrasing the classifier misses. The second is enforceable and auditable. They are not substitutes. Treating them as such — building elaborate detection pipelines on top of a broken principal model — is treating a symptom while the disease compounds.

The OWASP Top 10 for LLM Applications has been pointing in this direction for a while. *Excessive Agency* (LLM06) is, in plain reading, a principal-model problem: the application gave the LLM more functionality, permissions, or autonomy than the task required. It is the category that swallows most of the others — compromised tool use, rogue actions, cascading failures — they all reduce to: the agent had more power than the situation justified.

## You cannot filter your way out of an authorization problem

The framing I keep coming back to: you don't hand a temp worker your keycard and then install cameras to watch them. You give them a scoped badge that expires at 5pm. Detection is the cameras. Identity scoping is the badge.

The deeper point is about coverage. Detection is *per-vector* — a prompt injection detector catches prompt injections, with some false negative rate. It does nothing for model jailbreaks, supply chain compromise of a tool, a rogue agent in a multi-agent system, or the model simply being wrong in a way that produces a harmful action. Identity scoping is *per-principal* — it constrains what the agent can do regardless of how the compromise happened. One control, many threats.

If you only have budget for one of these — and most organizations effectively do, given attention is the scarce resource — the identity work has strictly broader coverage.

## What "agentic identity" means here, briefly

I am using it in the narrow, operational sense: an ephemeral, delegation-aware identity assigned to an autonomous AI agent, distinct from the user who initiated the task, with explicit scope bound to the task and short-lived credentials issued per invocation. The plumbing exists — token exchange, workload identity federation, OBO flows. What is missing is the will to treat the agent as a first-class principal rather than a function call running with the user's full privileges.

This post is not about *what* agentic identity is. It is about *why* it matters more than the thing the vendor floor is selling you.

## The punch

Detection is downstream of decision. Identity is the decision.

You can buy a better sensor every quarter and the underlying risk does not move, because the agent still has the standing privilege to act on whatever instruction the sensor missed. Or you can do the harder, less marketable work of fixing the principal model — and the sensors become what they were always supposed to be: useful telemetry on a system that is safe by construction.

I know which one I'd rather be defending in front of a board after the first real incident.
