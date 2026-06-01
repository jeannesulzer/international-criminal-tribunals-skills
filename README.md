# Open Source Skills for International Criminal Law Research

**A library of verification-first methodologies for AI-assisted research on 16 international and internationalised criminal jurisdictions.**

Hosted by [Impact Litigation Lab](https://impactlitigation.fr) — French nonprofit (association loi 1901, in formation).

---

## What this is

This repository hosts a library of **Skills** for Claude AI (Anthropic) covering 16 international and internationalised criminal jurisdictions, from the Nuremberg International Military Tribunal (1945) to Colombia's Jurisdicción Especial para la Paz (first sentences September 2025).

Each skill encodes a **verification-first discipline**: no case-law citation, indictment, decision, or judgment reference appears in any output without being verified against an authoritative source (the official tribunal website, the ICC Legal Tools Database, or other Tier 1 institutional sources). The skills are designed to make AI-assisted research in international criminal law **rigorous, reproducible, and reliable** — for students, practitioners, NGOs, journalists, and researchers.

Skills are an open standard adopted by Anthropic in October 2025 and are portable across major AI platforms (Claude, ChatGPT, Cursor, Gemini).

---

## Jurisdictions covered

The 16 jurisdictions are organised by structural and historical category:

### Post-1945 heritage
- **Nuremberg–Tokyo** — International Military Tribunal (IMT, 1945–1946), the twelve Nuremberg Military Tribunals (NMT, 1946–1949), and the International Military Tribunal for the Far East (IMTFE, 1946–1948)

### Ad hoc UN tribunals
- **ICTY** — International Criminal Tribunal for the former Yugoslavia (1993–2017)
- **ICTR** — International Criminal Tribunal for Rwanda (1994–2015)
- **IRMCT** — International Residual Mechanism for Criminal Tribunals (since 2010/2012)

### Permanent international jurisdiction
- **ICC** — International Criminal Court (since 2002)

### Hybrid tribunals (2000s–2010s)
- **ECCC** — Extraordinary Chambers in the Courts of Cambodia (2003–2022)
- **SCSL / RSCSL** — Special Court for Sierra Leone (2002–2013) and its Residual Special Court (since 2013)
- **STL** — Special Tribunal for Lebanon (2007–2023)

### Internationalised national chambers and hybrid courts
- **Special Panels Timor-Leste** — Special Panels for Serious Crimes (UNTAET, 2000–2006)
- **Reg. 64 Kosovo Panels** — UNMIK Regulation 64 Panels (2000–2008)
- **WCC-BiH** — War Crimes Chamber of the Court of Bosnia and Herzegovina (since 2005)
- **EAC** — Chambres Africaines Extraordinaires (Hissène Habré case, 2013–2017)

### Modern hybrid and transitional jurisdictions
- **KSC** — Kosovo Specialist Chambers and Specialist Prosecutor's Office (since 2015)
- **CPS-RCA** — Cour Pénale Spéciale de la République Centrafricaine (since 2015, operational since 2018)
- **JEP** — Jurisdicción Especial para la Paz, Colombia (since 2017, first sentences September 2025)

---

## Selection methodology

The selection of these 16 jurisdictions — and the deliberate exclusion of others — follows **five cumulative criteria**:

1. **Jurisdiction over international crimes** — competence over crimes against humanity, genocide, war crimes, aggression, or crimes defined by reference to these categories
2. **Structuring international or internationalised element** — international legal basis, international component in composition, or substantial application of international law
3. **Temporally and materially bounded competence** — specific conflict, regime, or set of events
4. **Structured public documentation** — judgments and decisions available in an official archive
5. **Substantial doctrinal contribution to international criminal law** — innovation, precedent, or institutional experience of broader relevance

The full methodological document — including discussion of borderline cases (the JEP, the CPS-RCA, the EAC Habré) and jurisdictions deliberately not yet included (national universal-jurisdiction prosecutions, truth and reconciliation commissions) — is available in **[METHODOLOGY.md](METHODOLOGY.md)**.

---

## Repository structure

Each skill is a self-contained directory:

```
[jurisdiction]/
├── SKILL.md                       — main entry point and discipline
├── CHANGELOG.md                   — version history
├── references/
│   ├── foundational-texts.md      — statutes, agreements, rules of procedure
│   ├── authoritative-sources.md   — Tier 1 and Tier 2 source hierarchy
│   ├── citation-format.md         — citation conventions and worked examples
│   ├── verification-workflow.md   — fallback ladder and jurisdiction-specific traps
│   └── jurisprudence-map.md       — topical map of principal holdings
└── examples/
    ├── example-verification.md    — verifying one citation end to end
    └── example-audit.md           — auditing user-supplied documents
```

---

## Methodological principles

Every skill in this library shares the same architecture:

- **Step 0 — Identify the document.** Before anything else, the skill distinguishes the case, the chamber, the document type, and the procedural posture.
- **Three-tier verification gradient.** Existence verified / content verified / paragraph verified — the output never claims a higher level than was actually achieved.
- **Source hierarchy.** Tier 1 (official tribunal websites, ICC Legal Tools, institutional archives) is authoritative; Tier 2 (academic commentary, trial monitoring NGOs, quality journalism) is labelled when used; nothing else is authoritative.
- **Jurisdiction-specific traps.** Each skill maps 5 to 7 recurrent errors specific to that jurisdiction (for example: confusing the Trial Chamber with the Appeals Chamber, misattributing a doctrine to the wrong decision, conflating connected cases).
- **Audit mode.** A distinct workflow for auditing user-supplied documents — useful for reviewing student work, briefs, or research notes.

---

## Working languages

The library covers three working languages:

- **English** — for ICC, ICTY/ICTR/IRMCT, ECCC, SCSL/RSCSL, STL, KSC, Special Panels Timor-Leste, Reg. 64 Kosovo, WCC-BiH, IMT/NMT/IMTFE
- **French** — for CPS-RCA (the procedural language of the court)
- **Spanish** — for JEP (the procedural language of the court)

Additional languages will be added when relevant: the EAC Habré skill (currently in development) will be bilingual French/English.

---

## How to use a skill

Each skill is designed to be used with Claude AI either:

- **As a project knowledge file** — upload the relevant directory or `.zip` into a Claude project, then ask your question
- **As a system prompt module** — extract the `SKILL.md` content and use it as part of a system prompt for your AI assistant
- **As a research methodology reference** — read the markdown files directly; they are designed to be useful even without an AI assistant

A worked example for each skill is provided in `examples/example-verification.md`.

---

## Roadmap

Currently in development:

- **Universal jurisdiction (France)** — in collaboration with Zacharie Laik (Legal Data Hunter)
- **Universal jurisdiction (Germany)** — Generalbundesanwalt practice
- **Updated treatment of proposed and emerging jurisdictions** — Special Tribunal for the Crime of Aggression against Ukraine, when operational

Suggestions, contributions, and proposals for new skills are welcome via GitHub Issues.

---

## Contributing

Contributions are welcome — corrections, additions, translations, new skills. The contribution workflow:

1. Open a GitHub Issue describing the proposed change
2. For corrections to existing skills: include the verified Tier 1 source supporting the correction
3. For new skills: confirm in the Issue that the proposed jurisdiction satisfies the five criteria in [METHODOLOGY.md](METHODOLOGY.md)
4. Submit a Pull Request

All skills are licensed under a permissive open source licence (see `LICENSE`).

---

## About Impact Litigation Lab

**Impact Litigation Lab** is a French nonprofit (association loi 1901, in formation) hosted under [impactlitigation.fr](https://impactlitigation.fr). Its mission is to develop open source methodologies and tools at the intersection of international criminal law, victims' rights, and artificial intelligence — for the benefit of students, practitioners, NGOs, journalists, and researchers worldwide.

This library is the inaugural project of Impact Litigation Lab.

---

## Acknowledgements

This library is the product of collective work. Particular thanks to the practitioners, scholars, and colleagues who reviewed, tested, and challenged earlier drafts. Errors and omissions remain my own.

---

## About the author

**Jeanne Sulzer** is an international human rights lawyer admitted to the Paris Bar and on the List of Counsel of the International Criminal Court. She is Head of the International Justice Commission at Amnesty International France, lectures at Sciences Po Paris School of International Affairs (PSIA) and at Université Paris-Panthéon-Assas, and previously served at the Extraordinary Chambers in the Courts of Cambodia (Civil Party Lead Co-Lawyers' Section and Office of the Co-Investigating Judges, 2008–2013).

---

## Citation

If you use this library in academic work, please cite as:

> Jeanne Sulzer, *Open Source Skills for International Criminal Law Research*, Impact Litigation Lab, 2026. Available at: github.com/jeannesulzer

---

*Impact Litigation Lab — June 2026*
*[impactlitigation.fr](https://impactlitigation.fr) · [github.com/jeannesulzer](https://github.com/jeannesulzer)*
