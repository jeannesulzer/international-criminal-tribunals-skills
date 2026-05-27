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

## Current state vs. README-described layout

The `README.md` describes a per-tribunal subdirectory layout:

```
icc/
├── SKILL.md
├── CHANGELOG.md
└── references/
    ├── authoritative-sources.md
    ├── citation-format.md
    ├── verification-workflow.md
    ├── foundational-texts.md
    ├── example-verification.md
    └── example-audit.md
```

What actually exists at the repo root, today:

```
README.md
authoritative-sources.md
citation-format.md
verification-workflow.md
foundational-texts.md
example-verification.md
example-audit.md
```

The `icc/SKILL.md`, `icc/CHANGELOG.md`, and `icc/references/` wrapper are not
on disk. The seven Markdown files at the root are the ICC skill content that
the README expects to find inside `icc/references/` (and the two `example-*`
files belong in `icc/examples/` per the README's narrative, though the README
itself groups them under `references/`).

When the user asks you to add content, ask whether they want it placed at the
root (current state) or moved into the `icc/` layout the README describes. Do
not silently reorganise — the discrepancy is real and the user may have a
reason for the current layout (e.g. mid-migration, or the README is what's
out of date).

## File map

- `README.md` — public-facing description of the skill suite, methodology, and
  intended layout.
- `authoritative-sources.md` — the source hierarchy: Tier 1 (icc-cpi.int,
  legal-tools.org, asp.icc-cpi.int), Tier 2 (NGOs, UN bodies, academic, news),
  and "do not cite". Includes the fallback ladder for icc-cpi.int 403s.
- `citation-format.md` — exact citation formats for the Rome Statute, EoC,
  RPE, Regulations, decisions, warrants, OTP statements, ASP documents. The
  Article 28 shorthand-vs-Statute discussion lives here.
- `verification-workflow.md` — the operational procedure: three-level
  verification gradient (Existence / Content / Paragraph), the fallback
  ladder, the standard workflow (identify → list → verify → draft →
  self-audit), and a worked Bemba example.
- `foundational-texts.md` — the four texts citable from project knowledge
  without `web_fetch` (Rome Statute, EoC, RPE, Regulations), and what is *not*
  foundational.
- `example-verification.md` — worked end-to-end examples: level-C full
  verification (Bemba effective control) and level-B partial verification
  (Ntaganda 2017 jurisdiction).
- `example-audit.md` — two audit modes: auditing a working draft vs. auditing
  a finalised Court record. The distinction matters; mixing them produces
  unhelpful output.

## House style for edits

Read a few existing files before drafting new content — the prose style is
deliberate and consistent across the seven files.

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
  every example in the repo today uses a real ICC matter (Bemba, Ntaganda,
  Lubanga, Katanga, Abd-Al-Rahman).

## Substantive constraints

These are not stylistic — they are the methodology the skills exist to
enforce. Edits that weaken them are bugs.

1. **Verification-first is non-negotiable.** Do not introduce text that
   permits citing case law from memory. The four foundational texts (Rome
   Statute, EoC, RPE, Regulations) are the only exception, and only when
   present in project knowledge.
2. **Gradient verification is the realistic posture.** Existence /
   Content / Paragraph levels are core. Don't simplify them away into
   "verified or not".
3. **icc-cpi.int 403s are structural.** Any new content that touches
   retrieval must respect that direct fetches fail unpredictably and offer
   the fallback ladder rather than treating failure as fatal.
4. **Statute numbering wins over practitioner shorthand.** Especially
   Article 28(1)/(2) vs. "28(a)/(b)". See `citation-format.md` for the
   reasoning — keep that section intact if you touch it.
5. **Public-redacted only.** Confidential filings (`-Conf`, `-Conf-Exp`)
   are not citable from a public output, ever. Don't add carve-outs.
6. **Not legal advice.** Outputs are research aids. Don't add language that
   reads as advice to a putative end-user.

## Adding a new tribunal

The README anticipates skills for ICTY, ICTR, MICT, SCSL, STL, ECCC, KSC,
IIIM, IIMM, UNITAD, and hybrid mechanisms. The intended pattern (per the
README) is one folder per tribunal:

```
[tribunal]/
├── SKILL.md
├── CHANGELOG.md
└── references/
    ├── authoritative-sources.md
    ├── citation-format.md
    ├── verification-workflow.md
    ├── foundational-texts.md
    └── examples/
        ├── example-verification.md
        └── example-audit.md
```

Until the existing ICC content is moved into `icc/`, adding a second tribunal
folder will produce an inconsistent repo. Surface that to the user before
creating the second folder; offer to migrate ICC first.

When adding tribunal-specific content, mirror the seven-file structure and
adapt — don't invent a different layout per tribunal. Constants per tribunal:
the document numbering scheme, the foundational instruments (statute,
RPE/equivalent, regulations/equivalent), the chamber names, the
authoritative-source domains, the fallback ladder when direct fetch fails.

## Git workflow

- Active branch for this work: `claude/claude-md-docs-jPc89`. Develop, commit,
  and push there. Don't push to `main` without explicit instruction.
- Commits should be small and descriptive. Match the existing log style
  (sentence-case summary, focus on *what changed and why*).
- No pre-commit hooks. No CI. No tests to run. Verification is editorial.
- Don't create a pull request unless the user asks for one.

## What to do when an instruction is unclear

The most common ambiguity will be **"add X to the skill"** — root files or
`icc/`? Ask. The second most common will be **"fix the citations in this
draft"** — that's a request to apply the methodology, not a request to edit
this repo; clarify before changing repo files.
