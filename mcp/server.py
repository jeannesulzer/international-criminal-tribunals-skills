"""International Justice MCP server.

Exposes the international-criminal-tribunals-skills suite over the Model
Context Protocol. Four capability areas, mapped to the suite's methodology:

  1. Expose the skills      -> list_tribunals, get_skill_file, read resources
  2. Verify citations       -> verify_citation (detect tribunal + return the
                               authoritative sources, citation format, and
                               verification workflow for it)
  3. Search the case law    -> search_jurisprudence (full-text over the
                               jurisprudence maps and reference files)
  4. Retrieve documents     -> fetch_document (HTTP fetch with the suite's
                               403 / fallback-ladder discipline surfaced)

The server is documentation-grounded: every tribunal folder in the repo is a
self-contained Claude Skill, and this server reads that content live rather
than duplicating it. Nothing here lets a citation be produced from memory —
the verification-first discipline is preserved by design.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from mcp.server.fastmcp import FastMCP

# --------------------------------------------------------------------------
# Repository layout
# --------------------------------------------------------------------------

# This file lives in <repo>/mcp/server.py; the content root is the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Files at the repo root that are not tribunal folders.
_NON_TRIBUNAL_DIRS = {"mcp", "docs", ".git"}

# The standard seven-file backbone every tribunal shares, plus the optional
# tribunal-specific references that some folders add.
STANDARD_REFERENCES = (
    "authoritative-sources",
    "citation-format",
    "verification-workflow",
    "foundational-texts",
    "jurisprudence-map",
)


@dataclass(frozen=True)
class Tribunal:
    """A single tribunal skill folder."""

    slug: str  # directory name, e.g. "icc"
    name: str  # frontmatter name, falls back to slug
    description: str  # frontmatter description (first sentence kept short)
    path: Path

    @property
    def skill_file(self) -> Path:
        return self.path / "SKILL.md"


# --------------------------------------------------------------------------
# Citation-pattern -> tribunal detection
# --------------------------------------------------------------------------
#
# Best-effort detection so verify_citation can route a raw citation to the
# right tribunal's authoritative sources. Patterns are ordered most- to
# least-specific; a citation may match several, and all matches are returned
# ranked by score. These mirror the case-number schemes documented in each
# tribunal's citation-format.md and in CLAUDE.md.

_DETECTION_RULES: dict[str, list[tuple[str, int]]] = {
    "icc": [
        (r"\bICC-\d{2}/\d", 5),
        (r"\bICC-\d", 4),
        (r"\bRome Statute\b", 3),
        (r"\bArticle\s+28\([ab]\)", 3),
    ],
    "icty-ictr-irmct": [
        (r"\bMICT-\d", 5),
        (r"\bIT-\d", 5),
        (r"\bICTR-\d", 5),
        (r"\b(Tadi[cć]|Krsti[cć]|Akayesu|Karad[zž]i[cć]|Mladi[cć])\b", 3),
    ],
    "eccc": [
        (r"/ECCC/", 5),
        (r"\bCase\s+00[1-4](?:/0[12])?\b", 4),
        (r"\b(Khmer Rouge|Duch|Nuon Chea|Khieu Samphan)\b", 3),
    ],
    "nuremberg-tokyo": [
        (r"\bIMTFE\b", 5),
        (r"\bIMT\b", 4),
        (r"\b(Nuremberg|Tokyo|Pritchard-Zaide|Blue Series|Green Series)\b", 3),
    ],
    "scsl-rscsl": [
        (r"\bSCSL-\d", 5),
        (r"\b(RSCSL|Special Court for Sierra Leone|Taylor)\b", 2),
    ],
    "stl": [
        (r"\bSTL-\d", 5),
        (r"\b(Special Tribunal for Lebanon|Ayyash)\b", 3),
    ],
    "ksc": [
        (r"\bKSC-(?:BC|CA)-\d", 5),
        (r"\b(Kosovo Specialist Chambers|Tha[cç]i)\b", 3),
    ],
    "cps-rca": [
        (r"\b(Cour P[eé]nale Sp[eé]ciale|CPS-RCA|Paoua|Koundjili|Lemouna)\b", 4),
    ],
    "jep": [
        (r"\bmacrocaso\b", 4),
        (r"\bCaso\s+\d{2}\b", 4),
        (r"\b(Jurisdicci[oó]n Especial para la Paz|JEP|falsos positivos)\b", 3),
    ],
    "special-panels-timor-leste": [
        (r"\b(SPSC|Serious Crimes Unit|Los Palos|UNTAET|Timor)\b", 3),
    ],
    "eac-habre": [
        (r"\b(Habr[eé]|Chambres Africaines|Extraordinary African Chambers|CAE)\b", 4),
    ],
    "reg-64-kosovo": [
        (r"\b(Reg\.?\s*64|Regulation\s+2000/64|UNMIK)\b", 4),
    ],
    "wcc-bih": [
        (r"\bRule\s+11\s*bis\b", 4),
        (r"\b(Court of Bosnia|Sud Bosne|War Crimes Chamber)\b", 3),
    ],
}


# --------------------------------------------------------------------------
# Skill discovery
# --------------------------------------------------------------------------


def _parse_frontmatter(text: str) -> dict[str, str]:
    """Parse the simple `key: value` YAML frontmatter used by SKILL.md.

    The suite's frontmatter only uses flat string keys (name, description),
    so a full YAML parser is unnecessary and avoids a dependency.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip("\n")
    out: dict[str, str] = {}
    key: str | None = None
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s?(.*)$", line)
        if m:
            key = m.group(1).strip()
            out[key] = m.group(2).strip()
        elif key and line.strip():
            # Continuation of a wrapped value.
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def _short(text: str, limit: int = 280) -> str:
    """First sentence (or first `limit` chars) of a longer description."""
    text = text.strip()
    dot = text.find(". ")
    if 0 < dot < limit:
        return text[: dot + 1]
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def _discover_tribunals() -> dict[str, Tribunal]:
    found: dict[str, Tribunal] = {}
    for child in sorted(REPO_ROOT.iterdir()):
        if not child.is_dir() or child.name in _NON_TRIBUNAL_DIRS:
            continue
        skill = child / "SKILL.md"
        if not skill.is_file():
            continue
        fm = _parse_frontmatter(skill.read_text(encoding="utf-8"))
        found[child.name] = Tribunal(
            slug=child.name,
            name=fm.get("name", child.name),
            description=fm.get("description", ""),
            path=child,
        )
    return found


# Discovered once at import; the repo content is static within a session.
TRIBUNALS: dict[str, Tribunal] = _discover_tribunals()


def _resolve_tribunal(slug_or_name: str) -> Tribunal | None:
    key = slug_or_name.strip().lower()
    if key in TRIBUNALS:
        return TRIBUNALS[key]
    for trib in TRIBUNALS.values():
        if trib.name.lower() == key:
            return trib
    return None


def _safe_md_path(trib: Tribunal, rel: str) -> Path | None:
    """Resolve a relative markdown path inside a tribunal folder, safely.

    Accepts forms like "SKILL.md", "references/citation-format.md", or a bare
    reference name like "citation-format". Rejects traversal outside the
    tribunal folder.
    """
    rel = rel.strip().lstrip("/")
    if not rel:
        rel = "SKILL.md"
    # Bare reference name shorthand: "citation-format" -> references/citation-format.md
    if "/" not in rel and not rel.endswith(".md") and rel != "SKILL":
        if rel in STANDARD_REFERENCES or rel.startswith(("case-", "defendants", "jurisprudence")):
            rel = f"references/{rel}.md"
    if not rel.endswith(".md"):
        rel += ".md"
    candidate = (trib.path / rel).resolve()
    try:
        candidate.relative_to(trib.path.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def _iter_md_files(trib: Tribunal) -> Iterable[Path]:
    yield from sorted(trib.path.rglob("*.md"))


def detect_tribunals(text: str) -> list[tuple[str, int]]:
    """Return (slug, score) pairs for tribunals matching the given text."""
    scores: dict[str, int] = {}
    for slug, rules in _DETECTION_RULES.items():
        for pattern, weight in rules:
            if re.search(pattern, text, flags=re.IGNORECASE):
                scores[slug] = scores.get(slug, 0) + weight
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)


# --------------------------------------------------------------------------
# MCP server
# --------------------------------------------------------------------------

mcp = FastMCP(
    "international-justice",
    instructions=(
        "Research, drafting, and citation-verification support for international "
        "criminal tribunals (ICC, ICTY/ICTR/IRMCT, ECCC, Nuremberg/Tokyo, SCSL, "
        "STL, KSC, CPS-RCA, JEP, Timor-Leste Special Panels, EAC/Habré, Reg-64 "
        "Kosovo, WCC-BiH).\n\n"
        "Methodology is verification-first: every case-specific citation "
        "(judgment, decision, warrant, filing, statement) MUST be verified "
        "against a Tier 1 authoritative source in the current conversation "
        "before it appears in any output. Only the foundational instruments "
        "(statutes, rules, regulations) may be cited from project knowledge.\n\n"
        "Typical flow: call list_tribunals to orient; verify_citation to route a "
        "citation to the right authoritative sources and workflow; "
        "search_jurisprudence to locate a holding; fetch_document to retrieve a "
        "primary source (honouring the fallback ladder on 403); get_skill_file "
        "to read any reference in full. This server never authorises citing "
        "case law from memory."
    ),
)


@mcp.tool()
def list_tribunals() -> str:
    """List every tribunal skill available, with its slug and a short description.

    Use this first to orient: it tells you which tribunals are covered and the
    exact slug to pass to the other tools (e.g. "icc", "icty-ictr-irmct",
    "eccc"). One folder per tribunal, each a self-contained Claude Skill.
    """
    lines = [f"{len(TRIBUNALS)} tribunal skills available:", ""]
    for trib in TRIBUNALS.values():
        refs = sorted(
            p.stem for p in (trib.path / "references").glob("*.md")
        ) if (trib.path / "references").is_dir() else []
        lines.append(f"## {trib.slug}")
        lines.append(_short(trib.description) or "(no description)")
        if refs:
            lines.append(f"References: {', '.join(refs)}")
        lines.append("")
    return "\n".join(lines).rstrip()


@mcp.tool()
def get_skill_file(tribunal: str, file: str = "SKILL.md") -> str:
    """Return the full text of a skill file for a tribunal.

    `tribunal` is a slug from list_tribunals (e.g. "icc"). `file` may be:
      - "SKILL.md" (default) — the entry point and hard rules
      - a reference path like "references/citation-format.md"
      - a bare reference name like "citation-format", "authoritative-sources",
        "verification-workflow", "foundational-texts", "jurisprudence-map"
      - an example like "examples/example-verification.md"

    Use this to read a tribunal's citation format, source hierarchy, or
    verification workflow in full before drafting or auditing.
    """
    trib = _resolve_tribunal(tribunal)
    if trib is None:
        return _unknown_tribunal_message(tribunal)
    path = _safe_md_path(trib, file)
    if path is None:
        available = [
            str(p.relative_to(trib.path)) for p in _iter_md_files(trib)
        ]
        return (
            f"No file '{file}' in tribunal '{trib.slug}'.\n\n"
            f"Available files:\n- " + "\n- ".join(available)
        )
    rel = path.relative_to(trib.path)
    return f"# {trib.slug}/{rel}\n\n" + path.read_text(encoding="utf-8")


@mcp.tool()
def search_jurisprudence(
    query: str,
    tribunal: str = "",
    scope: str = "all",
    max_results: int = 20,
) -> str:
    """Full-text search across the skills' case-law and reference content.

    `query` is matched case-insensitively against every line. Space-separated
    terms are ANDed (a line/section must contain all of them). Use it to find
    where a holding, case, doctrine, or document number is documented.

    `tribunal` (optional) restricts to one tribunal slug. `scope` narrows by
    file kind: "all" (default), "jurisprudence" (jurisprudence-map.md only),
    "citation" (citation-format.md), "sources" (authoritative-sources.md),
    "examples", or "skill" (SKILL.md). `max_results` caps the hits returned.

    Results are pointers, not a substitute for verification: a hit tells you
    where the suite documents something, which you still confirm against a
    Tier 1 source before citing.
    """
    terms = [t.lower() for t in query.split() if t.strip()]
    if not terms:
        return "Provide a non-empty query."

    scope_filter = {
        "jurisprudence": lambda p: p.name == "jurisprudence-map.md",
        "citation": lambda p: p.name == "citation-format.md",
        "sources": lambda p: p.name == "authoritative-sources.md",
        "examples": lambda p: p.parent.name == "examples",
        "skill": lambda p: p.name == "SKILL.md",
        "all": lambda p: True,
    }.get(scope.lower())
    if scope_filter is None:
        return (
            f"Unknown scope '{scope}'. Use: all, jurisprudence, citation, "
            "sources, examples, skill."
        )

    if tribunal:
        trib = _resolve_tribunal(tribunal)
        if trib is None:
            return _unknown_tribunal_message(tribunal)
        search_space = [trib]
    else:
        search_space = list(TRIBUNALS.values())

    hits: list[tuple[int, str, int, str]] = []  # (score, "slug/rel", lineno, line)
    for trib in search_space:
        for path in _iter_md_files(trib):
            if not scope_filter(path):
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines, start=1):
                low = line.lower()
                if all(t in low for t in terms):
                    score = sum(low.count(t) for t in terms)
                    rel = f"{trib.slug}/{path.relative_to(trib.path)}"
                    hits.append((score, rel, i, line.strip()))

    if not hits:
        return f"No matches for '{query}'" + (f" in {tribunal}" if tribunal else "") + "."

    hits.sort(key=lambda h: h[0], reverse=True)
    shown = hits[: max(1, max_results)]
    out = [f"{len(hits)} match(es) for '{query}'; showing {len(shown)}:", ""]
    for _score, rel, lineno, line in shown:
        snippet = line if len(line) <= 200 else line[:200] + "…"
        out.append(f"- `{rel}:{lineno}` — {snippet}")
    if len(hits) > len(shown):
        out.append(f"\n…and {len(hits) - len(shown)} more. Narrow the query or raise max_results.")
    out.append(
        "\nThese are documentation pointers. Verify any citation against a "
        "Tier 1 source before using it."
    )
    return "\n".join(out)


@mcp.tool()
def verify_citation(citation: str, tribunal: str = "") -> str:
    """Route a citation to its tribunal and return the guidance to verify it.

    Pass a raw citation or case reference (e.g. "ICC-01/05-01/08-3343",
    "Prosecutor v. Krstić IT-98-33-T", "Case 002/02"). The tool detects the
    tribunal from the citation's number scheme and key terms, then returns —
    for that tribunal — the citation-format rules, the authoritative-source
    hierarchy, and the verification workflow (including the fallback ladder
    for direct-fetch failures).

    Give `tribunal` explicitly to override detection. This tool does NOT
    assert a citation is correct — it equips you to confirm it against a
    primary source, which is the only thing that counts as verification.
    """
    if tribunal:
        trib = _resolve_tribunal(tribunal)
        if trib is None:
            return _unknown_tribunal_message(tribunal)
        candidates = [trib.slug]
        detection_note = f"Tribunal set explicitly to '{trib.slug}'."
    else:
        ranked = detect_tribunals(citation)
        if not ranked:
            return (
                f"Could not detect a tribunal from:\n  {citation}\n\n"
                "Pass `tribunal` explicitly (see list_tribunals) — the citation "
                "scheme did not match any known pattern."
            )
        candidates = [slug for slug, _ in ranked]
        top = ", ".join(f"{slug} (score {score})" for slug, score in ranked)
        detection_note = f"Detected from citation, ranked: {top}."

    primary = _resolve_tribunal(candidates[0])
    assert primary is not None

    parts = [
        f"# Verification guidance for: {citation}",
        "",
        detection_note,
        "",
        "## Verification posture",
        "Verification is gradient — match it to the claim:",
        "- **Existence**: document number, title, date, chamber confirmed against a Tier 1 source.",
        "- **Content**: retrieved text confirms the document holds, in substance, what you claim.",
        "- **Paragraph**: the cited paragraph(s) contain the cited proposition (required for any quotation or pinpoint).",
        "",
        f"## {primary.slug} — citation format",
        _read_or_note(primary, "references/citation-format.md"),
        "",
        f"## {primary.slug} — authoritative sources",
        _read_or_note(primary, "references/authoritative-sources.md"),
        "",
        f"## {primary.slug} — verification workflow (incl. fallback ladder)",
        _read_or_note(primary, "references/verification-workflow.md"),
    ]
    if len(candidates) > 1:
        parts += [
            "",
            "## Other possible tribunals",
            "The citation also resembles: "
            + ", ".join(candidates[1:])
            + ". If the detection is wrong, re-run with `tribunal` set.",
        ]
    parts += [
        "",
        "## Reminder",
        "This guidance does not verify the citation. Retrieve the document from "
        "a Tier 1 source in this conversation, then cite only what the source "
        "confirms. Confidential / redacted-exclusive filings are never citable "
        "from a public output.",
    ]
    return "\n".join(parts)


@mcp.tool()
async def fetch_document(url: str, tribunal: str = "") -> str:
    """Fetch a primary-source document over HTTP, honouring the suite's discipline.

    Use this to retrieve a court document, decision, or press release from an
    authoritative domain (icc-cpi.int, legal-tools.org, irmct.org,
    eccc.gov.kh, etc.). Sends a browser-like User-Agent to reduce 403s.

    On a 403 or block (structural for icc-cpi.int, cpsrca.cf, and others), the
    tool does NOT treat failure as fatal: it returns the tribunal's fallback
    ladder so you can work it (search the document number + domain, try Legal
    Tools, use Tier 2 to confirm existence/content, then ask the user). Pass
    `tribunal` to get the right ladder; otherwise it is inferred from the URL.
    """
    try:
        import httpx
    except ModuleNotFoundError:
        return (
            "The `httpx` dependency is not installed. Install the server's "
            "dependencies (see mcp/pyproject.toml) to enable fetching."
        )

    slug = tribunal or _infer_tribunal_from_url(url)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept": "text/html,application/pdf,*/*",
    }
    try:
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=30.0, headers=headers
        ) as client:
            resp = await client.get(url)
    except Exception as exc:  # network error, DNS, timeout, TLS
        return (
            f"Fetch failed for {url}\nError: {exc}\n\n"
            + _fallback_ladder_note(slug)
        )

    if resp.status_code == 403 or resp.status_code == 451:
        return (
            f"Blocked ({resp.status_code}) fetching {url}\n\n"
            "This is expected for some authoritative domains and is NOT fatal — "
            "the document still exists and is authoritative.\n\n"
            + _fallback_ladder_note(slug)
        )
    if resp.status_code >= 400:
        return (
            f"HTTP {resp.status_code} fetching {url}\n\n"
            + _fallback_ladder_note(slug)
        )

    ctype = resp.headers.get("content-type", "")
    if "pdf" in ctype.lower() or url.lower().endswith(".pdf"):
        size = len(resp.content)
        return (
            f"Retrieved a PDF from {url} ({size} bytes, content-type: {ctype}).\n"
            "This server returns text, not parsed PDF. Capture the document "
            "number, date, chamber, title, and the paragraph(s) you cite from "
            "the PDF itself. If you have a PDF-reading tool, use it on this URL."
        )

    text = resp.text
    body = _strip_html(text) if "html" in ctype.lower() else text
    if len(body) > 60_000:
        body = body[:60_000] + "\n\n…[truncated; refine to the relevant section]"
    return f"Retrieved {url} (HTTP {resp.status_code}, {ctype}):\n\n{body}"


# --------------------------------------------------------------------------
# Resources — expose every skill file as skill://<slug>/<relative-path>
# --------------------------------------------------------------------------
#
# This FastMCP version matches each URI template parameter as a single path
# segment ([^/]+), so a multi-segment wildcard is not available. The tribunal
# folders use a fixed two-level layout (root files + references/ + examples/),
# so one template per level covers every file cleanly.


def _resource_read(slug: str, rel: str) -> str:
    trib = _resolve_tribunal(slug)
    if trib is None:
        return _unknown_tribunal_message(slug)
    resolved = _safe_md_path(trib, rel)
    if resolved is None:
        return f"No file '{rel}' in tribunal '{slug}'."
    return resolved.read_text(encoding="utf-8")


@mcp.resource("skill://{slug}/SKILL.md")
def skill_main(slug: str) -> str:
    """The tribunal's SKILL.md entry point."""
    return _resource_read(slug, "SKILL.md")


@mcp.resource("skill://{slug}/CHANGELOG.md")
def skill_changelog(slug: str) -> str:
    """The tribunal's CHANGELOG.md."""
    return _resource_read(slug, "CHANGELOG.md")


@mcp.resource("skill://{slug}/references/{name}")
def skill_reference(slug: str, name: str) -> str:
    """A reference file, e.g. skill://icc/references/citation-format.md."""
    return _resource_read(slug, f"references/{name}")


@mcp.resource("skill://{slug}/examples/{name}")
def skill_example(slug: str, name: str) -> str:
    """An example file, e.g. skill://icc/examples/example-verification.md."""
    return _resource_read(slug, f"examples/{name}")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def _read_or_note(trib: Tribunal, rel: str) -> str:
    path = _safe_md_path(trib, rel)
    if path is None:
        return f"(no {rel} for {trib.slug})"
    return path.read_text(encoding="utf-8").strip()


def _unknown_tribunal_message(slug: str) -> str:
    known = ", ".join(TRIBUNALS)
    return f"Unknown tribunal '{slug}'.\n\nKnown slugs: {known}\nCall list_tribunals for descriptions."


def _infer_tribunal_from_url(url: str) -> str:
    domain_map = {
        "icc-cpi.int": "icc",
        "asp.icc-cpi.int": "icc",
        "irmct.org": "icty-ictr-irmct",
        "icty.org": "icty-ictr-irmct",
        "unictr": "icty-ictr-irmct",
        "eccc.gov.kh": "eccc",
        "rscsl.org": "scsl-rscsl",
        "scsl": "scsl-rscsl",
        "stl-tsl.org": "stl",
        "scp-ks.org": "ksc",
        "cpsrca": "cps-rca",
        "jep.gov.co": "jep",
        "chambresafricaines": "eac-habre",
        "forumchambresafricaines": "eac-habre",
        "sudbih.gov.ba": "wcc-bih",
    }
    low = url.lower()
    for needle, slug in domain_map.items():
        if needle in low:
            return slug
    return ""


def _fallback_ladder_note(slug: str) -> str:
    trib = _resolve_tribunal(slug) if slug else None
    if trib is not None:
        wf = _safe_md_path(trib, "references/verification-workflow.md")
        if wf is not None:
            return (
                f"Work the {trib.slug} fallback ladder (from "
                f"{trib.slug}/references/verification-workflow.md):\n\n"
                + wf.read_text(encoding="utf-8").strip()
            )
    return (
        "Generic fallback ladder:\n"
        "1. Search for the document number plus the authoritative domain — the "
        "court's own press release usually confirms number, title, date, "
        "chamber (existence/content level).\n"
        "2. Try legal-tools.org for the full text.\n"
        "3. Use a clearly-labelled Tier 2 source to confirm existence/content, "
        "noting the full PDF was not retrievable.\n"
        "4. If still unresolved, ask the user for the document.\n\n"
        "Call list_tribunals then get_skill_file(<slug>, 'verification-workflow') "
        "for the tribunal-specific ladder."
    )


_TAG_RE = re.compile(r"(?is)<(script|style)\b.*?</\1>")
_HTML_RE = re.compile(r"(?s)<[^>]+>")
_WS_RE = re.compile(r"\n{3,}")


def _strip_html(html: str) -> str:
    """Very small HTML-to-text reduction for readability of fetched pages."""
    text = _TAG_RE.sub(" ", html)
    text = _HTML_RE.sub("", text)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&#39;", "'")
        .replace("&quot;", '"')
    )
    lines = [ln.strip() for ln in text.splitlines()]
    text = "\n".join(ln for ln in lines if ln)
    return _WS_RE.sub("\n\n", text)


if __name__ == "__main__":
    mcp.run()
