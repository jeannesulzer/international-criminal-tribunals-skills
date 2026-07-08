# Using the guides with Claude — three ways in

Three ways to put this suite to work, from the simplest to the most advanced.
None of the first two requires any coding. **If in doubt, start with
Option 1** — it takes about three minutes and works on every Claude plan.

Whichever way in, the rule is the same everywhere: no citation without the
official document behind it. If a source cannot be found, the output says so.

---

## Option 1 — No installation: a Claude Project

*Works on every plan, including free. About three minutes.*

Treat a guide as a set of documents you hand to Claude.

1. **Create a project.** On [claude.ai](https://claude.ai), open **Projects**
   and create one — name it after the tribunal, say "ICC research".
2. **Download the guide's files.** Open the tribunal's folder in this
   repository (for example [`icc/`](icc/)). Download `SKILL.md` and the files
   in `references/` — the download button is at the top right of each file's
   page.
3. **Upload them** to the project as knowledge documents.
4. **Work inside that project.** Claude has the method, the source hierarchy,
   and the citation rules in front of it for every conversation there.

The limit of this route: the method applies inside that project only, because
the files are there — not automatically across all your chats.

## Option 2 — Install as a Skill

*Requires a Claude Pro, Max, Team, or Enterprise plan.*

A Skill is the same content, but Claude activates it by itself whenever the
conversation touches that tribunal — mention *Bemba* or *Duch* and the right
discipline applies without your asking.

1. **Download the repository.** Click the green **Code** button on the
   repository's front page, then **Download ZIP**, and unzip it.
2. **Zip one tribunal folder on its own.** Right-click the folder (for
   example `icc`) and compress it, producing `icc.zip`. The folder itself
   must sit at the root of the archive — zip the folder, not the files
   inside it, or Claude will not find `SKILL.md`.
3. **Upload it.** On claude.ai: **Settings → Customize → Skills →
   + Create skill**, and upload the zip.
4. **Repeat** for each tribunal you work with.

The guides are also published ready to use on
[Lawvable](https://www.lawvable.com).

## Option 3 — The MCP server

*For users comfortable with a terminal. Claude Desktop or Claude Code.*

The [Model Context Protocol](https://modelcontextprotocol.io) server in
[`mcp/`](mcp/) plugs the whole suite in at once — the thirteen guides, plus
citation verification, jurisprudence search, and primary-source retrieval as
tools the model calls directly.

One warning saves most of the confusion: in the Claude app, **do not use
Settings → Connectors** — that section is for remote servers on the public
internet. This server runs locally on your own machine and registers through
**Settings → Developer** instead.

**On Claude Desktop:**

1. **Install Python** 3.10 or newer from
   [python.org/downloads](https://www.python.org/downloads/) if you do not
   have it.
2. **Download the repository** (green **Code** button → **Download ZIP**) and
   unzip it somewhere permanent — the server reads the guides from inside
   this folder, so do not move it afterwards.
3. **Install the dependencies.** In a terminal:
   `pip3 install "mcp[cli]" httpx pypdf`
4. **Register the server.** In Claude Desktop, open **Settings → Developer →
   Edit Config**. In the `claude_desktop_config.json` file that opens, add
   (replacing the path with wherever you unzipped):

   ```json
   {
     "mcpServers": {
       "international-justice": {
         "command": "python3",
         "args": ["/absolute/path/to/international-criminal-tribunals-skills/mcp/server.py"]
       }
     }
   }
   ```

5. **Quit Claude completely and reopen it.** Closing the window is not
   enough — quit the application.
6. **Test it.** Ask Claude: *"Which tribunals does the international-justice
   server cover?"* If it lists thirteen, everything works.

**On Claude Code:**

```bash
claude mcp add international-justice -- python /absolute/path/to/mcp/server.py
```

Full tool documentation and design notes are in [`mcp/README.md`](mcp/README.md).
If none of this section made sense to you, use Option 1 or 2 — the MCP server
adds convenience, not exclusivity.

---

If an installation step fails or the instructions do not match what you see,
please open an issue on this repository — installation reports are how these
instructions improve.
