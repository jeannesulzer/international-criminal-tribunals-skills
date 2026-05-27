# International Criminal Tribunals — Claude Skills

A suite of [Claude Skills](https://docs.claude.com/en/docs/build-with-claude/skills) for research, drafting, and analysis involving international criminal tribunals. Each skill enforces a **verification-first** methodology: no citation appears in an output until it has been verified against an authoritative primary source.

## Skills in this suite

| Skill | Status | Scope |
|---|---|---|
| [`icc/`](./icc/) | v1.1 | International Criminal Court (Rome Statute system) |
| [`eccc/`](./eccc/) | v1.2 | Extraordinary Chambers in the Courts of Cambodia (Khmer Rouge Tribunal) |

Future tribunals (ICTY, ICTR, MICT, SCSL, STL, KSC, IIIM, IIMM, UNITAD, hybrid mechanisms) and regional human rights courts (ECtHR, IACtHR, ACtHPR) will be added one at a time as separate skills, with the same methodology and structure.

## Methodology

1. **Verification-first.** Every case-law, decision, filing, warrant, or statement citation is verified via `web_fetch` to an authoritative source in the conversation where it is produced. Foundational treaty texts may be cited from project knowledge when present. Nothing else may be cited from memory.
2. **One tribunal at a time.** Each skill matures before the next begins.
3. **Standard structure.** Every skill follows the same layout:
   - `SKILL.md` — entry point, core discipline, workflow
   - `references/` — source hierarchy, citation format, verification workflow, foundational texts, jurisprudence map, examples
4. **Authoritative sources only** for primary citations; secondary sources are clearly labelled in outputs.

## Repository layout
