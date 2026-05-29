# CLAUDE.md

Guidance for AI assistants working on **this repository** — i.e. editing the
skill content, not following the skill methodology to do legal research. (For
the latter, read `verification-workflow.md` and use it.)

## What this repo is

A documentation-only suite of [Claude
Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
for research, drafting, and analysis involving international criminal
tribunals. Each skill teaches Claude a **verification-first** methodology:
every case-law citation in an output must be verified against an authoritative
primary source in the conversation that produces it.

There is no code, no build system, no tests, no package manifest. Everything
is Markdown. Edits are content edits.

## Layout

```
README.md
CLAUDE.md
icc/
├── SKILL.md          # entry point; core discipline, when-to-use, workflow, hard rules
├── CHANGELOG.md
├── references/
│   ├── authoritative-sources.md
│   ├── citation-format.md
│   ├── verification-workflow.md
│   └── foundational-texts.md
└── examples/
    ├── example-verification.md
    └── example-audit.md
eccc/
├── SKILL.md
├── CHANGELOG.md
├── references/
│   ├── authoritative-sources.md
│   ├── citation-format.md
│   ├── case-documents-quick-reference.md
│   ├── verification-workflow.md
│   ├── foundational-texts.md
│   └── jurisprudence-map.md
└── examples/
    ├── example-verification.md
    └── example-audit.md
nuremberg-tokyo/
├── SKILL.md
├── CHANGELOG.md
├── references/
│   ├── authoritative-sources.md
│   ├── citation-format.md
│   ├── verification-workflow.md
│   ├── foundational-texts.md
│   ├── jurisprudence-map.md
│   └── defendants-and-judges.md
└── examples/
    ├── example-verification.md
    └── example-audit.md
icty-ictr-irmct/
├── SKILL.md
├── CHANGELOG.md
├── references/
│   ├── authoritative-sources.md
│   ├── citation-format.md
│   ├── verification-workflow.md
│   ├── foundational-texts.md
│   └── jurisprudence-map.md
└── examples/
    ├── example-verification.md
    └── example-audit.md
scsl-rscsl/   ┐ each of these five follows the same standard layout:
stl/          │ SKILL.md, CHANGELOG.md,
ksc/          │ references/{authoritative-sources, citation-format,
cps-rca/      │ verification-workflow, foundational-texts, jurisprudence-map},
jep/          ┘ examples/{example-verification, example-audit}
```

Each tribunal folder is a self-contained Claude Skill: `SKILL.md` is the entry
point and the rest is referenced from it. The seven-file backbone
(`SKILL.md`, `CHANGELOG.md`, the four standard references, two examples) is
common across tribunals; tribunal-specific reference files are added
alongside (e.g. ECCC has `case-documents-quick-reference.md` and
`jurisprudence-map.md`).

## File map

- `README.md` — public-facing description of the skill suite and methodology.
- `CLAUDE.md` — this file; guidance for AI assistants editing the repo.

### ICC skill

- `icc/SKILL.md` — entry point. Frontmatter (`name`, `description`), the core
  discipline, when to use the skill, the workflow summary, pointers to
  references and examples, and the five hard rules.
- `icc/CHANGELOG.md` — version history for the ICC skill.
- `icc/references/authoritative-sources.md` — the source hierarchy: Tier 1
  (icc-cpi.int, legal-tools.org, asp.icc-cpi.int), Tier 2 (NGOs, UN bodies,
  academic, news), and "do not cite". Includes the fallback ladder for
  icc-cpi.int 403s.
- `icc/references/citation-format.md` — exact citation formats for the Rome
  Statute, EoC, RPE, Regulations, decisions, warrants, OTP statements, ASP
  documents. The Article 28 shorthand-vs-Statute discussion lives here.
- `icc/references/verification-workflow.md` — the operational procedure:
  three-level verification gradient (Existence / Content / Paragraph), the
  fallback ladder, the standard workflow (identify → list → verify → draft →
  self-audit), and a worked Bemba example.
- `icc/references/foundational-texts.md` — the four texts citable from
  project knowledge without `web_fetch` (Rome Statute, EoC, RPE,
  Regulations), and what is *not* foundational.
- `icc/examples/example-verification.md` — worked end-to-end examples:
  level-C full verification (Bemba effective control) and level-B partial
  verification (Ntaganda 2017 jurisdiction).
- `icc/examples/example-audit.md` — two audit modes: auditing a working
  draft vs. auditing a finalised Court record. The distinction matters;
  mixing them produces unhelpful output.

### ECCC skill

- `eccc/SKILL.md` — entry point. Frontmatter, the verification-first
  discipline, the standard workflow, the four cases (001 / 002 with the
  002/01–002/02 severance / 003 / 004), pointers to references and examples,
  the sensitive-contexts note, and the hard rules.
- `eccc/CHANGELOG.md` — version history (semver, Keep-a-Changelog style).
- `eccc/references/authoritative-sources.md` — Tier 1 (eccc.gov.kh, the
  ECCC Archive, the two-volume *Guide to the ECCC*, Practice Directions,
  legal-tools.org), Tier 2 (OHCHR Cambodia, the *Annotated Cambodian Code of
  Criminal Procedure*, Cambodia Tribunal Monitor, DC-Cam, Ciorciari &
  Heindel, Jørgensen, academic journals), and "never authoritative". Khmer
  text controls for Cambodian-law components.
- `eccc/references/citation-format.md` — Case File Number anatomy
  (`[Case]/[Date]/ECCC/[Body]`), document-number letter-prefix table
  (A/B/C/D/E/F), severance handling (Case 002 / 002/01 / 002/02), the
  accused-name convention (SURNAME in capitals first), Internal Rules
  revision discipline, and the canonical "Frequently cited authorities"
  table reproduced from the *Guide Vol. 2*.
- `eccc/references/case-documents-quick-reference.md` — quick lookup table
  of the principal documents per Case, with status notes (severed
  proceedings, deceased accused, residual phase, terminated cases).
- `eccc/references/verification-workflow.md` — fallback ladder
  (eccc.gov.kh → legal-tools.org → OHCHR/UN Rule of Law → Tier 2
  summarisation → ask the user), partial-verification handling, language
  and redaction discipline.
- `eccc/references/foundational-texts.md` — the three foundational
  instruments (UN-Cambodia Agreement 2003 plus the Addendum 2021; ECCC Law
  as amended; Internal Rules with a revisions × dates table). Explains the
  "new" suffix on amended ECCC Law articles and the JCE caveat.
- `eccc/references/jurisprudence-map.md` — topic-by-topic map of the
  ECCC's principal holdings, mirroring the eight chapters of the *Guide
  Vol. 2*. Particularly developed for Civil Party reparations,
  JCE (including JCE III caveats), and genocide against the Cham and
  Vietnamese.
- `eccc/examples/example-verification.md` — single citation verified end
  to end (Case 002/02 genocide against the Cham, E465).
- `eccc/examples/example-audit.md` — two audit modes paralleling the ICC
  skill: working draft (citations are claims to be verified) vs. finalised
  Court record (the audit task shifts to downstream-reliance inventory).

### Nuremberg + Tokyo skill

A single integrated skill covering three post-WWII tribunals: the
International Military Tribunal at Nuremberg (IMT, 1945-46), the twelve
subsequent US Nuremberg Military Tribunals under Control Council Law
No. 10 (NMT, 1946-49), and the International Military Tribunal for the
Far East at Tokyo (IMTFE, 1946-48). One folder, three institutions.

- `nuremberg-tokyo/SKILL.md` — entry point. Frontmatter, the
  verification-first discipline, the gradient (Existence / Content /
  Page or volume), the standard workflow, the institutional
  architecture (IMT vs NMT vs IMTFE), the source hierarchy, the five
  citation modes, audit mode, substantive-doctrine pointers, and the
  sensitive-contexts note.
- `nuremberg-tokyo/CHANGELOG.md` — version history for the skill.
- `nuremberg-tokyo/references/authoritative-sources.md` — Tier 1 (the
  three official records — Blue Series, Green Series, Pritchard-Zaide
  volumes — plus the digital archives: Avalon, Harvard Nuremberg Trials
  Project, Stanford Taube Archive, UVA IMTFE Collection, ICC Legal
  Tools, JACAR, UN Audiovisual Library; institutional repositories and
  specialised university collections), Tier 2 (Nuremberg Academy,
  USHMM, academic commentary on both Nuremberg and Tokyo), and "never
  authoritative". Includes the languages-and-translations note.
- `nuremberg-tokyo/references/citation-format.md` — the five citation
  modes (Charter/Statute provisions, IMT Judgment via Blue Series or
  Oxford ICL, NMT cases via Green Series, IMTFE Judgment via
  Pritchard-Zaide with mandatory majority-vs-separate-opinion
  identification, Nuremberg Principles), plus the 22 IMT and 28 IMTFE
  defendant tables and the 11 IMTFE judges.
- `nuremberg-tokyo/references/verification-workflow.md` — separate
  fallback ladders for IMT/NMT and for IMTFE citations, the
  verification-level gradient, **the four classic traps** (IMT vs NMT;
  Nuremberg vs Tokyo; Charter terminology — Art. 6(a)(b)(c) vs Class
  A/B/C; majority Judgment vs separate opinions), and translation
  discipline.
- `nuremberg-tokyo/references/foundational-texts.md` — the instruments
  citable from project knowledge: the London Agreement and IMT Charter,
  Control Council Law No. 10, MacArthur's Special Proclamation and the
  Tokyo Charter, UNGA Resolutions 95(I) and 177(II), and the ILC 1950
  Nuremberg Principles.
- `nuremberg-tokyo/references/jurisprudence-map.md` — fourteen
  topic-by-topic sections mapping doctrine across IMT, NMT, and IMTFE
  (legality / *nullum crimen*, crimes against peace, war crimes, crimes
  against humanity with the armed-conflict-nexus divergence, criminal
  organisations, individual responsibility, no immunity, superior
  orders, conspiracy, command responsibility, the Hirohito
  non-indictment, the Pal dissent, the Nuremberg Principles, the twelve
  NMT cases).
- `nuremberg-tokyo/references/defendants-and-judges.md` — the
  tribunal-specific reference: 22 IMT defendants with German spellings,
  positions and sentences; the four IMT counts; the criminal-organisation
  findings; 28 IMTFE defendants with positions and sentences; the
  Hirohito non-indictment; Class A/B/C; the 11 IMTFE judges with their
  separate opinions; the chief prosecutors.
- `nuremberg-tokyo/examples/example-verification.md` — one Nuremberg
  citation (the "men, not abstract entities" passage of the IMT
  Judgment) and one Tokyo citation (the Pal dissent on aggressive war),
  verified end to end.
- `nuremberg-tokyo/examples/example-audit.md` — three audits, each
  illustrating one of the classic traps (IMT/NMT confusion via the
  Einsatzgruppen Case; Nuremberg/Tokyo Charter article-number confusion;
  the Pal dissent attributed to "the Tribunal").

The accused-name convention is tribunal-specific here too: IMT
defendants keep their German spellings (Göring, Seyß-Inquart, Heß);
IMTFE defendants keep the macrons in romanised Japanese (Tōjō, Tōgō,
Mutō), and the skill flags that the Pritchard-Zaide and JACAR
romanisations differ. The four classic traps are the Nuremberg + Tokyo
analogue of the ICC Article 28 shorthand discipline and the ECCC
severance discipline — keep them intact if you touch this skill.

### ICTY + ICTR + IRMCT skill

A single integrated skill covering the two UN ad hoc tribunals and their
residual mechanism: the International Criminal Tribunal for the former
Yugoslavia (ICTY, 1993-2017), the International Criminal Tribunal for
Rwanda (ICTR, 1994-2015), and the International Residual Mechanism for
Criminal Tribunals (IRMCT / MICT / "the Mechanism", 2010– ). They are
one skill because the Mechanism continues both tribunals' functions,
hosts their archives, and decided the late appeals under MICT numbers.

- `icty-ictr-irmct/SKILL.md` — entry point. Frontmatter, the
  verification-first discipline, the gradient (Existence / Content /
  Paragraph), the standard workflow, the institutional architecture
  (ICTY vs ICTR vs Mechanism, with the Transitional-Arrangements
  competence rule), the source hierarchy, the citation-format overview,
  audit mode, substantive-doctrine pointers, and the protective-measures
  note.
- `icty-ictr-irmct/CHANGELOG.md` — version history for the skill.
- `icty-ictr-irmct/references/authoritative-sources.md` — Tier 1
  (irmct.org, the Case Law Database `cld.irmct.org`, the Unified Court
  Records `ucr.irmct.org`, the legacy `icty.org` and
  `unictr.irmct.org`, and legal-tools.org), Tier 2 (UN documents,
  academic commentary, trial-monitoring/NGO archives, Refworld), and
  "never authoritative". Includes the confidential/redacted-document
  note.
- `icty-ictr-irmct/references/citation-format.md` — the case-number
  anatomy (`IT-` / `ICTR-` / `MICT-`), the phase suffixes
  (`-T`, `-A`, `-AR72`, `-S`, `-R`, `-ES`), the party-designation and
  diacritics conventions, the IT/ICTR → MICT transition for appeals
  (Karadžić, Mladić), and a canonical table of frequently cited
  authorities with verified case numbers and dates.
- `icty-ictr-irmct/references/verification-workflow.md` — the fallback
  ladder (irmct.org / case page → CLD → UCR → legacy sites →
  legal-tools.org → labelled secondary → ask the user), verification-
  level matching, the hard protective-measures rule (never identify a
  protected witness; prefer public redacted versions), and the
  English/French language note.
- `icty-ictr-irmct/references/foundational-texts.md` — the three
  Statutes (ICTY: SC Res. 827, 1993; ICTR: SC Res. 955, 1994; IRMCT:
  SC Res. 1966, 2010, with the Transitional Arrangements), the three
  Rules of Procedure and Evidence with the revision-in-force discipline,
  and the competence rule that explains the IT/MICT split.
- `icty-ictr-irmct/references/jurisprudence-map.md` — topic-by-topic map
  of the landmark holdings: jurisdiction (Tadić AR72), genocide
  (Akayesu, Krstić, Karadžić, Mladić), incitement (Akayesu, the Media
  case), crimes against humanity (Tadić, Kunarac), JCE (Tadić Appeal),
  command responsibility (Čelebići, Blaškić), torture (Furundžija),
  sexual violence (Akayesu, Kunarac, Furundžija), senior-leadership
  guilty plea (Kambanda), and the residual/fugitive function (Kabuga).
- `icty-ictr-irmct/examples/example-verification.md` — the Krstić /
  Srebrenica-genocide citation verified end to end, with the
  trial-vs-appeal distinction.
- `icty-ictr-irmct/examples/example-audit.md` — a working-draft audit
  (the Tadić JCE date/chamber error and the Akayesu/JCE III
  mischaracterisation) and a final-record audit (the Mladić Appeal
  Judgment and the IT/MICT pairing).

The tribunal-specific disciplines to keep intact here are the
IT/ICTR/MICT case-number distinction (the same accused may carry an IT
or ICTR trial number and a later MICT appeal number — e.g. Karadžić
IT-95-5/18 then MICT-13-55, Mladić IT-09-92 then MICT-13-56) and the
protective-measures rule. These are this skill's analogue of the ICC
Article 28 discipline and the ECCC severance discipline.

### SCSL + RSCSL skill

`scsl-rscsl/` — the Special Court for Sierra Leone (2002-2013) and the
Residual Special Court for Sierra Leone (since 2 December 2013). Standard
seven-file backbone. Established by the UN-Sierra Leone Agreement of
16 January 2002 pursuant to SC Res. 1315 (2000). Case-number form is
`SCSL-[NN]-[NN]` (the docket also uses a four-digit-year long form such
as `SCSL-2003-01` — the skill standardises on the short form). The four
principal cases: Taylor (`SCSL-03-01`), CDF/Norman-Fofana-Kondewa
(`SCSL-04-14`), RUF/Sesay-Kallon-Gbao (`SCSL-04-15`), AFRC/Brima-Kamara-Kanu
(`SCSL-04-16`). The disciplines to keep intact: the SCSL's landmark
holdings (first conviction for child-soldier recruitment; forced marriage
as an "other inhumane act" crime against humanity; the Taylor immunity
decision against a sitting head of State), the SCSL/RSCSL institutional
split, and the no-life-imprisonment penalty regime (fixed terms only).

### STL skill

`stl/` — the Special Tribunal for Lebanon (2007-2023). Standard
seven-file backbone. Established by SC Res. 1757 (2007); seat at
Leidschendam. Unique features the skill must preserve: it applied
**Lebanese criminal law**, allowed **trials in absentia**, and was the
first international tribunal to treat **terrorism** as a discrete crime
(the 16 February 2011 Appeals Chamber Interlocutory Decision). Main case
*Ayyash et al.* (`STL-11-01`), Trial Judgment 18 August 2020. The
discipline trap to keep intact: the two contempt cases are
`STL-14-05` = New TV S.A.L. & Al-Khayat (Al Jadeed) and
`STL-14-06` = Akhbar Beirut S.A.L. & Al-Amin — easily swapped, so the
mapping is stated explicitly.

### KSC skill

`ksc/` — the Kosovo Specialist Chambers and Specialist Prosecutor's
Office (The Hague, applying Kosovo law). Standard seven-file backbone.
Founded on Law No. 05/L-053 (2015) and Article 162 / Amendment 24 of the
Kosovo Constitution; mandate rooted in the Marty Report (PACE Doc. 12462,
2011). Case-number form `KSC-BC-[YYYY]-[NN]` (trial) and `KSC-CA-...`
(appeal). Key cases: Thaçi et al. (`KSC-BC-2020-06`), Mustafa
(`KSC-BC-2020-05`), Shala (`KSC-BC-2020-04`), Gucati and Haradinaj
(`KSC-BC-2020-07`). Keep appeal case numbers verified against scp-ks.org
before citing — the registry stem does not always track the trial number.

### CPS (Central African Republic) skill

`cps-rca/` — the Cour Pénale Spéciale, a hybrid national/international
court inside the CAR judicial system (seat Bangui). Standard seven-file
backbone, written in a French/English register. Founding instrument:
Loi organique n°15.003 of 3 June 2015; RPP is Loi 18.010. The flagship
matter is the **Affaire Paoua** (Koundjili/Lemouna massacre): Trial
Judgment 31 October 2022, Appeal 20 July 2023. Disciplines to keep intact:
the statutory "**notamment**" in Art. 3 (the crime list may be
illustrative, not exhaustive), the French-language-controls point, and
ICC complementarity. Note cpsrca.cf and related sites 403 on direct fetch.

### JEP (Colombia) skill

`jep/` — the Jurisdicción Especial para la Paz, the judicial component of
Colombia's transitional-justice system (SIVJRNR) from the 2016 Peace
Agreement. Standard seven-file backbone, in a Spanish/English register —
Spanish-language versions of documents control. Legal basis: Acto
Legislativo 01 de 2017, Ley 1957 de 2019, Ley 1922 de 2018. The
load-bearing things to keep right are the eleven **macrocaso** numbers and
themes (Caso 01 = FARC kidnappings; Caso 03 = "falsos positivos"; etc.),
the restorative **sanciones propias** (max 8 years) and **TOAR**, and the
two first restorative sentences of September 2025 (Caso 01, 16 Sept;
Caso 03, 18 Sept). Use the peso sign (`$`/COP), not other currency symbols.

## House style for edits

Read a few existing files before drafting new content — the prose style is
deliberate and consistent across both skills.

- **Conversational but disciplined.** Sentences explain *why* a rule exists,
  not just *what* it is. Example: "The reason: ICC document numbers are
  exact, paragraph numbers are exact, and the cost of an invented citation in
  real work … is high."
- **British English** throughout (`labelled`, `recognise`, `summarise`).
- **No emoji.** No marketing language. No "let's" / "we'll".
- **Tables for source tiers and verification levels**; bullets for ladders
  and checklists; prose for reasoning.
- **Inline code** for document numbers, URLs, file paths, and exact
  citation strings: `ICC-01/05-01/08-3343`, `-Red`, `Article 28(1)`.
- **Bold for the operative verb** in a procedural step (`**Step 0 —
  Identify the document.**`).
- **Worked examples are concrete.** Real case names, real document numbers,
  real paragraph behaviour. Don't introduce hypothetical "Case X" examples —
  every example in the repo today uses a real matter (ICC: Bemba, Ntaganda,
  Lubanga, Katanga, Abd-Al-Rahman; ECCC: Duch, NUON Chea, KHIEU Samphan,
  Cases 002/01 and 002/02).
- **Accused-name convention is tribunal-specific.** ICC uses Western
  first-last (Bemba, Ntaganda). ECCC uses the Cambodian SURNAME-first
  convention in capitals (NUON Chea, KHIEU Samphan, KAING Guek Eav alias
  Duch). Don't normalise across tribunals.

## Substantive constraints

These are not stylistic — they are the methodology the skills exist to
enforce. Edits that weaken them are bugs.

1. **Verification-first is non-negotiable.** Do not introduce text that
   permits citing case law from memory. The foundational texts per
   tribunal (ICC: Rome Statute, EoC, RPE, Regulations; ECCC: UN-Cambodia
   Agreement plus Addendum, ECCC Law as amended, Internal Rules) are the
   only exception, and only when present in project knowledge.
2. **Gradient verification is the realistic posture.** Existence /
   Content / Paragraph levels are core. Don't simplify them away into
   "verified or not".
3. **Direct-fetch failures are structural.** ICC: icc-cpi.int 403s.
   ECCC: eccc.gov.kh latency, partial PDFs, Khmer-only versions. Any new
   content that touches retrieval must respect this and offer the
   fallback ladder rather than treating failure as fatal.
4. **Instrument numbering wins over practitioner shorthand.** ICC:
   Article 28(1)/(2) vs. "28(a)/(b)" (see `icc/references/citation-format.md`).
   ECCC: ECCC Law `Article 29 new` rather than `Article 29`; Internal
   Rules revision stated explicitly (see `eccc/references/citation-format.md`).
   Keep these sections intact if you touch them.
5. **Public-redacted only.** ICC `-Conf` / `-Conf-Exp` and ECCC
   `-Confidential` / `-Strictly Confidential` filings are not citable
   from a public output, ever. Don't add carve-outs.
6. **Not legal advice.** Outputs are research aids. Don't add language that
   reads as advice to a putative end-user.
7. **ECCC-specific: language and sensitive contexts.** Khmer-language
   versions control for the Cambodian-law components; flag dependence on
   English translations rather than masking it. Use the Court's own
   language for the crimes against the Cham and the Vietnamese, the S-21
   killings, forced marriage and gender-based violence, and the
   approximately 1.7–2.2 million deaths during Democratic Kampuchea.
   Don't soften and don't sensationalise.

## Adding a new tribunal

The README anticipates skills for ICTY, ICTR, MICT, SCSL, STL, KSC, IIIM,
IIMM, UNITAD, and hybrid mechanisms, plus regional human rights courts
(ECtHR, IACtHR, ACtHPR). One folder per tribunal, mirroring the existing
layout:

```
[tribunal]/
├── SKILL.md
├── CHANGELOG.md
├── references/
│   ├── authoritative-sources.md
│   ├── citation-format.md
│   ├── verification-workflow.md
│   ├── foundational-texts.md
│   └── [tribunal-specific references, if any]
└── examples/
    ├── example-verification.md
    └── example-audit.md
```

When adding tribunal-specific content, mirror this structure and adapt —
don't invent a different layout per tribunal. Things that vary by tribunal:
the document numbering scheme, the foundational instruments (statute,
RPE/equivalent, regulations/equivalent), the chamber names, the
authoritative-source domains, the fallback ladder when direct fetch fails.
The methodology — verification-first, three-level gradient, public-redacted
only — is constant across tribunals and should not be re-litigated per
folder.

Tribunal-specific reference files are welcome alongside the four standard
references when the tribunal's practice warrants them (see ECCC's
`case-documents-quick-reference.md` and `jurisprudence-map.md`). They sit
in `references/`, not in their own folder.

## Git workflow

- Work on a topic branch, not on `main`. Suggested naming:
  `claude/<short-topic>-<short-suffix>` (matches earlier branches such as
  `claude/claude-md-docs-jPc89` and `claude/eccc-fixes-r9Yx2`). Don't
  push to `main` without explicit instruction.
- Commits should be small and descriptive. Match the existing log style
  (sentence-case summary, focus on *what changed and why*).
- No pre-commit hooks. No CI. No tests to run. Verification is editorial.
- Don't create a pull request unless the user asks for one.

## What to do when an instruction is unclear

The most common ambiguity is **"fix the citations in this draft"** — that's
a request to *apply* the relevant skill's methodology, not a request to
edit the repo. If the user wants the skill itself improved, that's an edit
to `icc/` or `eccc/` (references, examples, or SKILL.md). If they want
their own draft cleaned up, that's a separate session that uses the
skill, not edits to it. Clarify before changing repo files.

The second most common ambiguity is **which tribunal**. ECCC documents
look superficially similar to ICC documents (case caption, chamber, document
number, paragraph) but the schemes are different. If the user names a case
without naming a tribunal, identify the tribunal before applying a citation
format — Bemba is ICC; Duch and Cases 002/01 / 002/02 are ECCC.
