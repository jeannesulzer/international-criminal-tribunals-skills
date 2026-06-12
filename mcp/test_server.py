"""Smoke tests for the International Justice MCP server.

These exercise the pure logic (discovery, detection, path-safety, search,
verification routing) without standing up an MCP transport. Run with:

    cd mcp && python -m pytest test_server.py     # if pytest is installed
    cd mcp && python test_server.py               # plain-stdlib fallback
"""

from __future__ import annotations

import server


def test_tribunals_discovered():
    assert "icc" in server.TRIBUNALS
    assert "icty-ictr-irmct" in server.TRIBUNALS
    # The repo ships fourteen tribunal folders.
    assert len(server.TRIBUNALS) >= 13
    icc = server.TRIBUNALS["icc"]
    assert icc.name == "icc"
    assert "International Criminal Court" in icc.description


def test_detection_routes_known_schemes():
    assert server.detect_tribunals("ICC-01/05-01/08-3343")[0][0] == "icc"
    assert server.detect_tribunals("Prosecutor v. Krstić IT-98-33-T")[0][0] == "icty-ictr-irmct"
    assert server.detect_tribunals("Case 002/02")[0][0] == "eccc"
    assert server.detect_tribunals("STL-11-01")[0][0] == "stl"
    assert server.detect_tribunals("SCSL-03-01")[0][0] == "scsl-rscsl"
    assert server.detect_tribunals("KSC-BC-2020-06")[0][0] == "ksc"
    assert server.detect_tribunals("Hissène Habré reparations")[0][0] == "eac-habre"
    assert server.detect_tribunals("a grocery list") == []


def test_path_safety_rejects_traversal():
    icc = server.TRIBUNALS["icc"]
    assert server._safe_md_path(icc, "../../CLAUDE.md") is None
    assert server._safe_md_path(icc, "/etc/passwd") is None
    assert server._safe_md_path(icc, "SKILL.md") is not None
    # Bare reference-name shorthand resolves into references/.
    p = server._safe_md_path(icc, "citation-format")
    assert p is not None and p.name == "citation-format.md"


def test_get_skill_file_returns_content():
    out = server.get_skill_file("icc", "SKILL.md")
    assert "Core discipline" in out
    out2 = server.get_skill_file("icc", "authoritative-sources")
    assert "Tier 1" in out2


def test_search_finds_known_holding():
    out = server.search_jurisprudence("command responsibility", tribunal="icc")
    assert "match" in out.lower()
    # Scoped search only looks in jurisprudence maps.
    out2 = server.search_jurisprudence("genocide", scope="jurisprudence", max_results=5)
    assert "jurisprudence-map.md" in out2 or "No matches" in out2


def test_verify_citation_routes_and_includes_workflow():
    out = server.verify_citation("ICC-01/05-01/08-3343")
    assert "icc" in out
    assert "fallback ladder" in out.lower()
    assert "Verification posture" in out
    # Explicit override path.
    out2 = server.verify_citation("some reference", tribunal="eccc")
    assert "eccc" in out2


def test_infer_tribunal_from_url():
    assert server._infer_tribunal_from_url("https://www.icc-cpi.int/cases") == "icc"
    assert server._infer_tribunal_from_url("https://www.irmct.org/x") == "icty-ictr-irmct"
    assert server._infer_tribunal_from_url("https://example.com") == ""


def test_foundational_texts():
    out = server.get_foundational_texts("icc")
    assert "Rome Statute" in out
    assert "ONLY exception" in out
    assert "Unknown tribunal" in server.get_foundational_texts("not-a-tribunal")


def test_pdf_extraction_handles_garbage():
    # Non-PDF bytes should be reported as unparseable, not crash.
    out = server._extract_pdf_text("https://x/doc.pdf", b"not a real pdf", "application/pdf")
    assert "doc.pdf" in out
    assert ("could not parse" in out or "No extractable text" in out
            or "pypdf` is not installed" in out)


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failures = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {fn.__name__}: {exc}")
    print(f"\n{len(fns) - failures}/{len(fns)} passed")
    return failures


if __name__ == "__main__":
    raise SystemExit(1 if _run_all() else 0)
