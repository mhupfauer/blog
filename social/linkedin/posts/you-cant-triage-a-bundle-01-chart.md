# bundle 01 · Card — "either it's broken, or it's insecure"

Square 1080×1080 card at `out/creative/you-cant-triage-a-bundle.png`, rebuilt by `build/build-creative.py`. First atom for the post ["You can't triage a bundle"](https://hupfauer.one/posts/you-cant-triage-a-bundle/).

Named by post slug rather than folded into the flat `01–04` set, which belongs to the "which agent bricked prod?" campaign.

The card had to survive four rejected attempts: an AI illustration that said nothing, a 679-square unit chart that was too cerebral, and two typographic cuts that named the dilemma without showing what causes it. The art direction that fixed it came from gpt-6-astra, and the diagnosis was the useful part — "BROKEN or INSECURE" describes any security trade-off, while the distinctive fact, 679 fixes welded into one package, had been demoted to small print. Caveats live in the post body, not on the image.

Recommended slot: Tuesday or Thursday, 08:30 CET. The first two lines carry it, before LinkedIn's "see more" cut. Copy and card open on the same sentence on purpose — don't reword one without the other.

Every figure comes from Microsoft's MSRC CVRF release data for 2026-Sep, not press coverage: 679 CVEs cite KB5122871 (Windows Server 2025 only), exactly one of which carries `Exploited:Yes` — CVE-2026-81963. The widely quoted "966" is the release-wide figure across all Microsoft products; using it here would be wrong and would earn a correction in the comments.

---

## English (post body)

> Tough luck if you run Remote Desktop Services this month. Either it's broken, or it's insecure.
>
> Install Microsoft's September update for Windows Server 2025 and RDS goes unstable — connections failing after minutes, sign-ins hanging, hosts wedging at logoff. The published workaround: stop the VM, start it again, and wait for a future update.
>
> Roll it back and you hand back all 679 CVE fixes that ship in that one package, including one already under active exploitation. There is no way to keep 678 and drop the one that broke you. Not in WSUS, not in Intune, not in any patching product on the market.
>
> Which means the ranked list your vulnerability programme produces — CVSS, EPSS, KEV, pick your framework — cannot be expressed at the one moment it was supposed to pay off. Fifteen years of risk-based vulnerability management bought us the ability to rank a list we are not allowed to act on.
>
> AI-scale discovery didn't break patching. It broke triage.
>
> Two caveats the card has no room for. It doesn't hit every environment — Microsoft says "some organizations" and still hasn't confirmed a cause; administrators trace it to a change in remote audio redirection, which is community attribution, not a vendor statement. And there is usually a third option nobody advertises: keep the update, turn off the offending feature. Knowing which behaviours each critical workload can survive losing, before the month you need it, is most of the job.
>
> Counted from Microsoft's own release data, not from the coverage. Full piece in the comments.
>
> #PatchManagement #VulnerabilityManagement #WindowsServer #AIsecurity #GeneratedByOpus #AI_Generated

**First comment:** https://hupfauer.one/posts/you-cant-triage-a-bundle/

---

## Image text

Concept: **one sealed package, two bad exits.** The composition is the argument — a single uninterrupted bone block holds 679 and states it cannot be subdivided, then one rust fork leaves it and splits into two consequences of identical weight. The reader should understand the trap before reading the thesis line.

TOP LEFT: WINDOWS SERVER 2025      TOP RIGHT: SEPTEMBER 2026
HEADLINE: One update. / Two bad exits.
BLOCK: **679** · CVE fixes. / One cumulative update. / No selective install.
LEFT EXIT: INSTALL UPDATE → **BROKEN** / Remote Desktop Services fails.
RIGHT EXIT: ROLL BACK UPDATE → **INSECURE** / All 679 fixes removed. / One actively exploited CVE.
THESIS: Prioritisation needs a choice. / Cumulative updates remove it.

No attribution line, no footnotes, no logo.

Do not subdivide the block when editing — segmenting it contradicts the whole point. Keep rust to the seal and the fork only; it should read as causality, not decoration.
