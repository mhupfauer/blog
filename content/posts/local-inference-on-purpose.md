---
title: "Local inference, on purpose"
date: 2026-05-25T10:00:00+02:00
draft: false
tags: ["agentic-ai", "local-llm", "mlx", "claude-code", "opencode", "security"]
keywords: ["local LLM", "MLX", "Apple Silicon", "Claude Code offline", "OpenCode", "omlx", "Qwen3", "GLM-4.5", "ANTHROPIC_BASE_URL", "MacBook Pro M4 Max"]
description: "Why I run models on the laptop: not for cost, not as a hobby. Two operational reasons — offline work, and content that should never reach a vendor pipeline."
summary: "How I run omlx on an M4 Max MacBook Pro, point Claude Code at it via ANTHROPIC_BASE_URL when the network is gone, and switch to OpenCode entirely when the content is the threat model."
canonicalURL: "https://hupfauer.one/posts/local-inference-on-purpose/"
cover:
  image: "local-inference-on-purpose.jpg"
  alt: "Abstract laptop silhouette as a closed perimeter, with inference contained inside, on deep ink black"
  caption: ""
  relative: false
  hidden: false
---

I run models locally for two reasons: sometimes the network isn't there, and sometimes the content shouldn't be on someone else's pipeline. Neither reason is cost, sovereignty, or hobby. The setup below exists because those two conditions come up often enough that I stopped treating them as exceptions.

## The machine

A MacBook Pro 16", M4 Max, 128 GB unified memory. The 128 GB is the only spec that matters — it makes the choice between "fits and is fast" and "swap-thrashes into uselessness" a non-issue for the models I care about. Everything below assumes that headroom; on 36 GB you're picking different models, not running the same setup smaller.

## The server: omlx

`omlx` is a small MLX-based inference server published by `jundot` and installed from a tap:

```sh
brew tap jundot/omlx
brew install omlx
```

It speaks the OpenAI HTTP shape, binds `127.0.0.1:8000` by default, and — the reason I use it over alternatives — manages model residency itself. Point it at a directory of model subfolders and it loads and evicts them as requests come in. I reuse the LM Studio model directory rather than maintaining two copies:

```json
"model": { "model_dirs": ["/Users/markushupfauer/.lmstudio/models"] }
```

Running it as a brew service (`brew services start jundot/omlx/omlx`) gives me an always-on local endpoint. The auth key is generated into `~/.omlx/settings.json` on first run — the server rejects requests without it, which is the correct default for something binding a port, even on `127.0.0.1`.

## The model

The default is Unsloth's MLX 4-bit of **Qwen3.6-35B-A3B**. Small active-parameter count, fits comfortably in memory, fast enough that the agent loop isn't waiting on tokens. There are other models on disk — a GLM-4.5 variant, gpt-oss-120b, an abliterated Qwen for the rare cases where the standard alignment refuses tasks that make sense in an authorized engagement — but ninety percent of what I do hits the default. A bench of one tells you what's actually load-bearing.

## Claude Code, offline

Claude Code currently respects `ANTHROPIC_BASE_URL`. Point it at omlx and the client keeps working against a local model:

```sh
export ANTHROPIC_BASE_URL=http://127.0.0.1:8000
export ANTHROPIC_AUTH_TOKEN=omlx-...   # from ~/.omlx/settings.json
claude
```

omlx has a `claude_code` block in its settings (`mode: "local"`, `opus_model: "Qwen3.6-35B-A3B-UD-MLX-4bit"`) that handles the Anthropic-shape translation and routes the model name through. Context-window mismatches are real — a request shaped for 200k tokens does not actually fit in a 128k local context; omlx packs and truncates, you live with what that does to the long-tail prompts. For the kind of work this mode exists for, it's fine.

That work is bounded — I'm on a plane, on a train through a tunnel, or sitting on conference Wi-Fi where I'd rather not push large work prompts even over TLS just for the metadata — but it's a much wider band than the "local models are toys" framing suggests. For a lot of what an agent loop actually does — explain this stack trace, draft the next test, refactor this file, walk a codebase — Qwen3.6-35B-A3B at 4-bit lands close enough to Sonnet that the gap doesn't decide the task. It's not better. It is, more often than I expected when I set this up, good enough that the question becomes whether the marginal quality is worth the marginal exposure.

## OpenCode, when the content is the threat model

Offline is an availability problem. Sensitive content is a different problem and I treat it differently.

When the material genuinely should not leave the machine — a client artifact under NDA, a draft of something not ready to be on a vendor's logs, a half-formed thought I want to think through before any external system has a copy — I don't use Claude Code at all. Not even pointed at localhost. I switch to [OpenCode](https://opencode.ai).

Claude Code is an Anthropic client. Its job is to talk to Anthropic. `ANTHROPIC_BASE_URL` redirects the *destination*, but the binary, the update channel, the auth flow, the telemetry surfaces — those are all built around a relationship with a remote vendor. I'm choosing to trust an override flag against the grain of the entire product. That's fine for offline coding convenience. It is not what I want as the control when the threat model *is* the network.

OpenCode has no Anthropic-shaped client to redirect because it has no Anthropic-shaped client. It treats providers as configuration. omlx ships a launcher for it — `omlx launch opencode --model Qwen3.6-35B-A3B-UD-MLX-4bit` — that wires the local endpoint and key into the OpenCode config and starts it. The model is the same. The thing the binary is *trying* to do is different.

## The actual point

If the content itself is the risk, I want the control to be the absence of egress, not a vendor promise about what happens to it after egress. That's the entire argument. You can't classify your way out of "this should not have left the laptop" at runtime — it's a topology choice made before the request is constructed. The MacBook either has the weights or it doesn't. If it doesn't, no amount of careful prompting on the way out the door makes it not have left.

The cost is real but smaller than the cliché suggests: first-token latency on a cold model is seconds, the very hardest reasoning tasks still want the frontier model, and I lose the parts of the hosted experience that are genuinely good. The benefit is also real: for the broad middle of day-to-day work, the answer is close enough that being certain about where it came from is worth more than the marginal quality I'd get by sending it out.

Both modes — CC-over-omlx, and OpenCode-over-omlx — live behind the same brew service. The difference between them isn't a tuning knob. It's an answer to a different question.
