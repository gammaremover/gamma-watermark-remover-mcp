# Gamma Watermark Remover — MCP Server

[![PyPI](https://img.shields.io/pypi/v/gamma-watermark-remover-mcp?color=8b3dff&label=PyPI)](https://pypi.org/project/gamma-watermark-remover-mcp/)
[![MCP](https://img.shields.io/badge/MCP-server-8b3dff)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-8b3dff.svg)](LICENSE)
[![Web version](https://img.shields.io/badge/Web%20version-gammaremover.com-8b3dff)](https://gammaremover.com)

![Gamma Watermark Remover MCP server — AI agents remove the Made with Gamma badge](assets/banner.webp)

An [MCP](https://modelcontextprotocol.io) server that lets **Claude Desktop, Claude Code, and any MCP client** remove the **"Made with Gamma"** watermark from PDF and PowerPoint (.pptx) files exported from [Gamma.app](https://gamma.app) — right on your machine. Just ask:

> *"remove the gamma watermark from ~/Downloads/deck.pdf"*

Removal is **structural and lossless**: the badge image and its gamma.app hyperlink are deleted as document objects. Nothing is re-rendered, nothing is uploaded.

## What is the Gamma Watermark Remover MCP Server?

The Gamma Watermark Remover MCP server connects the [Model Context Protocol](https://modelcontextprotocol.io) to a document-cleaning engine, so AI assistants can remove the "Made with Gamma" watermark from Gamma.app exports on your behalf. Instead of opening a separate tool, you stay in your conversation: point Claude at an exported PDF or PowerPoint file, and the badge — a discrete document object with a gamma.app hyperlink — is deleted structurally. Your text stays selectable, your slides stay editable, and with the local server nothing ever leaves your machine.

This is the same engine behind the [gammaremover.com](https://gammaremover.com) web app and the [gamma-watermark-remover CLI](https://github.com/gammaremover/gamma-watermark-remover), packaged for the MCP ecosystem: Claude Desktop, Claude Code, Cursor, Windsurf, and any other MCP-compatible client.

## Setup

### Claude Desktop

Add to `claude_desktop_config.json` (Settings → Developer → Edit Config):

```json
{
  "mcpServers": {
    "gamma-watermark-remover": {
      "command": "uvx",
      "args": ["gamma-watermark-remover-mcp"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add gamma-watermark-remover -- uvx gamma-watermark-remover-mcp
```

### Any other MCP client

The server speaks stdio. Command: `uvx gamma-watermark-remover-mcp` (or `pipx run gamma-watermark-remover-mcp`, or `pip install gamma-watermark-remover-mcp` then `gamma-watermark-remover-mcp`).

### Remote endpoint (no install at all)

A hosted streamable-HTTP endpoint is available at **`https://gammaremover.com/mcp`** for agents that can't run a local server. It accepts file content as base64 (≤30MB), processes **in memory only** — nothing is stored or logged. For maximum privacy prefer the local stdio server above or the [in-browser tool](https://gammaremover.com).

## Tools

| Tool | What it does |
|------|--------------|
| `remove_gamma_watermark(file_path, output_path?)` | Cleans a `.pdf`/`.pptx` export; writes `<name>-no-watermark.<ext>` by default and reports exactly how many watermark objects were removed |
| `check_gamma_watermark_support(file_path)` | Checks whether a file is a supported format before processing |

If the badge was flattened into the page image (rare), the result honestly says a watermark may remain instead of silently failing.

## How it works

This server wraps the [gamma-watermark-remover](https://github.com/gammaremover/gamma-watermark-remover) Python library:

- **PDF** (`pypdf`): drops link annotations targeting `gamma.app`/`gamma.to` and the draw op of the small bottom-right badge image (transformation-matrix tracked, size-guarded so backgrounds are never touched)
- **PPTX** (`python-pptx`): removes the gamma-hyperlinked shape from slide masters/layouts (where Gamma stores it) and slides

## FAQ

**Which MCP clients does this work with?**
Any client that speaks MCP over stdio or streamable HTTP: Claude Desktop, Claude Code, Cursor, Windsurf, Cline, and others. The stdio variant is the default; the hosted endpoint at `https://gammaremover.com/mcp` covers clients that cannot spawn local processes.

**Do my files get uploaded?**
With the local stdio server, never — processing happens on your machine. The hosted endpoint receives file content (base64, up to 30MB), processes it in memory only, and stores nothing.

**What file formats are supported?**
PDF and PowerPoint (.pptx) exports from Gamma.app. Legacy .ppt must be converted to .pptx first.

**What happens if the watermark cannot be removed?**
Some exports flatten the badge into the page image. The tool reports `may_remain` honestly instead of degrading your file with pixel inpainting.

**Is this free?**
Yes — MIT-licensed open source, no account, no quota.

## Related Tools

- **Web app** (browser-based, no upload): [gammaremover.com](https://gammaremover.com)
- **CLI + Python library**: [gamma-watermark-remover](https://github.com/gammaremover/gamma-watermark-remover)
- **Local web UI**: [gamma-watermark-remover-webui](https://github.com/gammaremover/gamma-watermark-remover-webui)
- **MCP server** for Claude and AI agents: [gamma-watermark-remover-mcp](https://github.com/gammaremover/gamma-watermark-remover-mcp)
- **Agent skill** for Claude Code and OpenClaw: [gamma-watermark-remover-skill](https://github.com/gammaremover/gamma-watermark-remover-skill)
- **Curated Gamma resources**: [awesome-gamma](https://github.com/gammaremover/awesome-gamma)

## Responsible use

Only process files you created or have the right to modify. Keep originals as backup and review cleaned files before sharing. Gamma's official watermark-free route is its [paid plan](https://gammaremover.com/en/blog/gamma-free-vs-pro-watermark/).

## License

MIT
