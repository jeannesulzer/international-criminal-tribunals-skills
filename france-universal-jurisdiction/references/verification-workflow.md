# Verification workflow — France, universal jurisdiction

The operational procedure. It differs from the tribunal skills in one respect:
the **realistic ceiling is often lower**, because first-instance *cour
d'assises* judgments are frequently non-public. Honesty about the level reached
*is* the discipline.

## Step 0 — Identify the document
Pin down, before anything else:
- the **forum** — which *cour d'assises* (Paris? appeal? another seat?), the
  *chambre de l'instruction*, or the **Cour de cassation**;
- the **procedural posture** — investigation / trial / appeal / *cassation*;
- the **accused**, as named in the public record (respect anonymisation);
- the **jurisdictional basis** — 689-2 (torture/CAT, presence) vs 689-11
  (genocide/CAH/war crimes) vs the Rwanda statute vs a personality-based head.
  Getting this wrong is the most consequential error.

## Step 1 — List the citations
Statute (with the version date that applies) + each decision the output relies
on, with the proposition each supports.

## Step 2 — Verify (fallback ladder)
1. **Légifrance / Judilibre** — statute (versioned `LEGIARTI`) and any Cour de
   cassation decision (`JURITEXT` / ECLI).
2. **Official court or prosecutor record** — the assises verdict announcement,
   the PNAT communiqué, the *acte d'accusation* summary.
3. **Tier-2 tracker** — TRIAL/UJAR, ICD-Asser, Civitas Maxima, FIDH, HRW, ECCHR
   — for existence + content, **labelled as secondary**.
4. **Stop and state the ceiling** if the full judgment is not public.
5. **Ask the user** if a higher level is needed (and whether they can supply the
   judgment).

## Step 3 — Match the verification level
- **Existence** — court, date, accused, outcome confirmed.
- **Content** — what was held/found.
- **Paragraph / page** — the exact passage against the text.

For assises judgments, **"existence + official account"** is a legitimate
stopping point. Say so explicitly; never imply paragraph-level verification of a
judgment you have not read.

## Step 4 — Draft
Assert only what was verified. State the jurisdictional basis. Mark the level.

## Step 5 — Self-audit
- Is the **jurisdictional basis** correct and stated (689-2 / 689-11 / Rwanda
  statute / personality)?
- Is every statute citation the **version in force** at the relevant date?
- Is any **anonymised** person re-identified? (Must be no.)
- Is the conviction **final**, **under appeal**, or **revised on appeal**?
- Has any **opinion tribunal** (Kuala Lumpur/Perdana, Russell, PPT) crept in as
  if it were a court? (Must be no.)

## The anonymisation rule (hard)
French published international-crimes judgments are frequently anonymised for
data-protection reasons. **Never reconstruct or infer** the identity of an
anonymised accused, victim, or witness. Cite persons exactly as the public
record presents them. Where the official record names a person (e.g. Simbikangwa,
Kunti Kamara, where widely and officially reported), follow that record.

## The language rule
French controls. Verify against the French text; if you rely on an English
summary (HRW, JusticeInfo, Civitas Maxima), say so and treat the content level
as dependent on that translation until the French text is checked.

## Direct-fetch note
Légifrance and courdecassation.fr are generally reachable and reliable. Some
official court pages and the PNAT site can be slow or return errors; when a
direct fetch fails, that is structural — work the ladder (Tier-2 trackers carry
most assises outcomes) rather than treating failure as fatal.

---

## Reading the source document directly (the top of the ladder)

The most reliable verification is reading the **actual document**, not a
website's search snippet. Put this above everything else — and it matters more
here than for any other skill, because first-instance *cour d'assises*
judgments are frequently non-public:

**Rung 0 — work from the document itself when it is available.** Official
French court portals can be slow or unavailable, and most assises judgments are
not published at all. The two ways to reach the text anyway:

- **The user supplies it** — an uploaded PDF or pasted pages (a judgment, an
  *arrêt* of the Cour de cassation, an *acte d'accusation*) can be read
  directly, reaching paragraph-level verification. A practitioner on the matter
  usually already holds it; ask for it.
- **A retrieval tool reads it** — where a document-retrieval tool or MCP server
  is available (Légifrance/Judilibre for statute and Cour de cassation; a
  fetch-and-extract tool for a PDF), prefer it over a raw fetch.

Only when the document cannot be obtained do you fall back to the ladder above
— and then you state the ceiling honestly (for assises judgments, often
"existence + official/Tier-2 account").

## Site-search results are leads, not content

A result from a site-search index — or a "synthesis" of search snippets —
establishes at most that something **exists**. It is **never** content- or
paragraph-level verification. Treat it as a lead to confirm against the
document, and label it as such. Two recurring traps:

- **Transliteration / OCR garbling.** Names and acronyms get corrupted
  (foreign names transliterated into French, diacritics dropped). A name or
  acronym that appears only once in a snippet is a red flag — do not assert it.
- **Relational claims.** Who is whose subordinate, superior, co-perpetrator, or
  *complice* is the detail a synthesis most often inverts. Never assert a
  relationship — or a jurisdictional basis — from a snippet; it requires the
  document.
