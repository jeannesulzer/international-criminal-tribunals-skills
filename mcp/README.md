# International Justice MCP

A [Model Context Protocol](https://modelcontextprotocol.io) server that
exposes the `international-criminal-tribunals-skills` suite to any MCP client
(Claude Desktop, Claude Code, or another host).

It reads the tribunal skill folders in this repository live — it does not
duplicate their content — and surfaces four capability areas that map onto the
suite's verification-first methodology:

| Area | Tool / resource |
|---|---|
| Expose the skills | `list_tribunals`, `get_skill_file`, `get_foundational_texts`, `skill://…` resources |
| Verify citations | `verify_citation` |
| Search the case law | `search_jurisprudence` |
| Retrieve documents | `fetch_document` (with PDF text extraction) |

The server never authorises citing case law from memory. `verify_citation`
returns the *guidance* to verify a citation against a Tier 1 source; it does
not assert correctness. `fetch_document` honours the suite's fallback ladder
when an authoritative domain blocks a direct fetch (e.g. icc-cpi.int 403s).

## Tools

### `list_tribunals()`
Lists every tribunal skill with its slug and a short description. Call it
first to discover slugs (`icc`, `icty-ictr-irmct`, `eccc`, `nuremberg-tokyo`,
`scsl-rscsl`, `stl`, `ksc`, `cps-rca`, `jep`, `special-panels-timor-leste`,
`eac-habre`, `reg-64-kosovo`, `wcc-bih`).

### `get_skill_file(tribunal, file="SKILL.md")`
Returns the full text of a skill file. `file` accepts `SKILL.md`, a reference
path (`references/citation-format.md`), a bare reference name
(`citation-format`, `authoritative-sources`, `verification-workflow`,
`foundational-texts`, `jurisprudence-map`), or an example.

### `search_jurisprudence(query, tribunal="", scope="all", max_results=20)`
Full-text search across the skills' case-law and reference content.
Space-separated terms are ANDed. `scope` is one of `all`, `jurisprudence`,
`citation`, `sources`, `examples`, `skill`. Results are documentation
pointers — still verify before citing.

### `get_foundational_texts(tribunal)`
Returns the tribunal's `foundational-texts.md` — the constitutive instruments
(statute, rules, regulations) that are the *only* texts citable from project
knowledge without a fresh fetch, plus the amendment/revision discipline and
what is explicitly not foundational.

### `verify_citation(citation, tribunal="")`
Detects the tribunal from a raw citation (number scheme + key terms) and
returns, for that tribunal, the citation-format rules, the authoritative-source
hierarchy, and the verification workflow (including the fallback ladder). Pass
`tribunal` to override detection.

### `fetch_document(url, tribunal="")`
Fetches a primary source over HTTP with a browser-like User-Agent. On a 403 /
block it returns the relevant fallback ladder rather than failing. PDFs have
their text extracted (via `pypdf`); scanned/image-only PDFs are reported as
not machine-readable rather than returning empty output.

## Resources

Every skill markdown file is available as a resource at
`skill://<slug>/<relative-path>`, e.g. `skill://icc/SKILL.md` or
`skill://eccc/references/citation-format.md`.

## Running

Requires Python ≥ 3.10.

```bash
cd mcp
pip install -e .          # or: pip install "mcp[cli]>=1.2.0" httpx
python server.py          # runs over stdio
```

### Register with Claude Code

```bash
claude mcp add international-justice -- python /absolute/path/to/mcp/server.py
```

### Register with Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "international-justice": {
      "command": "python",
      "args": ["/absolute/path/to/mcp/server.py"]
    }
  }
}
```

The server resolves the repository root as the parent of `mcp/`, so it must
stay inside this repository to read the skill folders.

## Design notes

- **Documentation-grounded.** Tribunal folders are discovered at startup by
  scanning for `SKILL.md` and parsing its frontmatter, so adding a new
  tribunal folder to the repo makes it available with no code change.
- **Verification-first preserved.** No tool produces a citation; tools route
  to, search, or retrieve authoritative material and consistently remind the
  caller to verify.
- **Path-safe.** File access is constrained to within a tribunal folder;
  traversal outside the repo is rejected.
