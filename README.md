# International Criminal Tribunals — Claude Skills

A suite of [Claude Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) for research, drafting, and analysis involving international criminal tribunals. Each skill enforces a **verification-first** methodology: no citation appears in an output until it has been verified against an authoritative primary source.

## Skills in this suite

| Skill | Status | Scope |
|---|---|---|
| [`icc/`](./icc) | v1.1 | International Criminal Court (Rome Statute system) |

Future tribunals (ICTY, ICTR, MICT, SCSL, STL, ECCC, KSC, IIIM, IIMM, UNITAD, hybrid mechanisms) will be added one at a time as separate skills, with the same methodology and structure.

## Methodology

1. **Verification-first.** Every case-law, decision, filing, warrant, or statement citation is verified via `web_fetch` to an authoritative source in the conversation where it is produced. Foundational treaty texts may be cited from project knowledge when present. Nothing else may be cited from memory.
2. **One tribunal at a time.** Each skill matures before the next begins.
3. **Standard structure.** Every skill follows the same layout:
   - `SKILL.md` — entry point, core discipline, workflow
   - `references/` — source hierarchy, citation format, verification workflow, foundational texts
   - `examples/` — worked workflows on representative tasks
4. **Authoritative sources only** for primary citations; secondary sources are clearly labelled in outputs.

## Repository layout

```
international-criminal-tribunals-skills/
├── README.md
├── icc/
│   ├── SKILL.md
│   ├── CHANGELOG.md
│   └── references/
│       ├── authoritative-sources.md
│       ├── citation-format.md
│       ├── verification-workflow.md
│       ├── foundational-texts.md
│       ├── example-verification.md
│       └── example-audit.md
└── [future tribunal skills]/
```

## Installation

Each skill folder is a self-contained Claude Skill. To use:
- Upload the folder to a Claude Project, or
- Install as a user-level Skill (see Anthropic's [skills documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)).

The foundational treaty texts (Rome Statute, Elements of Crimes, Rules of Procedure and Evidence, Regulations of the Court) are not bundled in this repository — they are ICC publications, freely available on icc-cpi.int. Add them to a Project alongside the skill if you want them cited directly without a `web_fetch`.

## What these skills are not

- **Not legal advice.** Outputs are research and drafting aids for users who themselves understand international criminal law.
- **Not a substitute for primary documents.** A skill that follows the verification workflow can produce accurate citations and disciplined drafts; only the user can decide what to do with them.
- **Not endorsed by any tribunal.** This is an independent open-source project.

## Contributing

Issues, error reports, and corrections are welcome. Please open an issue with the specific citation, output, and source URL involved.

## License

[To be determined by maintainer — recommend permissive open-source license, e.g. MIT or Apache-2.0.]

