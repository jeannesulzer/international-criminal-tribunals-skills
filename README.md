# International Criminal Tribunals — Claude Skills

A suite of [Claude Skills](https://docs.claude.com/en/docs/build-with-claude/skills) for research, drafting, and analysis involving international criminal tribunals. Each skill teaches Claude a **verification-first** methodology: no case-law citation appears in an output until it has been verified against an authoritative primary source in the conversation that produced it.

Nine skills span the major international military tribunals, the UN ad hoc tribunals and their residual mechanism, and a range of hybrid and transitional-justice courts — from Nuremberg and Tokyo to the ICC, the Kosovo Specialist Chambers, and Colombia's Special Jurisdiction for Peace.

## Skills in this suite

| Skill | Version | Scope |
|---|---|---|
| [`icc/`](./icc/) | v1.1.1 | International Criminal Court (Rome Statute system) |
| [`eccc/`](./eccc/) | v1.2.1 | Extraordinary Chambers in the Courts of Cambodia (Khmer Rouge Tribunal) |
| [`nuremberg-tokyo/`](./nuremberg-tokyo/) | v1.0 | Post-WWII international military tribunals (IMT at Nuremberg, the twelve subsequent NMT trials under Control Council Law No. 10, and the IMTFE at Tokyo) |
| [`icty-ictr-irmct/`](./icty-ictr-irmct/) | v1.0 | UN ad hoc tribunals and their residual mechanism (ICTY, ICTR, and the IRMCT / Mechanism) |
| [`scsl-rscsl/`](./scsl-rscsl/) | v1.0 | Special Court for Sierra Leone and its Residual Special Court (SCSL / RSCSL) |
| [`stl/`](./stl/) | v1.0 | Special Tribunal for Lebanon (STL / TSL) |
| [`ksc/`](./ksc/) | v1.0 | Kosovo Specialist Chambers and Specialist Prosecutor's Office (KSC / SPO) |
| [`cps-rca/`](./cps-rca/) | v1.0 | Special Criminal Court of the Central African Republic (Cour Pénale Spéciale, CPS) |
| [`jep/`](./jep/) | v1.0.1 | Special Jurisdiction for Peace, Colombia (Jurisdicción Especial para la Paz, JEP) |


## Methodology

1. **Verification-first.** Every case-law, decision, filing, warrant, or statement citation is verified via `web_fetch` to an authoritative source in the conversation where it is produced. Foundational treaty texts may be cited from project knowledge when present. Nothing else may be cited from memory.
2. **One tribunal at a time.** Each skill matures before the next begins.
3. **Standard structure.** Every skill follows the same layout:
   - `SKILL.md` — entry point, core discipline, workflow
   - `references/` — source hierarchy, citation format, verification workflow, foundational texts (and any tribunal-specific references such as a jurisprudence map or case-documents quick reference)
   - `examples/` — worked end-to-end examples of the methodology
4. **Authoritative sources only** for primary citations; secondary sources are clearly labelled in outputs.

## Repository layout

​```
international-criminal-tribunals-skills/
├── README.md
├── CLAUDE.md
├── icc/
│   ├── SKILL.md
│   ├── CHANGELOG.md
│   ├── references/
│   │   ├── authoritative-sources.md
│   │   ├── citation-format.md
│   │   ├── verification-workflow.md
│   │   └── foundational-texts.md
│   └── examples/
│       ├── example-verification.md
│       └── example-audit.md
├── eccc/
│   ├── SKILL.md
│   ├── CHANGELOG.md
│   ├── references/
│   │   ├── authoritative-sources.md
│   │   ├── citation-format.md
│   │   ├── case-documents-quick-reference.md
│   │   ├── verification-workflow.md
│   │   ├── foundational-texts.md
│   │   └── jurisprudence-map.md
│   └── examples/
│       ├── example-verification.md
│       └── example-audit.md
├── nuremberg-tokyo/
│   ├── SKILL.md
│   ├── CHANGELOG.md
│   ├── references/
│   │   ├── authoritative-sources.md
│   │   ├── citation-format.md
│   │   ├── verification-workflow.md
│   │   ├── foundational-texts.md
│   │   ├── jurisprudence-map.md
│   │   └── defendants-and-judges.md
│   └── examples/
│       ├── example-verification.md
│       └── example-audit.md
├── icty-ictr-irmct/
│   ├── SKILL.md
│   ├── CHANGELOG.md
│   ├── references/
│   │   ├── authoritative-sources.md
│   │   ├── citation-format.md
│   │   ├── verification-workflow.md
│   │   ├── foundational-texts.md
│   │   └── jurisprudence-map.md
│   └── examples/
│       ├── example-verification.md
│       └── example-audit.md
├── scsl-rscsl/          # same standard layout (SKILL.md, CHANGELOG.md,
├── stl/                 # references/{authoritative-sources, citation-format,
├── ksc/                 # verification-workflow, foundational-texts,
├── cps-rca/             # jurisprudence-map}, examples/{verification, audit})
├── jep/
├── docs/
│   └── expert-review/    # one-page practitioner review sheet per skill
└── [future tribunal skills]/
​```

## Using a skill

Each folder is a self-contained Claude Skill. There are two ways to use one, and the difference matters:

- **As an installed Skill (recommended).** Install the folder as a Skill (see Anthropic's [Agent Skills documentation](https://docs.claude.com/en/docs/build-with-claude/skills)). Claude then loads it automatically, triggered by the `SKILL.md` frontmatter, whenever the relevant tribunal comes up.
- **As Project knowledge.** Upload the folder (or its zip) to a Claude Project. Claude reads the files as reference documents and will follow them when asked, but they are not auto-triggered the way an installed Skill is — so prompt Claude to use the skill explicitly.

The foundational treaty texts (e.g. Rome Statute, ECCC Law, UN-Cambodia Agreement, Internal Rules) are not bundled here — they are publicly available on the respective Court websites. Add them to a Project alongside the relevant skill if you want them cited directly without a `web_fetch`.

## Documentation

`docs/expert-review/` holds a one-page review sheet per skill — load-bearing facts, dates, case numbers, citation conventions, and the "traps" each skill guards against — intended for a quick practitioner sanity-check.

## What these skills are not

- **Not legal advice.** Outputs are research and drafting aids for users who themselves understand international criminal law.
- **Not a substitute for primary documents.** A skill that follows the verification workflow can produce accurate citations and disciplined drafts; only the user can decide what to do with them.
- **Not endorsed by any tribunal.** This is an independent open-source project.

## Contributing

Issues, error reports, and corrections are welcome. Please open an issue with the specific citation, output, and source URL involved.

## Author

[Jeanne Sulzer](https://impactlitigation.fr) — International human rights lawyer (Paris Bar & ICC list of counsel), Founding Partner at [Impact Litigation](https://impactlitigation.fr), Lecturer at Sciences Po (Law & PSIA) and Paris II Panthéon-Assas, Head of the International Justice Commission at Amnesty France.

## How to cite

> Jeanne Sulzer, *International Criminal Tribunals — Claude Skills* (open-source skill suite), 2026, https://github.com/jeannesulzer/international-criminal-tribunals-skills.

## License

This work is licensed under a [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You are free to share and adapt the material for any purpose, including commercially, provided you give appropriate credit. See the [`LICENSE`](./LICENSE) file for the full text.
