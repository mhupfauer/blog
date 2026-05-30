# 03 · Audiogram (native LinkedIn video)

Pull a 60–90 second clip from the Bench cut — the OT-trajectory paragraph reads especially well aloud. The build script extracts the slice, renders a square (1080×1080) MP4 with the cover image as background and a live waveform, and burns the spoken text as captions.

Outputs land at `out/audiograms/bench-en.mp4` and `out/audiograms/bench-de.mp4`. Upload as native video on LinkedIn — native video out-reaches link posts by ≈ 2×.

Recommended slots: Thursday week 1 (EN), Monday week 2 (DE), 08:30 CET.

---

## English (post body)

> 90 seconds, straight from the Bench cut: how the AI-first roadmap reaches the shop floor — read-only at first, then a maintenance ticket, then a batch parameter "within the validated window". Each step defensible. None of them re-asks whether the chain that issues the write can name the person and the agent behind it.
>
> Boardroom cut (~10 min) and Bench cut (~12 min), EN + DE, in the comments.
>
> #AgenticAI #OTSecurity #IdentityAccessManagement

**First comment:** https://hupfauer.one/posts/which-agent-bricked-prod/

---

## Deutsch (post body)

> 90 Sekunden, direkt aus dem Bench-Cut: Wie die AI-First-Roadmap die Werkshalle erreicht — erst read-only, dann ein Wartungsticket, dann ein Batch-Parameter "im validierten Bereich". Jeder Schritt für sich verteidigbar. Keiner davon fragt erneut, ob die Kette, die den Write absetzt, die Person und den Agent dahinter benennen kann.
>
> Boardroom-Cut (~10 min) und Bench-Cut (~14 min), EN + DE, in den Kommentaren.
>
> #AgenticAI #OTSecurity #IAM

**Erster Kommentar:** https://hupfauer.one/posts/which-agent-bricked-prod/

---

## Clip selection

Choose by ear in the script.txt for each cut. The build script takes start/end timestamps (in seconds) — adjust at the top of `build-audiograms.py` after listening to the existing mp3s.
