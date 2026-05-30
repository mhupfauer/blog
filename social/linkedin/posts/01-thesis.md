# 01 · Thesis post

Lead atom. Lands the contrarian sentence and the two-question test. Link to the post goes in the first comment, not in the body.

Recommended slot: Tuesday ≈ 08:30 CET (EN) / Thursday ≈ 08:30 CET (DE).

---

## English

> Most enterprise agents in production have already lost the auditability claim. The role model, the permission docs, the incident-response plan — fiction along with it.
>
> Two questions every hop an agent makes has to answer: *whose* authority is being exercised, and *which* agent exercised it. Keep both and you have something you can authorize and audit. Lose either — and most have lost at least one — and "we have agent identity" is a slide, not a control.
>
> The user disappears behind an app-only token, or a service account. The agent disappears behind a platform-wide client id that forty other agents share. The authorization disappears the moment data is copied out of the system that knew the ACLs into one that doesn't. Three places to drop the principal. Three matching gaps in the audit table.
>
> Here is the part regulated shops should worry about more than any jailbreak: the property that fails the auditor on a quiet Tuesday is the same one that fails the incident bridge during an outage. If your authoritative logs cannot show *whose* authority and *which* agent for any action — along with what it was authorized to do and what it actually did downstream — you do not have agent authentication. You have a shared account with an LLM bolted onto it.
>
> Full version below. Wrote it for the people who actually build this, with two audio cuts — a Boardroom cut (~10 min) for governance, a Bench cut (~12 min) for engineering — in English and German.
>
> #AgenticAI #IdentityAccessManagement #Cybersecurity

**First comment:** https://hupfauer.one/posts/which-agent-bricked-prod/

---

## Deutsch

> Die meisten Enterprise-Agenten in Produktion haben den Auditability-Anspruch bereits verloren. Das Rollenmodell, die Berechtigungsdoku, der Incident-Response-Plan — Fiktion gleich mit.
>
> Jeder Hop, den ein Agent macht, muss zwei Fragen beantworten: *Wessen* Autorität wird ausgeübt — und *welcher* Agent hat sie ausgeübt? Beides erhalten, und es gibt etwas, das man autorisieren und auditieren kann. Eines davon verloren — und die meisten haben mindestens eines verloren — und "wir haben Agent Identity" ist ein Slide, kein Control.
>
> Der User verschwindet hinter einem App-Only-Token oder einem Service-Account. Der Agent verschwindet hinter einer plattformweiten Client-ID, die vierzig andere Agenten teilen. Die Autorisierung verschwindet in dem Moment, in dem Daten aus dem System mit den ACLs in ein System ohne kopiert werden. Drei Stellen, an denen das Principal kippt. Drei passende Lücken in der Audit-Tabelle.
>
> Der Teil, über den sich regulierte Häuser mehr Sorgen machen sollten als über jeden Jailbreak: Die Eigenschaft, die an einem ruhigen Dienstag den Auditor scheitern lässt, ist dieselbe, die während eines Incidents die Bridge scheitern lässt. Wenn deine autoritativen Logs für eine beliebige Aktion nicht zeigen können, *wessen* Autorität und *welcher* Agent — zusammen mit dem, was autorisiert war und was downstream tatsächlich passiert ist — dann hast du keine Agent Authentication. Du hast einen Shared Account mit einem LLM angeflanscht.
>
> Volle Version unten. Geschrieben für die Leute, die das Zeug tatsächlich bauen. Zwei Audio-Cuts: Boardroom-Cut (~10 min) für Governance, Bench-Cut (~12–14 min) für Engineering — auf Englisch und Deutsch.
>
> #AgenticAI #IAM #Informationssicherheit

**Erster Kommentar:** https://hupfauer.one/posts/which-agent-bricked-prod/
