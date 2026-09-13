# bundle 01 · Card — "either it's broken, or it's insecure"

Square 1080×1080 card at `out/creative/you-cant-triage-a-bundle.png`, rebuilt by `build/build-creative.py`. First atom for the post ["You can't triage a bundle"](https://hupfauer.one/posts/you-cant-triage-a-bundle/).

Named by post slug rather than folded into the flat `01–04` set, which belongs to the "which agent bricked prod?" campaign.

The card states the dilemma flat — install it and RDS breaks, roll it back and you return 679 fixes — and hangs every caveat off an asterisk underneath. That split is deliberate: the hook stays blunt enough to stop a scroll, the nuance is all still there for anyone who opens the image, and nobody gets to accuse the card of overclaiming. The dagger hangs off the word "or", because the note it points to is the one that says the binary is false.

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
> The caveats are on the card, and one matters more than the rest: there is usually a third option nobody advertises — keep the update, turn off the offending feature. Knowing which behaviours each critical workload can survive losing, before the month you need it, is most of the job.
>
> Counted from Microsoft's own release data, not from the coverage. Full piece in the comments.
>
> #PatchManagement #VulnerabilityManagement #WindowsServer #AIsecurity #GeneratedByOpus #AI_Generated

**First comment:** https://hupfauer.one/posts/you-cant-triage-a-bundle/

---

## Image text

KICKER: KB5122871 · WINDOWS SERVER 2025 · 8 SEPTEMBER 2026
HEADLINE: Tough luck if you run RDS. Either it's broken, or it's insecure.

LEFT — INSTALL THE UPDATE → **BROKEN\***
Remote Desktop Services goes unstable. Connections fail after minutes, sign-ins hang, hosts wedge at logoff. Microsoft's published workaround: stop the VM, deallocate it, start it again, and wait for a future update.

RIGHT — ROLL IT BACK → **INSECURE\*\***
All 679 CVE fixes in the package go back with it. There is no way to keep 678 and drop the one that broke you, and one of the 679 is already under active exploitation.\*\*\*

FOOTNOTES:
- \* Not everywhere. Microsoft says "some organizations" and has confirmed no cause. Administrators trace the trigger to a change in remote audio redirection — that is community attribution, not a vendor statement.
- \*\* Most of those 679 will never be used against you. That is not the point: prioritisation assumes you can act on the ranking, and inside a cumulative update you cannot express it at all.
- \*\*\* CVE-2026-81963, Windows Update Stack elevation of privilege, flagged by Microsoft as Exploitation Detected. The month's other exploited zero-day ships in a different package.
- † (on "or") There is a third option nobody advertises: keep the update, disable remote audio redirection by policy. Reader-reported, unconfirmed — and for a call centre the feature you just switched off is the product.

ATTRIBUTION: hupfauer.one · you can't triage a bundle
