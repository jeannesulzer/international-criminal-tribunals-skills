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

try:
    # MCP Python SDK 1.x
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # SDK 2.x renamed FastMCP to MCPServer; the surface this server uses
    # (constructor with name + instructions, .tool(), .resource(), .run())
    # is unchanged. Without this shim, a fresh install of the SDK makes the
    # server crash at import — which the MCP client reports as a startup
    # timeout or "could not attach".
    from mcp.server.mcpserver import MCPServer as FastMCP

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
        (r"\bSrebrenica\b", 3),
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


# Discovery is lazy (first tool call, not import) so the server attaches to
# the MCP client instantly — slow startups get killed by client timeouts.
_TRIBUNALS_CACHE: dict[str, Tribunal] | None = None


# --------------------------------------------------------------------------
# Remote content mode
# --------------------------------------------------------------------------
#
# The server normally reads the skill folders around it (it lives in
# <repo>/mcp/). But some clients launch server.py standalone — e.g. the
# published one-line `uv run … https://raw.githubusercontent.com/…/server.py`
# configuration downloads this single file into a cache directory with no
# repository around it. In that case the local scan finds nothing, and the
# server falls back to reading the same content from the repository on
# GitHub, fetched lazily and cached in memory. Same files, same discipline —
# only the transport differs.

_GITHUB_REPO = "jeannesulzer/international-criminal-tribunals-skills"
_GITHUB_BRANCH = "main"
_RAW_BASE = f"https://raw.githubusercontent.com/{_GITHUB_REPO}/{_GITHUB_BRANCH}/"
_TREE_URL = (
    f"https://api.github.com/repos/{_GITHUB_REPO}/git/trees/{_GITHUB_BRANCH}"
    "?recursive=1"
)

_REMOTE_MODE = False
_REMOTE_FILES: dict[str, list[str]] = {}  # slug -> sorted relative .md paths
_REMOTE_TEXT: dict[str, str] = {}  # "<slug>/<rel>" -> cached file content
_HTTP_CLIENT = None  # lazy httpx.Client, reused across fetches


def _http():
    global _HTTP_CLIENT
    if _HTTP_CLIENT is None:
        import httpx

        _HTTP_CLIENT = httpx.Client(follow_redirects=True, timeout=30.0)
    return _HTTP_CLIENT


def _remote_read(slug: str, rel: str) -> str | None:
    """Fetch one skill file from the repository on GitHub, with caching."""
    key = f"{slug}/{rel}"
    if key in _REMOTE_TEXT:
        return _REMOTE_TEXT[key]
    try:
        resp = _http().get(_RAW_BASE + key)
    except Exception:
        return None
    if resp.status_code != 200:
        return None
    _REMOTE_TEXT[key] = resp.text
    return resp.text


def _discover_remote() -> dict[str, Tribunal]:
    """Discover tribunals from the GitHub repository tree (standalone mode)."""
    import json

    resp = _http().get(_TREE_URL)
    resp.raise_for_status()
    entries = json.loads(resp.text).get("tree", [])
    md_paths = [
        e["path"]
        for e in entries
        if e.get("type") == "blob" and e.get("path", "").endswith(".md")
    ]
    slugs = sorted(
        {
            p.split("/", 1)[0]
            for p in md_paths
            if "/" in p
            and p.split("/", 1)[1] == "SKILL.md"
            and p.split("/", 1)[0] not in _NON_TRIBUNAL_DIRS
        }
    )
    found: dict[str, Tribunal] = {}
    for slug in slugs:
        _REMOTE_FILES[slug] = sorted(
            p.split("/", 1)[1] for p in md_paths if p.startswith(slug + "/")
        )
        text = _remote_read(slug, "SKILL.md") or ""
        fm = _parse_frontmatter(text)
        found[slug] = Tribunal(
            slug=slug,
            name=fm.get("name", slug),
            description=fm.get("description", ""),
            path=REPO_ROOT / slug,
        )
    return found


def _tribunals() -> dict[str, Tribunal]:
    """Local folders when the repository is present; GitHub otherwise.

    A failed remote discovery (offline, rate-limited) is not cached, so the
    next tool call retries instead of leaving the server permanently empty.
    """
    global _TRIBUNALS_CACHE, _REMOTE_MODE
    if _TRIBUNALS_CACHE:
        return _TRIBUNALS_CACHE
    found = _discover_tribunals()
    if found:
        _TRIBUNALS_CACHE = found
        return found
    try:
        found = _discover_remote()
    except Exception:
        return {}
    if found:
        _REMOTE_MODE = True
        _TRIBUNALS_CACHE = found
    return found


def _resolve_tribunal(slug_or_name: str) -> Tribunal | None:
    key = slug_or_name.strip().lower()
    tribunals = _tribunals()
    if key in tribunals:
        return tribunals[key]
    for trib in tribunals.values():
        if trib.name.lower() == key:
            return trib
    return None


def _normalize_rel(rel: str) -> str:
    """Normalise a requested file path inside a tribunal folder.

    Accepts forms like "SKILL.md", "references/citation-format.md", or a bare
    reference name like "citation-format".
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
    return rel


def _safe_md_path(trib: Tribunal, rel: str) -> Path | None:
    """Resolve a relative markdown path inside a tribunal folder, safely.

    Rejects traversal outside the tribunal folder. Local mode only.
    """
    candidate = (trib.path / _normalize_rel(rel)).resolve()
    try:
        candidate.relative_to(trib.path.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def _tribunal_files(trib: Tribunal) -> list[str]:
    """All markdown files of a tribunal, as sorted relative paths."""
    if _REMOTE_MODE:
        return list(_REMOTE_FILES.get(trib.slug, []))
    return sorted(
        str(p.relative_to(trib.path)) for p in trib.path.rglob("*.md")
    )


def _read_tribunal_file(trib: Tribunal, rel: str) -> tuple[str, str] | None:
    """Read one tribunal file, local or remote. Returns (normalised rel, text).

    In local mode, path safety comes from `_safe_md_path` (no traversal out of
    the tribunal folder). In remote mode it comes from membership in the known
    file list — only paths GitHub's repository tree lists can be fetched.
    """
    rel_norm = _normalize_rel(rel)
    if _REMOTE_MODE:
        if rel_norm not in _REMOTE_FILES.get(trib.slug, []):
            return None
        text = _remote_read(trib.slug, rel_norm)
        return (rel_norm, text) if text is not None else None
    path = _safe_md_path(trib, rel_norm)
    if path is None:
        return None
    return rel_norm, path.read_text(encoding="utf-8")


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
    tribunals = _tribunals()
    if not tribunals:
        return (
            "No tribunal skills found. The server found no skill folders "
            "locally and could not reach the repository on GitHub "
            f"(https://github.com/{_GITHUB_REPO}). Check network access and "
            "call this tool again."
        )
    lines = [f"{len(tribunals)} tribunal skills available:", ""]
    for trib in tribunals.values():
        refs = sorted(
            f.removeprefix("references/").removesuffix(".md")
            for f in _tribunal_files(trib)
            if f.startswith("references/")
        )
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
    got = _read_tribunal_file(trib, file)
    if got is None:
        available = _tribunal_files(trib)
        return (
            f"No file '{file}' in tribunal '{trib.slug}'.\n\n"
            f"Available files:\n- " + "\n- ".join(available)
        )
    rel, text = got
    return f"# {trib.slug}/{rel}\n\n" + text


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
        "jurisprudence": lambda rel: rel.endswith("jurisprudence-map.md"),
        "citation": lambda rel: rel.endswith("citation-format.md"),
        "sources": lambda rel: rel.endswith("authoritative-sources.md"),
        "examples": lambda rel: rel.startswith("examples/"),
        "skill": lambda rel: rel == "SKILL.md",
        "all": lambda rel: True,
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
        search_space = list(_tribunals().values())

    hits: list[tuple[int, str, int, str]] = []  # (score, "slug/rel", lineno, line)
    for trib in search_space:
        for rel in _tribunal_files(trib):
            if not scope_filter(rel):
                continue
            got = _read_tribunal_file(trib, rel)
            if got is None:
                continue
            for i, line in enumerate(got[1].splitlines(), start=1):
                low = line.lower()
                if all(t in low for t in terms):
                    score = sum(low.count(t) for t in terms)
                    hits.append((score, f"{trib.slug}/{rel}", i, line.strip()))

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
def get_foundational_texts(tribunal: str) -> str:
    """Return a tribunal's foundational instruments — the only texts citable from memory.

    Every tribunal has a small set of constitutive instruments (its statute,
    rules of procedure and evidence, and regulations / equivalents) that, under
    the suite's methodology, MAY be cited from project knowledge without a
    fresh fetch — provided they are present in the conversation. Everything else
    (judgments, decisions, warrants, filings, statements) must be verified
    against a Tier 1 source first.

    This returns the tribunal's `foundational-texts.md`, which names exactly
    which instruments qualify, the revision/amendment discipline that applies
    (e.g. ECCC Law "Article 29 new", the in-force RPE revision), and what is
    explicitly NOT foundational. Use it to decide whether a given instrument
    citation needs verification or not.
    """
    trib = _resolve_tribunal(tribunal)
    if trib is None:
        return _unknown_tribunal_message(tribunal)
    got = _read_tribunal_file(trib, "references/foundational-texts.md")
    if got is None:
        return (
            f"No foundational-texts.md for '{trib.slug}'. Foundational instruments "
            "are the only texts citable from project knowledge; without this file, "
            "treat every instrument citation as requiring verification."
        )
    return (
        f"# {trib.slug} — foundational texts (citable from project knowledge "
        "only when present in the conversation)\n\n"
        + got[1].strip()
        + "\n\n---\nReminder: these instruments are the ONLY exception to "
        "verify-before-citing, and only when actually present. All case-specific "
        "documents (judgments, decisions, filings) still require a Tier 1 fetch."
    )


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
        return _extract_pdf_text(url, resp.content, ctype)

    text = resp.text
    body = _strip_html(text) if "html" in ctype.lower() else text
    if len(body) > 60_000:
        body = body[:60_000] + "\n\n…[truncated; refine to the relevant section]"
    return f"Retrieved {url} (HTTP {resp.status_code}, {ctype}):\n\n{body}"


# --------------------------------------------------------------------------
# Citation resolution and quote verification
# --------------------------------------------------------------------------
#
# These tools mechanise the first rungs of the verification gradient.
# resolve_citation checks a citation's FORM against the tribunal's documented
# scheme and extracts its components; verify_quote checks a claimed passage
# against the authoritative source itself. Neither vouches for anything the
# source does not support: form-validity is not existence, and existence is
# not content.

_CASE_FORMS: dict[str, list[tuple[str, str]]] = {
    # slug -> (label, regex) for the canonical case/document number forms,
    # mirroring each tribunal's citation-format.md.
    "icc": [
        ("document number", r"ICC-\d{2}/\d{2}-\d{2}/\d{2}-[0-9][\w.-]*"),
        ("case number", r"ICC-\d{2}/\d{2}-\d{2}/\d{2}"),
        ("situation number", r"ICC-\d{2}/\d{2}"),
    ],
    "icty-ictr-irmct": [
        ("ICTY case number", r"IT-\d{2}-[\dA-Za-z/&-]+"),
        ("ICTR case number", r"ICTR-\d{2,4}-[\dA-Za-z-]+"),
        ("Mechanism case number", r"MICT-\d{2}-[\dA-Za-z.-]+"),
    ],
    "eccc": [
        ("case file number", r"00[1-4](?:/0[12])?(?:/\d{2}-\d{2}-\d{4})?[-/]?ECCC[\w/-]*"),
        ("case designation", r"Case\s+00[1-4](?:/0[12])?"),
    ],
    "scsl-rscsl": [("case number", r"SCSL-(?:\d{4}|\d{2})-\d{2}[\w-]*")],
    "stl": [("case number", r"STL-\d{2}-\d{2}[\w/-]*")],
    "ksc": [("case number", r"KSC-(?:BC|CA|SC|CC)-\d{4}-\d{2}[\w/-]*")],
    "special-panels-timor-leste": [("case number", r"\d{1,3}[-/]\d{4}")],
}

_PARA_RE = re.compile(
    r"(?:para(?:graph)?s?\.?|§§?)\s*(\d+(?:\s*[-–]\s*\d+)?)", re.IGNORECASE
)
_PHASE_SUFFIX_RE = re.compile(r"-(T|A|AR7\d(?:bis)?|S|R|ES|PT|Red\d?|Corr|Conf(?:-Exp)?|Anx[\w.]*)\b")


@mcp.tool()
def resolve_citation(citation: str, tribunal: str = "") -> str:
    """Parse a citation, validate its form against the tribunal's scheme, and say how to verify it.

    Pass a citation string (e.g. "Prosecutor v. Bemba, ICC-01/05-01/08-3343,
    para. 188"). The tool detects the tribunal, extracts the components (case
    or document number, phase or redaction suffixes, paragraph references),
    checks the number's FORM against the tribunal's documented scheme, and
    flags citation-discipline problems (confidential-filing suffixes, a
    Case 002 reference without the 002/01 vs 002/02 severance, IT/MICT
    pairing).

    Form-validity is NOT existence: a well-formed citation can still be
    invented. The output ends with the concrete verification route. Use
    verify_quote to check a quoted passage against the source itself.
    """
    text = citation.strip()
    if not text:
        return "Provide a citation string."

    if tribunal:
        trib = _resolve_tribunal(tribunal)
        if trib is None:
            return _unknown_tribunal_message(tribunal)
        slugs = [trib.slug]
        detection = f"Tribunal set explicitly to '{trib.slug}'."
    else:
        ranked = detect_tribunals(text)
        slugs = [s for s, _ in ranked]
        detection = (
            "Detected: " + ", ".join(f"{s} (score {sc})" for s, sc in ranked)
            if ranked
            else "No tribunal detected from the citation. Pass `tribunal` explicitly."
        )

    lines = [f"# Citation analysis: {text}", "", detection, ""]

    matches: list[tuple[str, str, str]] = []  # (slug, label, matched text)
    for slug in slugs or list(_CASE_FORMS):
        for label, pattern in _CASE_FORMS.get(slug, []):
            m = re.search(pattern, text)
            if m:
                matches.append((slug, label, m.group(0)))
        if matches and matches[0][0] == slug:
            break  # most specific forms of the top-ranked tribunal found

    lines.append("## Components")
    if matches:
        slug, label, matched = matches[0]
        lines.append(f"- **{label}** ({slug}): `{matched}` — form matches the documented scheme.")
    else:
        lines.append(
            "- No canonical case-number form recognised. Either the citation "
            "is incomplete, or its number does not follow the tribunal's "
            "documented scheme (see the tribunal's citation-format.md) — "
            "treat that as a warning sign."
        )

    paras = _PARA_RE.findall(text)
    if paras:
        lines.append(f"- **Paragraph reference(s)**: {', '.join(paras)} — paragraph-level verification required before quoting.")

    suffixes = _PHASE_SUFFIX_RE.findall(text)
    for s in suffixes:
        if s.startswith("Conf"):
            lines.append(
                f"- **`-{s}` suffix — HARD STOP**: confidential filings are never "
                "citable from a public output. Use the public redacted version."
            )
        elif s.startswith("Red"):
            lines.append(f"- **`-{s}` suffix**: public redacted version — the correct one to cite publicly.")
        else:
            lines.append(f"- **`-{s}` suffix**: phase/annex marker — confirm it matches the document you mean.")

    # Tribunal-specific discipline flags.
    if any(s == "eccc" for s, _, _ in matches) or re.search(r"\bCase\s+002\b(?!/0[12])", text):
        if re.search(r"\bCase\s+002\b(?!/0[12])", text):
            lines.append(
                "- **ECCC severance**: 'Case 002' without /01 or /02 is ambiguous — "
                "specify Case 002/01 or Case 002/02 for trial-stage documents."
            )
    if re.search(r"\bIT-\d", text) and re.search(r"\b(appeal|appeals judgment)\b", text, re.I):
        lines.append(
            "- **IT/MICT pairing**: late ICTY appeals (Karadžić, Mladić, Šešelj) were "
            "decided under MICT case numbers — confirm which institution issued the "
            "document you cite."
        )

    lines += ["", "## Verification route"]
    primary = _resolve_tribunal(slugs[0]) if slugs else None
    if primary is not None:
        lines.append(
            f"1. Retrieve the document from a Tier 1 source for {primary.slug} "
            f"(see get_skill_file('{primary.slug}', 'authoritative-sources')) — "
            "the Legal Tools Database (legal-tools.org) covers most tribunals, "
            "with a Persistent URL per document."
        )
    else:
        lines.append("1. Identify the tribunal, then retrieve from its Tier 1 source (list_tribunals to orient).")
    lines += [
        "2. Confirm existence (number, title, date, chamber), then content, then "
        "the exact paragraph(s) — match the verification level to the claim.",
        "3. For any quotation, run verify_quote against the retrieved source.",
        "",
        "Form-validity established here is not verification. A citation appears "
        "in an output only after the source confirms it.",
    ]
    return "\n".join(lines)


def _normalise_for_match(text: str) -> str:
    """Normalise typographic variation that legitimately differs between a
    quote and a source rendering (curly quotes, dashes, whitespace runs)."""
    import unicodedata

    text = unicodedata.normalize("NFKC", text)
    for src, dst in (
        ("“", '"'), ("”", '"'), ("‘", "'"), ("’", "'"),
        ("–", "-"), ("—", "-"), (" ", " "),
    ):
        text = text.replace(src, dst)
    return re.sub(r"\s+", " ", text).strip()


def _match_quote(source_text: str, quote: str) -> tuple[str, float, str]:
    """Locate a quote in source text. Returns (verdict, score, evidence).

    Verdicts: 'verbatim' (normalised exact substring), 'close' (>= 0.85
    similarity on the best window), 'partial' (>= 0.60), 'absent'.
    """
    import difflib

    src = _normalise_for_match(source_text)
    q = _normalise_for_match(quote)
    if not q:
        return "absent", 0.0, "Empty quote."

    low_src, low_q = src.lower(), q.lower()
    pos = low_src.find(low_q)
    if pos != -1:
        start = max(0, pos - 120)
        return "verbatim", 1.0, "…" + src[start : pos + len(q) + 120] + "…"

    # Sliding-window fuzzy match over word windows of the quote's length.
    src_words = src.split()
    q_len = max(4, len(q.split()))
    window = int(q_len * 1.3) + 2
    best_ratio, best_snippet = 0.0, ""
    step = max(1, q_len // 3)
    for i in range(0, max(1, len(src_words) - window + 1), step):
        cand = " ".join(src_words[i : i + window])
        ratio = difflib.SequenceMatcher(None, low_q, cand.lower()).ratio()
        if ratio > best_ratio:
            best_ratio, best_snippet = ratio, cand
    if best_ratio >= 0.85:
        return "close", best_ratio, best_snippet
    if best_ratio >= 0.60:
        return "partial", best_ratio, best_snippet
    return "absent", best_ratio, best_snippet


@mcp.tool()
async def verify_quote(url: str, quote: str, paragraph: str = "", tribunal: str = "") -> str:
    """Check a claimed quotation against the authoritative source document itself.

    Pass the source URL (prefer a Legal Tools Persistent URL or the court's
    own record), the quoted text as you intend to use it, and optionally the
    paragraph number claimed. The tool fetches the source (PDF text is
    extracted), locates the passage, and reports one of:

    - verified (verbatim): the passage appears in the source as quoted;
    - close match: minor differences — quote from the source, not from memory;
    - partial similarity / not found: do NOT use the quotation;
    - source unreachable: the fallback ladder for the tribunal is returned.

    A 'verified' here is verification at content level; pair it with the
    paragraph check for pinpoint cites. This tool never confirms a quote the
    source does not contain.
    """
    if not quote.strip():
        return "Provide the quoted text to verify."
    fetched = await fetch_document(url, tribunal)
    if fetched.startswith(("Fetch failed", "Blocked", "HTTP ")):
        return (
            "## verify_quote: source unreachable\n\n" + fetched
            + "\n\nThe quote is UNVERIFIED. Work the ladder above or ask the "
            "user for the document; do not use the quotation until the source "
            "confirms it."
        )

    verdict, score, evidence = _match_quote(fetched, quote)

    para_note = ""
    if paragraph:
        para_pat = re.compile(
            r"(?:^|\D)" + re.escape(paragraph.strip()) + r"(?:\.|\)|\s)", re.M
        )
        if verdict in ("verbatim", "close") and evidence:
            anchor = evidence.strip("…").strip()[:60]
            zone_start = max(0, _normalise_for_match(fetched).find(anchor) - 600)
            zone = _normalise_for_match(fetched)[zone_start : zone_start + 1200]
            para_note = (
                f"\n- Claimed paragraph {paragraph}: marker "
                + ("FOUND near the passage (best-effort — PDF extraction can reflow numbering)."
                   if para_pat.search(zone) else
                   "not confirmed near the passage. PDF extraction often drops "
                   "paragraph markers; confirm the pinpoint against the document layout.")
            )

    if verdict == "verbatim":
        head = "## verify_quote: VERIFIED (verbatim, content level)"
        advice = "The passage appears in the source as quoted."
    elif verdict == "close":
        head = f"## verify_quote: CLOSE MATCH (similarity {score:.2f})"
        advice = (
            "The source contains a near-identical passage. Quote the source's "
            "wording exactly rather than the submitted text."
        )
    elif verdict == "partial":
        head = f"## verify_quote: PARTIAL SIMILARITY ONLY (best {score:.2f})"
        advice = (
            "The source does not contain this passage as quoted. Do NOT use "
            "the quotation; re-read the best-matching passage below."
        )
    else:
        head = f"## verify_quote: NOT FOUND (best similarity {score:.2f})"
        advice = (
            "The source does not appear to contain this passage. Do NOT use "
            "the quotation. If the document is long and truncated, refine the "
            "fetch to the relevant section and re-run."
        )

    return "\n".join([
        head, "",
        f"Source: {url}",
        f"Quote submitted: \"{quote.strip()[:300]}\"",
        advice + (para_note or ""),
        "",
        "Best-matching passage in source:",
        f"> {evidence[:600]}" if evidence else "> (none)",
        "",
        "Verification is conversation-bound: this result holds for the "
        "document as fetched now, at the URL above.",
    ])


def _tier1_section(markdown: str) -> str:
    """Extract the Tier 1 section of an authoritative-sources file.

    Captures from the heading containing "Tier 1" up to the next heading of
    the same or higher level; falls back to the file's head if the layout is
    unexpected.
    """
    lines = markdown.splitlines()
    start = level = None
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,4})\s+.*tier\s*1", line, re.IGNORECASE)
        if m:
            start, level = i, len(m.group(1))
            break
    if start is None:
        return markdown[:4000]
    for j in range(start + 1, len(lines)):
        m = re.match(r"^(#{1,4})\s", lines[j])
        if m and len(m.group(1)) <= level:
            return "\n".join(lines[start:j]).strip()
    return "\n".join(lines[start:]).strip()


@mcp.tool()
def search_sources(query: str, tribunal: str = "") -> str:
    """Route a research query to the right Tier 1 search entry points.

    Returns, for the tribunal concerned (detected from the query, or passed
    explicitly), the Tier 1 section of its authoritative-sources reference:
    the databases to search, in order of authority, with the suite's guidance
    on each. Use fetch_document on the entry points to run the search, and
    verify anything found before citing it.

    This tool does not search a private index: it routes to the courts' own
    databases, which are the only places a search result counts.
    """
    if not query.strip():
        return "Provide a query."
    if tribunal:
        trib = _resolve_tribunal(tribunal)
        if trib is None:
            return _unknown_tribunal_message(tribunal)
        slugs = [trib.slug]
        note = f"Tribunal set explicitly to '{trib.slug}'."
    else:
        ranked = detect_tribunals(query)
        slugs = [s for s, _ in ranked[:2]]
        note = (
            "Detected from query: " + ", ".join(slugs)
            if slugs
            else "No tribunal detected — showing the cross-tribunal entry point. "
            "Pass `tribunal` to get a specific court's source hierarchy."
        )

    out = [f"# Search routing for: {query}", "", note, ""]
    for slug in slugs:
        trib = _resolve_tribunal(slug)
        if trib is None:
            continue
        got = _read_tribunal_file(trib, "references/authoritative-sources.md")
        if got is None:
            continue
        text = got[1]
        section = _tier1_section(text)
        out += [f"## {slug} — Tier 1 sources", section, ""]
    out += [
        "## Cross-tribunal",
        "The ICC Legal Tools Database (https://www.legal-tools.org) indexes "
        "documents across international criminal jurisdictions, with a "
        "Persistent URL per document.",
        "",
        "Results found through any of these entry points are still citations "
        "to verify: existence, content, paragraph — in that order.",
    ]
    return "\n".join(out)


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
    got = _read_tribunal_file(trib, rel)
    if got is None:
        return f"No file '{rel}' in tribunal '{slug}'."
    return got[1]


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
    got = _read_tribunal_file(trib, rel)
    if got is None:
        return f"(no {rel} for {trib.slug})"
    return got[1].strip()


def _unknown_tribunal_message(slug: str) -> str:
    known = ", ".join(_tribunals())
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
        got = _read_tribunal_file(trib, "references/verification-workflow.md")
        if got is not None:
            return (
                f"Work the {trib.slug} fallback ladder (from "
                f"{trib.slug}/references/verification-workflow.md):\n\n"
                + got[1].strip()
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


def _extract_pdf_text(url: str, data: bytes, ctype: str) -> str:
    """Extract text from a fetched PDF, with graceful degradation.

    Court PDFs are the primary-source format for most tribunals, so pull the
    text where possible. Scanned/image-only PDFs yield little or no text — in
    that case say so plainly rather than returning an empty result.
    """
    size = len(data)
    try:
        from pypdf import PdfReader  # type: ignore
    except ModuleNotFoundError:
        return (
            f"Retrieved a PDF from {url} ({size} bytes, content-type: {ctype}).\n"
            "Text extraction is unavailable because `pypdf` is not installed "
            "(see mcp/pyproject.toml). Capture the document number, date, "
            "chamber, title, and cited paragraph(s) from the PDF directly."
        )

    import io

    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception as exc:
        return (
            f"Retrieved a PDF from {url} ({size} bytes) but could not parse it: "
            f"{exc}\nIt may be encrypted or malformed. Open the source directly "
            "and capture the document number, date, chamber, and paragraphs."
        )

    pages = reader.pages
    chunks: list[str] = []
    for i, page in enumerate(pages, start=1):
        try:
            chunks.append(page.extract_text() or "")
        except Exception:
            chunks.append("")
    text = "\n\n".join(c.strip() for c in chunks if c.strip())

    header = (
        f"Retrieved PDF from {url} ({size} bytes, {len(pages)} page(s)).\n"
        "Verify the document number, date, chamber, and the exact paragraph "
        "numbering against this text before citing — extracted layout can drop "
        "or reflow paragraph markers.\n\n"
    )
    if not text.strip():
        return (
            header
            + "No extractable text — this is likely a scanned/image-only PDF. "
            "Treat it as not machine-readable: confirm the citation from the "
            "source document itself or via the tribunal's fallback ladder."
        )
    if len(text) > 60_000:
        text = text[:60_000] + "\n\n…[truncated; refine to the relevant pages/section]"
    return header + text


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
