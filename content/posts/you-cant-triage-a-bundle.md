---
title: "You can't triage a bundle"
slug: "you-cant-triage-a-bundle"
date: 2026-09-13T15:30:00+02:00
draft: false
tags: ["security", "patch-management", "vulnerability-management", "ai-security", "detection-engineering", "resilience"]
keywords: ["Patch Tuesday September 2026", "KB5122871", "Remote Desktop Services broken update", "AI vulnerability discovery", "cumulative update rollback", "Known Issue Rollback", "risk-based vulnerability management", "patch ring automation", "compensating controls", "autonomous patching", "release validation", "NIS2 incident reporting", "time to exploit"]
description: "The single September cumulative update for Windows Server 2025 fixes 679 CVEs — and left Remote Desktop Services unstable on everything from Windows 11 back to Server 2012. Roll it back and you give back all 679. Risk-based vulnerability management assumes you can choose which fixes to install; a cumulative update removes the choice."
summary: "AI-scale discovery did not break patching. It broke triage. Prioritisation frameworks rank vulnerabilities so you can act on some and defer others, and on a Windows cumulative update that ranking buys you nothing — you take the applicable contents whole or you take none of them. The September 2026 release and the RDS regression it carried are the same event seen from both ends. What follows: why the three default responses are all bad, why conventional validation was never going to catch this class of regression, and what changes when rollout, compensating controls and validation stop being things humans do by hand once a month."
canonicalURL: "https://hupfauer.one/posts/you-cant-triage-a-bundle/"
cover:
  image: "you-cant-triage-a-bundle.jpg"
  alt: "Abstract illustration: a dense block of stacked lines descending toward a narrow aperture, with a single thin rust-coloured line passing through alone"
  hidden: false
  relative: false
---

On 8 September Microsoft shipped fixes for 966 vulnerabilities — its largest security release ever, and very nearly twelve times the 81 it shipped in the same month last year.[^pt2026][^pt2025] Three days later it opened a known-issue entry titled "Remote Desktop Services might stop responding after Sept. 2026 security update." In Microsoft's own words, RDS "might become unstable, resulting in RDP connections failing after several minutes, sign-in issues, or servers hanging at 'Please wait for the Remote Desktop Configuration'," with MMC, the RDS Licensing Diagnoser and File Explorer going unresponsive alongside it. Affected platforms run from Windows 11 version 26H1 back to Windows Server 2012. The published workaround, in full, is that if a virtual machine becomes unreachable over RDP you may be able to restore it by stopping, deallocating and restarting it; the KB article suggests affected organisations contact Microsoft Support for Business.[^rds][^kb]

So an administrator with a terminal-server estate spent last week choosing between two things. Keep the update, and keep session hosts that wedge hours after boot and strand users at logoff. Or uninstall it — which is what people did, by script, over DISM, to the machines they could still reach[^rdsreports] — and give back everything else in the package in order to restore usable sessions.

It is worth being exact about what "everything else" means, because the number is the argument. Microsoft's own release data says KB5122871, the single September cumulative update for Windows Server 2025, remediates **679 CVEs**: 378 elevation of privilege, 147 remote code execution, 85 information disclosure, 47 denial of service, and 63 of them rated Critical. Among them is CVE-2026-81963, a Windows Update Stack privilege-escalation bug Microsoft flags as *Exploitation Detected*. On Server 2022 the equivalent package carries 641 CVEs, on Server 2019 616, and those two carry the month's *other* exploited zero-day, the ALPC overflow CVE-2026-85880, which does not affect Server 2025 at all.[^cvrf]

So the trade was not one bad change against a handful of fixes. It was one bad change against six hundred and seventy-nine of them, and there is no third option inside the bundle, because the bundle does not come apart.

Be precise about what that does and does not claim, because the imprecise version is easy to knock down. Patch Tuesday as a whole is not one artifact: it spans Office, Azure, SQL Server and the rest, and any competent admin approves and withholds by product, platform and KB. The constraint is one level down, inside the OS package. There is no mechanism — not in WSUS, not in Intune, not in your patching vendor of choice — to take 678 of those 679 fixes and leave the one that broke RDS. The unit you assess risk in is the CVE. The unit you deploy in is the cumulative update, and this month that unit was 679 CVEs wide. Those have never been the same unit; for twenty years the gap was narrow enough not to matter.

It matters now, and the reflex reading of why is wrong. This is not a story about Microsoft's QA slipping. QA did not get twelve times worse in twelve months. What changed is how much is riding in the same vehicle, on the same monthly cadence, into the same four-hour change window you had last year.

## The vendor got an accelerator and the vehicle didn't

Microsoft said the volume part itself, and said it months in advance. In July it published a note on evolving vulnerability management "to meet the speed of AI-powered discovery," describing a multi-model agentic scanning harness it calls MDASH and telling customers plainly that "as AI helps defenders discover more issues, customers will see a higher volume of security updates included in each security release."[^msft] September was not a surprise. It was the thing the vendor told you was coming, arriving.

Take it at face value, too, because it is probably true and it is certainly good. Those bugs existed last September. A remote code execution flaw that sat in FreeBSD's NFS server for seventeen years — until a model found it and then autonomously exploited it to root this spring[^mythos] — was not safer for the seventeen years nobody knew about it. Discovery is not the problem and I am not going to pretend it is.

Nor is this a Microsoft phenomenon, which matters more than the Microsoft part. Anthropic and roughly fifty partners reported finding more than ten thousand high- or critical-severity issues in widely used software in a single month under Project Glasswing.[^glasswing] Google's Big Sleep has been filing against open-source projects for over a year. Every vendor in your estate is queuing for the same accelerator, and the ones who reach it will ship what they find down the monthly pipes they already have. September is simply the first month where it became impossible to ignore, because Windows is where the fleet is homogeneous, the update is undecomposable, and skipping is not on the menu.

That undecomposability is deliberate, and Microsoft's own tooling admits the cost of it. Known Issue Rollback exists so that Microsoft can remotely disable a specific *non-security* change that turned out to be bad, without disturbing the security content shipping beside it — and it explicitly does not apply to security fixes.[^kir] That mechanism is an admission, in code, that a monthly bundle of security and quality changes sometimes needs a scalpel after it has left the building.

But notice what wielding it requires: for Microsoft to switch off one bad change, somebody must first know *which* change is bad. Days after the RDS reports started, there was no confirmed cause, no KIR, and a community reverse-engineering a theory out of one line in the changelog about improved audio redirection. That is this post's argument stated inside the vendor's own tooling — as the volume of change outruns the attention available per change, the scalpel gets harder to aim, and it is therefore least likely to be available in exactly the months you would most want it. What administrators had instead was the blade: the update, or not the update.

I want to be careful about the causal step here, because it is the one a vendor would attack. More CVEs fixed does not mechanically mean proportionally more regression risk; plenty of those fixes are small, isolated, or in code paths nothing touches. The honest claim is narrower and survives anyway. Validation capacity — anyone's, at any vendor — does not scale one-for-one with discovered defects. When shipped change volume rises sharply and the release cadence, the package structure and the regression budget per change do not, the chance that a given month's bundle carries something that breaks *your specific environment* stops being a tail risk and becomes a planning assumption. Plan for it accordingly. That is the whole of the inference, and it does not require knowing anything about Microsoft's staffing.

## The objection I have to kill first

The sharp reader has the rebuttal loaded: *966 is a discovery artifact. Most of those are low-value bugs nobody will ever weaponise, the count is inflated by a model that got good at finding overflows in parsers, and treating it as twelve times the risk is innumerate.*

Correct, and I want to concede it with numbers rather than grudgingly, because the concession is where the argument gets teeth.

VulnCheck's first-half 2026 data says the exploitation curve did not bend the way the discovery curve did. 495 vulnerabilities entered known-exploited status in 1H 2026, roughly 200 of them within 31 days of publication — against roughly 194 in the equivalent 2025 window. Flat. The share showing exploitation on or before the publication date actually *fell*, from 28.93% to 23.43%. And of 1,061 vulnerabilities attributed to AI-assisted discovery, 14 — 1.3% — have been confirmed exploited in the wild.[^vulncheck]

Read those with their limits attached, because I am about to lean on them. 1.3% confirmed-exploited is a floor, not a verdict: it reflects an observation window of months against bugs disclosed recently, and confirmation depends on somebody having the telemetry to see it. "Publication to known exploitation" is not "publication to first exploitation." The defensible reading is not that the other 98.7% are harmless — it is that discovery volume and observed exploitation volume have not risen together, and nothing in the data supports the n-day-is-now-n-hour register the vendor blogs have adopted. The one genuinely bad number in the set is the median from publication to known exploitation, which fell from 120 days to 80.

So the panic version of this post would be wrong, and I am not writing it. In an ecosystem with separable fixes, a defender who installed sixteen of those 679 and deferred the rest — having established that the sixteen are applicable, reachable and exposed in their estate, and the rest are not — would have made a good technical call.

They just don't get to make it. That is the entire point. Prioritisation — CVSS, EPSS, KEV, whatever your programme runs on — produces a ranked list whose purpose is to tell you which fixes to install now and which to defer. Feed that list into a Windows cumulative update and the ranking cannot be expressed. Not "is expensive to express." Cannot. Every euro the industry spent over fifteen years building risk-based vulnerability management bought you the ability to rank a list you are not allowed to act on, on the largest and most uniform fleet you own.

Note what that does and doesn't indict. Risk-based prioritisation still works, and works well, wherever fixes are separable: Linux packages, appliance firmware, third-party applications, browser extensions, container base images, SaaS configuration. This is not a claim that ranking vulnerabilities is useless. It is a claim that it fails precisely where most enterprises have their largest homogeneous estate, and that the failure got much more expensive the moment the undecomposable artifact started carrying an order of magnitude more change.

AI-scale discovery did not break patching. It broke triage — and it broke it at the point of deployment, which is the only point where triage was ever supposed to cash out.

## The three defaults, priced honestly

Most organisations answer this with one of three postures. None of them is good, and I want to be clear that these are the common defaults rather than the whole decision space — the useful answers are combinations, and they are the subject of the back half of this post.

**Install on day one with light validation.** You accept an unpredictable functional regression in exchange for closing the month's exploited bugs. Last week that bill came due as a terminal-server estate that stops accepting sessions. Security teams habitually price this at zero, and it is not zero: if the affected service is payments, clinical systems, dispatch or telephony, the outage is an incident in its own right. Depending on your sector, entity classification and whether the disruption crosses the significance thresholds, a self-inflicted availability failure can put you on the NIS2 clock — early warning inside 24 hours, notification inside 72 — which is the same clock a breach starts. That is a conditional, not a universal; the point is only that your own change is capable of triggering the obligation you bought the patching programme to discharge.

**Wait a month.** The strategy that has quietly worked for twenty years. Two things about it. First, staged delay is legitimate reliability engineering — deploying to a canary population and watching before going broad is what you should do, and I am not sneering at it. What is parasitic is the specific version most organisations run: not staging, but waiting for *other people's* production to act as your canary. It works because someone with more exposure installs first, breaks, files support cases, posts to Born or BleepingComputer, and generates enough signal — crash dumps, telemetry, forum noise — that the vendor publishes a known issue before your change window opens. That is an externality you are consuming, and last week you consumed it from whoever ran the September update against a busy session host on the 8th.

Second, price the delay honestly, which means *not* reaching for the 966 again after I just spent a section disavowing count panic. The cost of a thirty-day deferral is not "thirty days of exposure to 966 vulnerabilities." It is thirty days of exposure to the few in that bundle that are actually applicable, reachable and being used — on any given Windows server this month, exactly one of the two elevation-of-privilege bugs Microsoft marks as exploited, which matters in the post-initial-access and lateral-movement part of an intrusion rather than as a front door — against a median publication-to-exploitation window that is now 80 days.[^vulncheck] A thirty-day wait spends more than a third of that median. And note what waiting does not buy: updates are cumulative, so you are not skipping the bad change, you are deferring it. Unless the vendor fixes it first, October's bundle contains September's regression. You choose when you meet it, not whether.

**Don't patch.** Unmanaged indefinite deferral is not a strategy, and I want to separate it from something that looks similar and is defensible. A deliberately unpatched system — an OT controller under certification constraints, a clinical device the vendor will not let you touch — sitting behind enforced isolation with a named risk owner and a review date is an engineering decision. "We'll get to it" is not, and it is what the industry is drifting into by accident: Verizon's 2026 DBIR puts the median time for full patching at 43 days, up from 32 the year before, and finds that organisations patched just 26% of the defects in CISA's known-exploited catalogue, down from 38%.[^dbir] Not 26% of everything — 26% of the list of things confirmed to be in use by attackers. Defenders got slower while the queue got longer, and nobody chose that.

Notice the shape all three share. Every one of them is rationed by *elapsed human time* — validation time, decision time, rollout time. That is the only variable in this equation you control, and it is the one thing AI on the defender side genuinely moves. Not detection. Not triage, which we have established has nowhere to cash out. The clock.

## Your ten-minute smoke test would not have caught this

Before the prescription, kill the comfortable answer, which is "test more thoroughly."

Read the RDS failure as an engineer. Instability "in some environments." Connections failing after several minutes. Hangs as users log off. One administrator's debugging pointed at a deadlock between Remote Desktop and the Local Session Manager; the community's working theory traces the trigger to a change in remote audio redirection. Microsoft has confirmed neither.[^rdsreports][^born] The precise mechanism is still unknown, and the operational lesson does not depend on it: the reported failure needs concurrency, duration, real session churn, and a device-redirection configuration that a large share of deployments never enable.

A ten-minute smoke test that opens a session, checks a window appears and disconnects cleanly will pass. A two-hour UAT with three people clicking through an application will very likely pass. I am not claiming nobody could have caught it — a shop that soak-tests RDS with logoff storms and redirection enabled might have, and if that is you, you are rare enough to prove the point. The claim is that the validation most enterprises actually run is *structurally* incapable of surfacing this class of defect, because it tests the wrong shape: short, serial, single-user, with defaults nobody in production uses.

So "test more" is the wrong axis. The axis is test shape — derived from what production actually does, run at production concurrency, sustained long enough for a race to lose, against the workloads whose outage is a reportable event. And be clear about what such a suite proves: it proves the service still works after the vendor's patch. It does not prove the vulnerability is fixed. Those are different validations and only one of them is yours to run.

Nobody has ever had the human hours to write and maintain that per critical service, which is why almost nobody has it. That, narrowly, is what changed on the defender side.

## What to actually build

Two things, really: a machine that moves updates, and a brake you can reach without stopping the machine. The four pieces below split evenly between them.

<figure class="post-diagram">
<div class="diagram-scroll">
<svg viewBox="0 0 720 756" role="img" aria-label="Swimlane diagram of an autonomous patch pipeline. Columns are Signal, Pipeline, Validation, Human and Production. The vendor bundle of 679 indivisible CVEs is ingested by the pipeline, which generates a ring predicate as IaC, enforced denies, detection rules and a test suite derived from production telemetry. Validation soaks that suite at production load in its own trust domain and signs an attestation. A human reads one diff and owns the invariants, then approves promotion to ringed production rollout under a rate cap. An invariant breach in production returns to a second human gate for risk acceptance, which kills the feature rather than the update. Production telemetry regenerates next month's test suite." font-family="ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif" fill="currentColor">
<title>Signal to deployment in an autonomous patch pipeline</title>
<desc>Five columns show which actor does what: the vendor emits an indivisible bundle, the pipeline authors artifacts, a separate validation domain signs an attestation, a human gates on invariants and on risk acceptance, and production rolls out in rate-capped rings with a feedback loop back to test generation.</desc>
<defs>
<marker id="tb-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
<marker id="tb-arrow-accent" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#C25A2E"/></marker>
</defs>

<rect x="5" y="34" width="134" height="714" fill="currentColor" opacity="0.03"/>
<rect x="149" y="34" width="134" height="714" fill="currentColor" opacity="0.03"/>
<rect x="293" y="34" width="134" height="714" fill="currentColor" opacity="0.03"/>
<rect x="437" y="34" width="134" height="714" fill="currentColor" opacity="0.045"/>
<rect x="581" y="34" width="134" height="714" fill="currentColor" opacity="0.03"/>

<g font-size="10" opacity="0.6" text-anchor="middle" letter-spacing="0.9">
<text x="72" y="18">SIGNAL</text>
<text x="216" y="18">PIPELINE</text>
<text x="360" y="18">VALIDATION</text>
<text x="504" y="18" fill="#C25A2E" opacity="1">HUMAN</text>
<text x="648" y="18">PRODUCTION</text>
</g>
<line x1="5" y1="28" x2="715" y2="28" stroke="currentColor" stroke-width="1" opacity="0.25"/>

<rect x="11" y="46" width="122" height="72" rx="3" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="72" y="65" font-size="12" text-anchor="middle">Vendor bundle</text>
<text x="72" y="83" font-size="13" text-anchor="middle" font-weight="600">679 CVEs</text>
<text x="72" y="98" font-size="10" text-anchor="middle" opacity="0.7">all or none</text>
<text x="72" y="112" font-size="10" text-anchor="middle" opacity="0.7">+ known-issue feed</text>

<path d="M72,118 V133 H216 V148" fill="none" stroke="currentColor" stroke-width="1.2" marker-end="url(#tb-arrow)"/>
<text x="144" y="129" font-size="10" text-anchor="middle" opacity="0.75">ingest</text>

<rect x="155" y="148" width="122" height="40" rx="3" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="216" y="166" font-size="11.5" text-anchor="middle">Ring predicate</text>
<text x="216" y="180" font-size="9.5" text-anchor="middle" opacity="0.7">as IaC</text>

<rect x="155" y="195" width="122" height="40" rx="3" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="216" y="213" font-size="11.5" text-anchor="middle">Enforced denies</text>
<text x="216" y="227" font-size="9.5" text-anchor="middle" opacity="0.7">the control</text>

<rect x="155" y="242" width="122" height="40" rx="3" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="216" y="260" font-size="11.5" text-anchor="middle">Detection rules</text>
<text x="216" y="274" font-size="9.5" text-anchor="middle" opacity="0.7">the sensor</text>

<rect x="155" y="289" width="122" height="40" rx="3" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="216" y="307" font-size="11.5" text-anchor="middle">Test suite from</text>
<text x="216" y="321" font-size="9.5" text-anchor="middle" opacity="0.7">prod telemetry</text>

<path d="M216,329 V344 H360 V359" fill="none" stroke="currentColor" stroke-width="1.2" marker-end="url(#tb-arrow)"/>
<text x="288" y="340" font-size="10" text-anchor="middle" opacity="0.75">to non-prod</text>

<rect x="299" y="359" width="122" height="82" rx="3" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="360" y="379" font-size="11.5" text-anchor="middle">Soak at prod load</text>
<text x="360" y="393" font-size="10" text-anchor="middle" opacity="0.7">hours, not minutes</text>
<line x1="311" y1="402" x2="409" y2="402" stroke="currentColor" stroke-width="1" opacity="0.25"/>
<text x="360" y="418" font-size="11.5" text-anchor="middle">signs attestation</text>
<text x="360" y="432" font-size="9.5" text-anchor="middle" opacity="0.7">own trust domain</text>

<path d="M360,441 V456 H504 V471" fill="none" stroke="currentColor" stroke-width="1.2" marker-end="url(#tb-arrow)"/>
<text x="432" y="452" font-size="10" text-anchor="middle" opacity="0.75">PR + attestation</text>

<rect x="443" y="471" width="122" height="82" rx="3" fill="none" stroke="#C25A2E" stroke-width="1.8"/>
<text x="504" y="490" font-size="9.5" text-anchor="middle" fill="#C25A2E" letter-spacing="0.8">HUMAN GATE</text>
<text x="504" y="509" font-size="11.5" text-anchor="middle">Read one diff</text>
<text x="504" y="525" font-size="11" text-anchor="middle">Own the invariants</text>
<text x="504" y="540" font-size="9.5" text-anchor="middle" opacity="0.7">what &#8220;working&#8221; means</text>

<path d="M504,553 V568 H648 V583" fill="none" stroke="#C25A2E" stroke-width="1.5" marker-end="url(#tb-arrow-accent)"/>
<text x="576" y="564" font-size="10" text-anchor="middle" fill="#C25A2E">approve</text>

<rect x="587" y="583" width="122" height="90" rx="3" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="648" y="602" font-size="11.5" text-anchor="middle">canary &#183; pilot</text>
<text x="648" y="618" font-size="11.5" text-anchor="middle">broad &#183; critical</text>
<line x1="599" y1="630" x2="697" y2="630" stroke="currentColor" stroke-width="1" opacity="0.25"/>
<text x="648" y="647" font-size="11" text-anchor="middle">&#8804; N hosts / hour</text>
<text x="648" y="662" font-size="9.5" text-anchor="middle" opacity="0.7">one service in flight</text>

<rect x="443" y="600" width="122" height="90" rx="3" fill="none" stroke="#C25A2E" stroke-width="1.8"/>
<text x="504" y="619" font-size="9.5" text-anchor="middle" fill="#C25A2E" letter-spacing="0.8">HUMAN GATE</text>
<text x="504" y="638" font-size="11.5" text-anchor="middle">Risk acceptance</text>
<text x="504" y="654" font-size="10.5" text-anchor="middle">kill the feature,</text>
<text x="504" y="669" font-size="10.5" text-anchor="middle">not the update &#8212;</text>
<text x="504" y="684" font-size="10.5" text-anchor="middle">or hold the bundle</text>

<path d="M648,673 V706 H504 V696" fill="none" stroke="#C25A2E" stroke-width="1.5" stroke-dasharray="5 3" marker-end="url(#tb-arrow-accent)"/>
<text x="578" y="701" font-size="10" text-anchor="middle" fill="#C25A2E">invariant breach</text>

<path d="M565,637 H581" fill="none" stroke="#C25A2E" stroke-width="1.5" marker-end="url(#tb-arrow-accent)"/>

<path d="M690,673 V730 H180 V335" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="5 3" opacity="0.75" marker-end="url(#tb-arrow)"/>
<text x="447" y="725" font-size="10" text-anchor="middle" opacity="0.75">telemetry regenerates next month&#8217;s suite</text>
</svg>
</div>
<figcaption>The machine authors, validates and deploys; the human is consulted twice — once on what &#8220;working&#8221; means before the rollout, once on carrying the exposure after something breaks. Nothing in the Signal column is separable, which is why every arrow after it is about containment rather than selection.</figcaption>
</figure>

**One: automate the pipeline, not the decision.** Rings are a solved idea, and nearly everyone who has them promotes between rings on a human calendar — which is exactly why the cadence is a month. Define the rings in IaC and define promotion as a machine-evaluable predicate over your own telemetry. Concretely, for a session-host fleet: a canary ring has accumulated at least *N* session-hours and *M* logoff cycles since the update landed; error rates on the top transactions sit within a defined band of the unpatched cohort still running beside it; telemetry coverage itself is above a floor, so that silence is treated as missing signal rather than as health; and any of those failing halts promotion rather than merely annotating it. The human writes and owns that predicate. The machine executes it, monthly, without a meeting. A model is genuinely good at generating and maintaining the Terraform, Bicep or Ansible underneath, and at reconciling the drift that makes most patch estates lie to you about their own coverage.

Building this creates a new problem immediately — an automated system with standing rights to push vendor code to every host you own — and I will come back to it, because it is the price of everything in this section.

**Two: distinguish the two kinds of control, and then the two kinds of thing you write.** There are two different jobs being done under the word "mitigation." One reduces exploitability while you are waiting to patch. The other contains functional blast radius while keeping the patch installed. Conflating them is how teams end up believing they have covered a CVE when what they actually did was work around a regression.

Within the first job, the distinction this site keeps returning to applies unchanged: a Sigma rule, a YARA signature, a Snort alert are sensors. An enforced deny at a choke point, a blocking WAF rule, a disabled feature, a segment boundary are controls. Generate both — a model writes either in seconds — but be honest about which one you just deployed, because forty new detection rules produce a strong feeling of having done something and change nothing about reachability. Two caveats worth more than the slogan. A CVE description frequently does not contain enough detail to produce a rule that actually matches exploitation rather than plausible-looking traffic, so enforcement needs testing for both coverage and collateral damage before it goes in blocking mode. And network chokepoints do nothing for a local elevation-of-privilege bug, a malicious document opened by a trusted user, or authenticated lateral movement — which is to say they do nothing for either of this month's exploited zero-days. Deploy them where a chokepoint genuinely exists, and say plainly where none does. This is the same line I drew about [identity scoping versus input filtering](/posts/identity-is-the-control-plane/) and about [auto-mode classifiers](/posts/auto-mode-is-a-sensor-too/).

**Three: generate validation from telemetry, not from imagination.** Point a model at what you already record for a critical service — top transaction paths, session duration distributions, concurrency envelopes, client capability mix, the periodic jobs, the feature and redirection settings actually in use — and have it emit a suite that reproduces that, then run it in non-prod at real concurrency for hours rather than minutes and gate ring promotion on the result.

Three limits, because this is the part of the post most exposed to sounding like the vendor blogs I have been mocking. Recorded production behaviour is not ground truth: telemetry omits the rare-but-critical path precisely because it is rare, and it will faithfully reproduce defects you already have. A generated suite can encode the wrong invariants and hand you a green light you trust more than you trusted your own instinct, so keep the human-approved invariants stable and diff the generated assertions each month — the assertions that quietly disappear are the interesting ones. Monthly regeneration should refresh the workload, never the definition of success. And the inputs are session records, access logs and traces, which means credentials, tokens and personal data: minimise and sanitise before they go anywhere, prefer a model you host for this, and treat the generated suite as a derived sensitive artifact. The cure should not open a new exposure path.

What this actually buys is not perfect validation. It is that the authoring and maintenance cost of a representative suite falls far enough that running one every month becomes plausible, where before it was a project nobody finished twice.

**Four: rehearse turning the feature off, not the update.** Some failures you can only observe, and there the reach time is everything. The move a lot of administrators reached for first was not uninstalling anything — it was disabling remote audio redirection by policy on the affected session hosts, keeping every security fix installed. Community admins got there before any vendor documentation did.[^born] Note the shape: the control was not `uninstall-kb`, it was a group policy setting, and a model reading the release notes and the known-issue text can propose that and write it for you.

Two honest qualifications. That specific mitigation is reader-reported, not confirmed, and for a call centre the "unnecessary feature" you just disabled may be the product. And plenty of regressions will have no convenient flag at all. So the move is not "feature flags solve this" — it is that for each critical workload you should already know which behaviours can be turned off independently of the update, and have found that out on a day when nothing was on fire.

The monthly artifact from all of this should be a pull request, not a project: the ring-definition diff, the enforced denies for what you cannot reach yet, the detection rules for what you cannot block, the regenerated test plan, and the inventory of feature-level kill switches for anything flagged risky. A human reads a diff in twenty minutes. That is the format judgement survives in.

## The pipeline is now your most dangerous identity

Build all of that and you have constructed a system with standing authority to push code to every host in the estate, on a schedule, without a human in the loop. Say it out loud and you will recognise the shape, because it is the one the industry has spent five years writing supply-chain incident reports about.

Some of the countermeasures are obvious and worth stating precisely rather than reassuringly. Verifying vendor signatures stops substituted packages; it does nothing about a compromised vendor build process or a maliciously legitimate signed artifact, so it is a floor, not a defence. Promotion between rings should consume an attestation the pipeline cannot mint for itself — concretely, a signed result from a validation runner in a separate trust domain, holding a signing key the deployment identity has no path to, with the promotion gate verifying that signature rather than reading a status field the pipeline can write. Rate caps on how many hosts may change per hour and what fraction of any single service may be in flight bound how fast a wrong decision propagates; they do not prevent estate-wide compromise, they buy you the minutes in which to notice, which is the same reason [the SOC middle needs an action budget](/posts/nobody-sells-your-middle/).

And separate two authorities that feel similar and are not. Installing vendor-signed updates is a narrow, auditable power. Deploying model-generated firewall rules, GPOs and test harnesses is a much broader one, because that content is authored by a system that reads attacker-influenced input — release notes, advisories, ticket text — and it should sit behind review even when the patch rollout does not. The whole [identity-scoping argument](/posts/identity-is-the-control-plane/) lands here in a new place: this pipeline is now among the most valuable credentials you own, and the failure mode to budget against is not that it breaks. It is that it works perfectly, for someone else.

## What stays human

Two things.

The definition of "working" for each critical service — the invariants, the acceptable degradation, which failure justifies stopping a security rollout mid-flight. A model can write the test that checks an invariant. It cannot tell you that four minutes of delay in the settlement batch is survivable and sixty seconds in dispatch is not. That is a business fact, and it is the input that makes everything upstream of it mean anything.

And the decision, when exposure and regression risk cannot both be driven to zero in the same month, about which one you are going to carry — accepted, priced, and written down under a name. The apparatus above exists to make that call rare. It does not make it go away, and it is not delegable, because it is the only part of this where being wrong is a judgement rather than a bug.

The basics did not change. Patch what can be patched, enforce controls in front of what cannot, validate against something resembling reality before production, and be able to reverse one behaviour without reversing everything. All of that was in a hardening guide twenty years ago. What changed is that doing it by hand, once a month, in a four-hour window, with three people and a spreadsheet, stopped being arithmetic that closes.

The old job was reading a list of vulnerabilities and deciding which ones to act on. That job is gone; the bundle ate it. The new job is telling a machine what "broken" means, precisely enough, before it finds out on its own.

[^pt2026]: "Microsoft September 2026 Patch Tuesday fixes 966 flaws, 2 zero-days," BleepingComputer, 8 Sep 2026 — 966 vulnerabilities across the whole release, of which 105 are rated Critical. Per-category totals quoted by outlets vary and do not reconcile exactly against the release data, which is why the per-package figures in this post are counted directly from Microsoft's CVRF rather than taken from reporting. The two exploited zero-days are CVE-2026-81963 (Windows Update Stack, link-following elevation of privilege) and CVE-2026-85880 (Windows ALPC, heap-based buffer overflow elevation of privilege). They affect different platform sets — see [^cvrf]. The article attributes the volume increase to Microsoft's adoption of an AI-powered vulnerability discovery system. Totals differ by outlet depending on whether releases adjacent to Patch Tuesday are counted — [SecurityWeek](https://www.securityweek.com/microsoft-patches-record-974-vulnerabilities-including-two-exploited-zero-days/) reports 974 — so treat the figure as a release-wide count, not a per-package one. [bleepingcomputer.com](https://www.bleepingcomputer.com/news/microsoft/microsoft-september-2026-patch-tuesday-fixes-966-flaws-2-zero-days/)
[^pt2025]: "Microsoft September 2025 Patch Tuesday fixes 81 flaws, two zero-days," BleepingComputer, 9 Sep 2025. Same publication and counting methodology twelve months earlier, which is why this is the comparison used here rather than a cross-outlet one. [bleepingcomputer.com](https://www.bleepingcomputer.com/news/microsoft/microsoft-september-2025-patch-tuesday-fixes-81-flaws-two-zero-days/)
[^rds]: "Remote Desktop Services might stop responding after Sept. 2026 security update," Windows release health, Windows Server 2025 known issues. Originating update KB5122871, OS Build 26100.33438, released 2026-09-08; opened 2026-09-11 11:19 PT, status *Mitigated*. Affected platforms span Windows 11 26H1/25H2/24H2/23H2, Windows 10 22H2/21H2, LTSC 2019 and 2016, and Windows Server 2025, 2022, 2019, 2016, 2012 R2 and 2012. [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/release-health/status-windows-server-2025)
[^kb]: KB5122871, September 8 2026 (OS Build 26100.33438). The update "contains fixes and quality improvements from KB5120233," i.e. security and non-security content in one package; the article does not enumerate the vulnerabilities it addresses, deferring to the Security Update Guide. It carries the RDS known issue and directs affected organisations to Support for Business. [support.microsoft.com](https://support.microsoft.com/en-us/servicing/os/windows-server/2026/09/kb5122871-windows-server-2025-security-update)
[^cvrf]: Counted from Microsoft's own machine-readable release data: the MSRC Common Vulnerability Reporting Framework document for September 2026 (`api.msrc.microsoft.com/cvrf/v3.0/cvrf/2026-Sep`), by taking every CVE whose remediation list cites the relevant KB. KB5122871 maps to Windows Server 2025 only and remediates 679 CVEs (378 elevation of privilege, 147 remote code execution, 85 information disclosure, 47 denial of service, 10 tampering, 9 security feature bypass, 3 spoofing; 63 Critical and 616 Important). KB5122882 (Server 2022) carries 641 and KB5122876 (Server 2019) 616. CVE-2026-81963 is remediated by KB5122871 and affects Windows 11 23H2 through 26H1 plus Server 2025; CVE-2026-85880 is not in KB5122871 and affects Windows 10 and Server 2019/2022/2016/2012 R2/2012. Both carry the MSRC threat string `Exploited:Yes … Exploitation Detected`. The document contains 1,239 CVE entries in total, more than the press counts, because it also includes republished non-Microsoft CVEs such as Chromium fixes carried by Edge. [msrc.microsoft.com](https://msrc.microsoft.com/update-guide/releaseNote/2026-Sep)
[^rdsreports]: "September Windows Server updates break Remote Desktop Services," BleepingComputer — KB5122876 (Server 2019), KB5122882 (Server 2022) and KB5122871 (Server 2025); administrators report the service becoming unresponsive as users log off, one attributing it to "a deadlock between RDP and LSM," and removing the packages remotely over DISM to restore service. [bleepingcomputer.com](https://www.bleepingcomputer.com/news/microsoft/september-windows-server-updates-break-remote-desktop-services/)
[^born]: "Windows: Remote Desktop Services (RDS) Issues Confirmed by the September 2026 Update," Born's Tech and Windows World, 12 Sep 2026 — community attribution of the trigger to a change in Remote Desktop audio redirection, and disabling remote audio as a reader-reported mitigation. Neither is confirmed by Microsoft. [borncity.com](https://borncity.com/win/2026/09/12/windows-remote-desktop-services-rds-issues-confirmed-by-the-september-2026-update/)
[^kir]: "Known Issue Rollback," Microsoft Learn — KIR reverts "only the targeted change, fix, functionality, or feature that caused the problem." It applies to non-security fixes; security fixes do not use it. It exists because security and non-security changes ship together in a single cumulative update. [learn.microsoft.com](https://learn.microsoft.com/en-us/troubleshoot/windows-server/installing-updates-features-roles/known-issue-rollback)
[^vulncheck]: "State of Exploitation 1H-2026," VulnCheck — 495 KEVs in the first half of 2026; 23.43% with evidence of exploitation on or before the CVE publication date, down from 28.93% in 2025; median publication-to-KEV of 80 days, down from 120; roughly 200 CVEs exploited within 31 days versus roughly 194 in 2025; and of 1,061 vulnerabilities attributed to AI-assisted discovery, 14 (1.3%) confirmed exploited in the wild. Note that "known exploitation" is bounded by observation window and detection coverage, and is not the same as first exploitation. [vulncheck.com](https://www.vulncheck.com/blog/state-of-exploitation-1h-2026)
[^dbir]: Verizon 2026 Data Breach Investigations Report, as reported by [SecurityWeek](https://www.securityweek.com/verizon-dbir-2026-vulnerability-exploitation-overtakes-credential-theft-as-top-breach-vector/): "The median time for full patching increased to 43 days in 2025, up from 32 days in the previous year," and organisations "patched only 26% of the security defects in CISA's Known Exploited Vulnerabilities (KEV) catalog last year, a drop from 38% in 2024." Note for anyone chasing the numbers: the widely quoted "edge devices and VPNs went from 3% to 22%" figure belongs to the *2025* DBIR, not this one, and pairs with the older 32-day median — don't weld the two editions together.
[^glasswing]: "Project Glasswing: An initial update," Anthropic — approximately 50 partners with early access to Claude Mythos Preview, and more than ten thousand high- or critical-severity findings across widely used software in the first month. [anthropic.com](https://www.anthropic.com/research/glasswing-initial-update)
[^mythos]: "Claude Mythos Preview," Anthropic: the model "fully autonomously identified and then exploited a 17-year-old remote code execution vulnerability in FreeBSD that allows anyone to gain root on a machine running NFS" — CVE-2026-4747, in the RPCSEC_GSS authentication path of the NFS *server*. [anthropic.com](https://www.anthropic.com/research/mythos-preview)
[^msft]: "Evolving Windows vulnerability management to meet the speed of AI-powered discovery," Windows Experience Blog, 9 July 2026 — names Microsoft Security's multi-model agentic scanning harness (MDASH) and states that "as AI helps defenders discover more issues, customers will see a higher volume of security updates included in each security release." [blogs.windows.com](https://blogs.windows.com/windowsexperience/2026/07/09/evolving-windows-vulnerability-management-to-meet-the-speed-of-ai-powered-discovery/)
