# 02 · Document carousel

Nine-slide PDF. Carousels still get top-tier reach on LinkedIn. PDF lives at `out/carousel/carousel.pdf` — upload it as the post's attached document.

Recommended slot: Tuesday week 2 ≈ 08:30 CET.

---

## English (post body)

> Three identity collapses, one bar.
>
> Worked the wiring across Entra OBO, on-prem Kerberos, low-code agent platforms, RAG ACLs, and the shop floor. Same property fails in every estate: the user, the agent, or the authorization gets dropped — usually quietly, at a hop nobody planned for.
>
> This is the short visual version. Full essay with interactive diagrams and the audio cuts in the comments.
>
> #AgenticAI #IdentityAccessManagement #Cybersecurity

**First comment:** https://hupfauer.one/posts/which-agent-bricked-prod/

---

## Deutsch (post body)

> Drei Identity-Collapses, eine Latte.
>
> Habe die Verkabelung quer durchgespielt — Entra OBO, On-Prem-Kerberos, Low-Code-Agent-Plattformen, RAG-ACLs, Werkshalle. Dieselbe Eigenschaft kippt in jedem Estate: User, Agent oder Autorisierung gehen verloren — meistens leise, bei einem Hop, den niemand geplant hat.
>
> Das ist die kurze visuelle Version. Volle Essay mit interaktiven Diagrammen und Audio-Cuts in den Kommentaren.
>
> #AgenticAI #IAM #Informationssicherheit

**Erster Kommentar:** https://hupfauer.one/posts/which-agent-bricked-prod/

---

## Slide spec

The PDF builder reads this section. Edit the slide text below, then run `python3 social/linkedin/build/build-carousel.py` to regenerate `out/carousel/carousel.pdf` and the nine PNG fallbacks.

### slide-01 · cover
TITLE: Which agent bricked prod?
SUBTITLE: A two-question test for enterprise agent identity
FOOTER: hupfauer.one

### slide-02 · the thesis
EYEBROW: The test
TITLE: Every hop must answer two questions.
BODY: Whose authority is being exercised. Which agent exercised it. Keep both and you have something you can authorize and audit. Lose either — most have — and your role model is a slide, not a control.

### slide-03 · collapse 1
EYEBROW: Collapse 1 of 3 · the user
TITLE: User disappears behind an app-only token.
BODY: A client-credentials hop in the middle of a user-initiated chain. The downstream API sees a service principal with broader rights than the human ever held. Audit table says "App did it." Person is gone.

### slide-04 · collapse 2
EYEBROW: Collapse 2 of 3 · the agent
TITLE: Agent disappears behind a shared platform identity.
BODY: Forty agents built by forty makers all show up at the resource as one client id. The audit table cannot distinguish agent A from agent B without correlating on platform-internal run IDs that were never propagated.

### slide-05 · collapse 3
EYEBROW: Collapse 3 of 3 · the authorization
TITLE: ACL disappears at the ingestion boundary.
BODY: Source-system permissions are a property of the system you copied data out of. They are not in the chunk. RAG retrieves flat. Bob can read through the bot things he could never open at source — and your compliance plane cannot enumerate the corpus.

### slide-06 · OT asymmetry
EYEBROW: Where this matters most
TITLE: A misrouted write to a Jira ticket is an email. A misrouted write to a setpoint moves actuators.
BODY: The AI-first roadmap reaches the shop floor on purpose — that is where the margin is made. The chain that issues the write was already missing the actor. Now it points at the part of the company that physically moves.

### slide-07 · A2A
EYEBROW: Why this hasn't blown up yet
TITLE: Living off the chatbot.
BODY: The only thing saving us is compartmentalisation — the agents do not talk to each other yet. The day they do, lateral movement is the published API and privilege escalation is whichever neighbour has the broader connector. No payload, no CVE — polite REST calls.

### slide-08 · the bricked-prod vignette
EYEBROW: What it looks like on a bad Tuesday
TITLE: An agent closes a change-freeze hold.
BODY: Alice asks the bot to tidy stale tickets. The maker's admin PAT bulk-closes across projects Alice can't see — including the hold on a forward-only migration. Pipeline cuts the build. Migration locks the orders table. Three and a half hours of downtime. Forensics from authoritative logs: impossible.

### slide-09 · the bar
EYEBROW: The bar for Part 1
TITLE: If your logs cannot prove who and which, you don't have agent auth.
BODY: You have a shared account with an LLM bolted onto it. Full essay, interactive diagrams, and audio cuts (DE + EN) — link in the comments.
FOOTER: hupfauer.one
