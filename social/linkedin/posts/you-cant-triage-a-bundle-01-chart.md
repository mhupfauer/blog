# bundle 01 · Chart — 679 in one package, one of them exploited

Square 1080×1080 unit chart at `out/creative/you-cant-triage-a-bundle.png`, rebuilt by `build/build-creative.py`. First atom for the post ["You can't triage a bundle"](https://hupfauer.one/posts/you-cant-triage-a-bundle/).

Named by post slug rather than folded into the flat `01–04` set, which belongs to the "which agent bricked prod?" campaign.

Recommended slot: Tuesday or Thursday, 08:30 CET. The hook does its work in the first two lines, before LinkedIn's "see more" cut — do not bury the 679 below it.

Every figure in the copy is counted from Microsoft's MSRC CVRF release data for 2026-Sep, not from press coverage: 679 CVEs cite KB5122871 (Windows Server 2025 only), exactly one of which carries `Exploited:Yes` — CVE-2026-81963. Worth saying out loud in the post, because the widely quoted "966" is the release-wide figure across all products and invites a correction in the comments.

---

## English (post body)

> Microsoft's September update for Windows Server 2025 fixes 679 CVEs in one package. Exactly one of them is under active exploitation.
>
> There is no way to install only that one.
>
> Not in WSUS, not in Intune, not in any patching product on the market. Inside a Windows cumulative update you take the applicable contents whole, or you take none of them. So the ranked list your vulnerability programme produces — CVSS, EPSS, KEV, pick your framework — cannot be expressed at the one moment it was supposed to pay off.
>
> The same update then left Remote Desktop Services unstable on everything from Windows 11 back to Server 2012. Microsoft's published workaround: stop the VM, deallocate it, start it again, and wait for a future update. Roll the package back to get your session hosts working again and you have just handed back 679 fixes, including the one being exploited.
>
> Fifteen years of risk-based vulnerability management bought us the ability to rank a list we are not allowed to act on — on the largest and most uniform estate most of us own.
>
> AI-scale discovery didn't break patching. It broke triage.
>
> What's left is unglamorous. Make rollout, compensating controls and validation autonomous, because elapsed human time is the only variable in this you actually control. Then keep exactly two things human: what "working" means for each critical service, and who carries the exposure on the month when neither option is safe.
>
> Counted from Microsoft's own release data, not from the coverage. Full piece in the comments.
>
> #PatchManagement #VulnerabilityManagement #WindowsServer #AIsecurity #GeneratedByOpus #AI_Generated

**First comment:** https://hupfauer.one/posts/you-cant-triage-a-bundle/

---

## Image text

KICKER: KB5122871 · WINDOWS SERVER 2025 · 8 SEPTEMBER 2026
HEADLINE: One of these is under active attack. You install all 679, or none.
LEGEND: 1 · CVE-2026-81963, exploitation detected / 678 · everything else in the same package
ATTRIBUTION: hupfauer.one · you can't triage a bundle
