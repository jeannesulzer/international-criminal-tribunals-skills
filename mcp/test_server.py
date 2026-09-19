"""Smoke tests for the International Justice MCP server.

These exercise the pure logic (discovery, detection, path-safety, search,
verification routing) without standing up an MCP transport. Run with:

    cd mcp && python -m pytest test_server.py     # if pytest is installed
    cd mcp && python test_server.py               # plain-stdlib fallback
"""

from __future__ import annotations

import server


def test_tribunals_discovered():
    tribunals = server._tribunals()
    assert "icc" in tribunals
    assert "icty-ictr-irmct" in tribunals
    # The repo ships thirteen tribunal folders.
    assert len(tribunals) >= 13
    icc = tribunals["icc"]
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
    icc = server._tribunals()["icc"]
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


def test_remote_mode_standalone_copy():
    """A standalone copy of server.py (no repository around it) reads from GitHub.

    This is how the published one-line `uv run … server.py` configuration
    launches the server. Requires network access to github.com; if GitHub is
    unreachable the test reports a skip rather than failing.
    """
    import importlib.util
    import shutil
    import sys
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as td:
        dst = Path(td) / "cache" / "server.py"
        dst.parent.mkdir()
        shutil.copy(Path(server.__file__), dst)
        spec = importlib.util.spec_from_file_location("server_standalone", dst)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = mod
        try:
            spec.loader.exec_module(mod)
        finally:
            sys.modules.pop(spec.name, None)

        tribunals = mod._tribunals()
        if not tribunals:
            print("  (skipped: GitHub unreachable — remote mode not exercised)")
            return
        assert mod._REMOTE_MODE
        assert len(tribunals) >= 13
        out = mod.get_skill_file("icc", "SKILL.md")
        assert "verification" in out.lower()
        # Safety in remote mode: only paths listed in the repository tree
        # are fetchable — traversal-style paths resolve to nothing.
        assert mod._read_tribunal_file(tribunals["icc"], "../CLAUDE.md") is None


def test_resolve_citation_parses_and_flags():
    out = server.resolve_citation("Prosecutor v. Bemba, ICC-01/05-01/08-3343, para. 188")
    assert "icc" in out
    assert "ICC-01/05-01/08-3343" in out
    assert "188" in out
    assert "form matches" in out.lower() or "form matches the documented scheme" in out
    # Confidential suffix is a hard stop.
    out2 = server.resolve_citation("ICC-01/04-01/06-2842-Conf", tribunal="icc")
    assert "HARD STOP" in out2
    # ECCC severance discipline.
    out3 = server.resolve_citation("Case 002 Trial Judgment", tribunal="eccc")
    assert "002/01" in out3
    # Garbage citation warns rather than validating.
    out4 = server.resolve_citation("some vague reference", tribunal="icc")
    assert "No canonical case-number form recognised" in out4


def test_match_quote_levels():
    src = (
        "57. The Chamber recalls that \u201ceffective control\u201d is the "
        "material ability to prevent or repress the commission of the crimes. "
        "58. This standard has been applied consistently."
    )
    v, s, _ = server._match_quote(src, 'the material ability to prevent or repress the commission of the crimes')
    assert v == "verbatim" and s == 1.0
    # Curly vs straight quotes normalise away.
    v2, _, _ = server._match_quote(src, '"effective control" is the material ability')
    assert v2 == "verbatim"
    # Paraphrase scores below verbatim.
    v3, s3, _ = server._match_quote(src, "effective control means being able to stop or punish crimes")
    assert v3 in ("close", "partial", "absent") and s3 < 1.0
    # Absent text is not found.
    v4, _, _ = server._match_quote(src, "the tribunal lacks jurisdiction over corporations entirely")
    assert v4 in ("partial", "absent")


def test_search_sources_routes_to_tier1():
    out = server.search_sources("effective control command responsibility", tribunal="icc")
    assert "Tier 1" in out
    assert "legal-tools" in out.lower()
    out2 = server.search_sources("Srebrenica genocide appeal")
    assert "icty-ictr-irmct" in out2


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
