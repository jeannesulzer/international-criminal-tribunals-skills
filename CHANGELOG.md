# Changelog — International Criminal Tribunals skill suite

All notable changes to the repository as a whole are recorded here. Each skill
also keeps its own `CHANGELOG.md` for changes internal to that skill. This file
tracks suite-level changes: skills added or removed, repository-wide
documentation, and the methodology statement.

The format follows [Keep a Changelog](https://keepachangelog.com/), and the
project aims to follow semantic versioning at the suite level.

## [Unreleased]

### Added
- `mcp/` — a Model Context Protocol server exposing the suite to MCP-capable
  clients (Claude Desktop, Claude Code). Six tools: list the tribunals, read
  any skill file, fetch a tribunal's foundational texts, verify a citation
  (with tribunal auto-detection), search the jurisprudence, and retrieve a
  primary-source document (PDF text extraction and fallback-ladder handling),
  plus `skill://` resources. Discovers tribunals dynamically from the folder
  layout and preserves the verification-first discipline — no tool produces a
  citation from memory. Python, with a stdlib-runnable smoke-test suite.
- Four new skills: `special-panels-timor-leste/` (Special Panels for Serious
  Crimes, Dili District Court), `eac-habre/` (Extraordinary African Chambers,
  Habré case), `reg-64-kosovo/` (UNMIK Regulation 64 Panels), and `wcc-bih/`
  (War Crimes Chamber of the Court of Bosnia and Herzegovina) — bringing the
  suite to thirteen skills covering sixteen jurisdictions.
- `METHODOLOGY.md` — the selection methodology: the five cumulative criteria
  for including a jurisdiction, the doctrinal taxonomies, the application table
  for all sixteen jurisdictions, and the specific inclusion discussions.
- `LICENSE` — Creative Commons Attribution 4.0 International (CC BY 4.0).
- `docs/expert-review/` — one-page practitioner review sheet per skill.
- `INSTALL.md` — a plain-language walkthrough of the three ways to use the
  suite with Claude (a project, the Skills upload, the MCP server), written
  after user reports that the developer-oriented instructions were hard to
  follow.

### Changed
- `mcp/README.md`: added an "Installation for non-developers (Claude
  Desktop)" section — six steps, plus the warning that the local server
  registers through Settings → Developer, not Settings → Connectors (the
  mistake an installation report showed users actually make).
- Rewrote `README.md` for publication under the Impact Litigation Lab framing.
- Softened the JEP skill's claim that retrieval to jep.gov.co "succeeds
  reliably" to acknowledge that direct fetch can fail and that the fallback
  ladder is load-bearing.

## [0.1.0] — earlier

### Added
- Initial nine skills: `icc/`, `eccc/`, `nuremberg-tokyo/`,
  `icty-ictr-irmct/`, `scsl-rscsl/`, `stl/`, `ksc/`, `cps-rca/`, `jep/`, each
  following the standard seven-file backbone (SKILL.md, CHANGELOG.md, four to
  five reference files, two worked examples).
