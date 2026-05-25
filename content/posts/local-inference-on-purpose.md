---
title: "Local inference, on purpose"
date: 2026-05-25T10:00:00+02:00
draft: false
tags: ["agentic-ai", "local-llm", "mlx", "claude-code", "opencode", "security"]
keywords: ["local LLM", "MLX", "Apple Silicon", "OpenCode", "omlx", "Qwen3", "GLM-4.7", "gpt-oss-120b", "ANTHROPIC_BASE_URL"]
description: "ANTHROPIC_BASE_URL redirects the model endpoint, not the rest of the client. 'Local' is a property of where the binary connects, not where one of its endpoints points."
summary: "Notes on actually running models locally on an M4 Max: omlx as the server, Qwen3.6-35B-A3B and GLM-4.7-Flash for agent work, gpt-oss-120b for writing. Why pointing Claude Code at localhost is fine for offline ergonomics and wrong as a perimeter."
canonicalURL: "https://hupfauer.one/posts/local-inference-on-purpose/"
cover:
  image: "local-inference-on-purpose.jpg"
  alt: "Abstract laptop silhouette as a closed perimeter, with inference contained inside, on deep ink black"
  caption: ""
  relative: false
  hidden: false
---

I run models locally when the network isn't there, and when the content can't leave the device. Not cost, not hobby. Those two cases come up often enough that they have a default path on this machine.

There is a genre of "run Claude Code with a local model" guide currently in rotation that goes: install some MLX server, export `ANTHROPIC_BASE_URL=http://127.0.0.1:…`, declare victory. The genre confuses endpoint substitution with local execution. "Local" is a property of where the binary connects, not of where one of its endpoints points — and the difference matters as soon as anyone makes a security argument out of the setup.

## The machine

MacBook Pro 16", M4 Max, 128 GB unified memory. The 128 GB is the spec that changes the model menu — it turns "doesn't fit" into "slow but usable" for things that would otherwise force a smaller choice. On 36 GB you are trading context, concurrency, or model size.

## The server: omlx

[omlx](https://github.com/jundot/omlx) is a small MLX-based inference server, installed via Homebrew tap:

```sh
brew tap jundot/omlx
brew install omlx
brew services start jundot/omlx/omlx
```

It speaks the OpenAI HTTP shape, binds `127.0.0.1:8000`, and — the reason I use it over alternatives — manages model residency itself. Point it at a directory of model subfolders and it loads and evicts them as requests come in. I reuse the LM Studio model folder rather than maintaining two copies:

```json
"model": { "model_dirs": ["/Users/markushupfauer/.lmstudio/models"] }
```

Running it as a brew service gives me an always-on local endpoint. Requiring an auth key on first run is a sane default even for a loopback listener.

## The models

For agent-loop work — read this file, run this test, refactor this function, walk this codebase — two MLX builds cover most of what I'd otherwise send to Sonnet. Qwen3.6-35B-A3B-UD-MLX-4bit (≈20.17 GB on disk) is my default: small active-parameter MoE, fast in the loop. GLM-4.7-Flash-MLX-6bit (≈22.68 GB) is the fallback when Qwen feels verbose or off-key on a particular task. In day-to-day codebase work both land close enough to Sonnet that model quality is rarely what decides the outcome. They are not better. They are good enough that the marginal quality I'd get by sending the prompt out is not obviously worth the marginal exposure.

For writing and synthesis, 128 GB is enough to run a 4-bit MLX build of gpt-oss-120b. Genuinely slow — you will notice every prompt — but it works, and for content that absolutely cannot leave the device, latency is the price of the perimeter.

## What `ANTHROPIC_BASE_URL` actually does

Claude Code respects an override for its API base URL:

```sh
export ANTHROPIC_BASE_URL=http://127.0.0.1:8000
export ANTHROPIC_AUTH_TOKEN=omlx-...   # from ~/.omlx/settings.json
claude
```

omlx ships a `claude_code` settings block (`mode: "local"`, `opus_model: "Qwen3.6-35B-A3B-UD-MLX-4bit"`) that handles the Anthropic-shape translation. Context-window mismatches are the visible cost: a request shaped for 200k tokens does not fit a 128k local context; omlx packs and truncates, and you accept that long diffs and large repository walks suffer the most.

That mode is genuinely useful — conference Wi-Fi where I'd rather not send account-linked prompts anywhere, planes, trains through tunnels. For a lot of what an agent loop actually does, Qwen3.6-35B-A3B at 4-bit closes most of the gap to Sonnet.

What the variable does not do is make Claude Code a local-only program. Claude Code is a vendor client. The model endpoint is one egress path; the binary still depends on vendor infrastructure for updates, auth, and parts of its feature surface, all of which sit behind their own endpoints. The honest test is not "does my model call hit localhost" but "what survives if the only outbound rule on this machine is loopback." Run that experiment on a strict default-deny egress and you find out quickly how much of the client still wants to talk to home. Most of the inference works. Other things — depending on which feature you exercise — do not.

This is fine if you set the variable for ergonomic reasons. It is not fine if you set it because the *content* should not leave the machine. Those are two different problems and the env var only buys you the first one, and only when you happen to be using the parts of the client that survive without the rest of the network.

## Actually local: a different client

If the threat model is "this code, prompt, or draft must not leave the laptop", switch clients. The binary needs to not have a vendor relationship to fall back on.

[OpenCode](https://opencode.ai) is the one I use. It treats the model backend as a backend; omlx ships a launcher (`omlx launch opencode --model Qwen3.6-35B-A3B-UD-MLX-4bit`) that wires the local endpoint and key into the config and starts it. The relevant property is testability: I can run the useful path with egress denied to everything but loopback, and notice the moment that stops being true.

There is also a stripped, de-Anthropic'd fork of Claude Code floating around. It exists, it works, and depending on jurisdiction it is a fairly direct invitation to find out how local copyright and reverse-engineering law treats minified vendor JavaScript. Decide accordingly.

## The actual point

If you want offline ergonomics, redirect the endpoint. If you want a perimeter, change the client. That choice happens before the prompt is constructed — you cannot classify your way out of "this should not have left the laptop" at runtime. The MacBook either has the weights and a client that knows only how to talk to them, or it doesn't.

The cost is real but smaller than the lazy version of this argument suggests: cold-start latency is seconds, the hardest reasoning tasks still benefit from a frontier model, and a few hosted features I genuinely like aren't there. The benefit is also real. For the broad middle of day-to-day work, being certain about where the answer came from is worth more than the quality I'd get by sending it out.

Both modes — CC-over-omlx and OpenCode-over-omlx — live behind the same brew service. The difference between them isn't a tuning knob. It's an answer to a different question.
