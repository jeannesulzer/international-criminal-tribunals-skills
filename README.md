# Skills for International Justice

**An open-source library of 13 skills for AI-assisted research in international criminal law.**

Built by [Jeanne Sulzer](https://www.linkedin.com/in/jeannesulzer/) — Avocate au Barreau de Paris, ICC List of Counsel, Founding Partner of [Impact Litigation](https://www.impactlitigation.fr/), Head of the Legal Commission of Amnesty International France, Lecturer at Sciences Po Paris (PSIA) and Université Paris II Panthéon-Assas.

This project provides a curated library of Claude skills covering 16 international and internationalised jurisdictions that have shaped international criminal law, from Nuremberg (1945) to Colombia's JEP (first judgments September 2025).

---

## What this is

A library of 13 skills, each encoding the doctrinal map, source hierarchy, and verification workflow for one or more international jurisdictions. The skills do not contain scraped data. They encode a methodology that instructs Claude to consult the tribunals' own official archives — judgments, decisions, indictments — before producing any citation.

---

## The 13 skills

| # | Skill | Jurisdictions covered | Official source |
|---|---|---|---|
| 1 | **ICC** | International Criminal Court | [icc-cpi.int](https://www.icc-cpi.int) |
| 2 | **ECCC** | Extraordinary Chambers in the Courts of Cambodia | [eccc.gov.kh](https://www.eccc.gov.kh) |
| 3 | **ICTY / ICTR / IRMCT** | ICTY, ICTR, and International Residual Mechanism | [irmct.org](https://www.irmct.org) |
| 4 | **Nuremberg / Tokyo** | IMT (Nuremberg, 1945–46) and IMTFE (Tokyo, 1946–48) | [legal-tools.org](https://www.legal-tools.org) |
| 5 | **STL** | Special Tribunal for Lebanon | [stl-tsl.org](https://www.stl-tsl.org) / [legal-tools.org](https://www.legal-tools.org) |
| 6 | **KSC** | Kosovo Specialist Chambers | [scp-ks.org](https://www.scp-ks.org) |
| 7 | **SCSL / RSCSL** | Special Court for Sierra Leone and its Residual Mechanism | [rscsl.org](https://www.rscsl.org) |
| 8 | **CPS-RCA** | Cour Pénale Spéciale (Central African Republic) | [cpsrca.cf](https://www.cpsrca.cf) |
| 9 | **JEP** | Jurisdicción Especial para la Paz (Colombia) | [jep.gov.co](https://www.jep.gov.co) |
| 10 | **EAC (Habré)** | Extraordinary African Chambers, Hissein Habré case | [legal-tools.org](https://www.legal-tools.org) |
| 11 | **WCC-BiH** | War Crimes Chamber, Court of Bosnia and Herzegovina | [sudbih.gov.ba](https://www.sudbih.gov.ba) |
| 12 | **Special Panels Timor-Leste** | UNTAET Serious Crimes Panels (Dili District Court) | [legal-tools.org](https://www.legal-tools.org) |
| 13 | **Reg. 64 Kosovo** | UNMIK Regulation 64 Panels (Kosovo district courts) | [legal-tools.org](https://www.legal-tools.org) |

**Total: 13 skills, 16 jurisdictions.** Two skills are composite: ICTY/ICTR/IRMCT covers three jurisdictions, and Nuremberg/Tokyo covers two (the IMT and the IMTFE).

---

## How to install and use

Installation requires no coding.

1. **Download** the skill matching the jurisdiction you are working on from this repository.
2. **Drop it** into a [Claude project](https://claude.ai) as a knowledge document. Each skill is a `.zip` archive containing a `SKILL.md` file and reference materials.
3. **Ask your question** in a conversation within that project. Claude reads the instructions encoded in the skill, consults the tribunal's official archives to verify any reference, and produces an answer grounded in verified sources.

A skill, once uploaded, persists across all conversations within the project. You can upload multiple skills to the same project if you are working across several jurisdictions.

---

## Also available: an MCP server

For users working in an MCP-capable client (Claude Desktop, Claude Code), the repository also ships a [Model Context Protocol](https://modelcontextprotocol.io) server in [`mcp/`](mcp/). Where the skills above are dropped into a Claude project as knowledge documents, the MCP server exposes the same suite as tools the model can call directly — the same verification-first discipline, made available programmatically.

It provides six tools: list the tribunals, read any skill file, fetch a tribunal's foundational texts, verify a citation (the server detects the tribunal from the citation and returns its authoritative sources and verification workflow), search the jurisprudence, and retrieve a primary-source document (with PDF text extraction, and the fallback ladder when an official site blocks a direct fetch). No tool produces a citation from memory.

The server reads the skill folders live, so it always reflects the current content of the suite. Setup and client-registration instructions are in [`mcp/README.md`](mcp/README.md). This is an optional, advanced path — using the skills requires no coding at all.

---

## Methodology: verification-first

Each skill encodes a non-negotiable requirement: **no case-law citation is produced without having been verified against the official archives**.

Each skill contains:
- A `SKILL.md` file with the methodological instructions
- Five reference files: `foundational-texts.md`, `authoritative-sources.md`, `citation-format.md`, `verification-workflow.md`, `jurisprudence-map.md`
- Two pedagogical example files
- A `CHANGELOG.md`

The skills themselves do not contain pre-stored case-law data. They contain methodological instructions and pointers to the official archives that the tribunals publish for public consultation. Judicial transparency is constitutive of our field: judgments are made public to enable analysis, critique, and the construction of international law.

---

## Next steps

A planned next step is to explore the transposition of this methodology to domain-specific small language models (SLMs) and local Retrieval-Augmented Generation (RAG) architectures. The discipline will remain, the tools will evolve.

Contributions from practitioners, NGOs, researchers, national jurisdictions, and developers interested in SLMs and RAG are welcome.

---

## On the structural concerns raised by generative AI

I am fully aware of the structural concerns raised by generative AI today. The report *[Unlawful by Design: Exposing the Human Rights Costs of Generative AI](https://www.amnesty.org/en/documents/pol40/0996/2026/en/)* (POL 40/0996/2026, May 2026) published by Amnesty International anchors its analysis in international human rights law and documents the issues of mass data collection, structural biases, and disproportionate environmental impact of standalone generative AI systems, with respect to the protections guaranteed in particular by the International Covenant on Civil and Political Rights, the International Convention on the Elimination of All Forms of Racial Discrimination, and the Convention on the Rights of the Child.

This report deserves to be read in full by everyone practising in our field.

---

## License

This project is released under the **Creative Commons Attribution 4.0 International licence (CC BY 4.0)**. You are free to share and adapt the material, including commercially, provided you give appropriate credit. See the [`LICENSE`](LICENSE) file for details.

---

## Contributing

Issues, pull requests, and discussions are welcome. Suggested contributions include:
- Additional skills for jurisdictions not yet covered
- Translations of skill documentation
- Improvements to the verification workflow
- Experimentation with SLM and RAG transposition

Contact: through [LinkedIn](https://www.linkedin.com/in/jeannesulzer/) or via the Issues tab on this repository.

---

## Citation

If you use these skills in research or practice, please cite as:

> Sulzer, Jeanne. *Skills for International Justice — An Open-Source Library for AI-Assisted Research in International Criminal Law.* Impact Litigation Lab, 2026. github.com/jeannesulzer

---

© 2026 Jeanne Sulzer / Impact Litigation Lab. Released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).
