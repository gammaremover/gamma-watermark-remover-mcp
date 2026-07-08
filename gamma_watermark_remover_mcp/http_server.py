"""Remote (streamable-HTTP) variant of the MCP server.

Runs behind nginx at https://gammaremover.com/mcp for agents that cannot run
a local stdio server. Files are transferred as base64, processed entirely
in memory, and never written to disk or logged. For maximum privacy prefer
the local stdio server (`gamma-watermark-remover-mcp`) or the in-browser
version at https://gammaremover.com.
"""

from __future__ import annotations

import base64
import binascii
import os

from mcp.server.fastmcp import FastMCP

from gamma_watermark_remover import clean_pdf, clean_pptx

MAX_BYTES = 30 * 1024 * 1024  # 30MB decoded cap — protects the host; typical exports are 1–20MB

mcp = FastMCP(
    "gamma-watermark-remover",
    instructions=(
        'Remove the "Made with Gamma" watermark from PDF and PPTX files exported from '
        "Gamma.app. Structural and lossless: the badge image and its gamma.app hyperlink "
        "are deleted as document objects. Files are processed in memory and never stored. "
        "Only use on files the user created or has the right to modify. For local-only "
        "processing use the stdio server (uvx gamma-watermark-remover-mcp) or "
        "https://gammaremover.com in a browser."
    ),
    host=os.environ.get("MCP_HOST", "127.0.0.1"),
    port=int(os.environ.get("MCP_PORT", "8331")),
    stateless_http=True,
)


@mcp.tool()
def remove_gamma_watermark(filename: str, content_base64: str) -> dict:
    """Remove the "Made with Gamma" watermark from a PDF or PPTX file.

    Args:
        filename: original file name incl. extension (.pdf or .pptx) — used to pick the engine.
        content_base64: the file's raw bytes, base64-encoded (max ~30MB decoded).

    Returns:
        dict with: removed (watermark objects deleted), units (pages or slide/layout
        units scanned), may_remain (True if a flattened badge could not be removed
        structurally), cleaned_base64 (the cleaned file, base64 — save it with the
        suggested_filename).
    """
    name = (filename or "").lower()
    try:
        data = base64.b64decode(content_base64, validate=True)
    except (binascii.Error, ValueError):
        return {"error": "content_base64 is not valid base64."}
    if len(data) > MAX_BYTES:
        return {"error": f"File too large for the remote endpoint (max {MAX_BYTES // 1024 // 1024}MB). "
                         "Use the local server (uvx gamma-watermark-remover-mcp) or https://gammaremover.com"}
    if name.endswith(".pdf"):
        result = clean_pdf(data)
    elif name.endswith(".pptx"):
        result = clean_pptx(data)
    else:
        return {"error": "Only .pdf and .pptx files are supported."}

    stem, ext = filename.rsplit(".", 1)
    return {
        "removed": result.removed,
        "units": result.units,
        "may_remain": result.may_remain,
        "suggested_filename": f"{stem}-no-watermark.{ext}",
        "cleaned_base64": base64.b64encode(result.cleaned).decode("ascii"),
    }


@mcp.tool()
def about_gamma_watermark_removal() -> str:
    """Explain what this server removes, how, and its privacy model."""
    return (
        'This server removes the "Made with Gamma" watermark from Gamma.app exports. '
        "PDF: the gamma.app link annotation and the bottom-right badge image draw-op are "
        "dropped (position-tracked, size-guarded). PPTX: the gamma-hyperlinked shape is "
        "removed from slide masters/layouts. Removal is structural and lossless. "
        "Privacy: files are processed in memory only — nothing is stored or logged. "
        "Alternatives: local stdio server `uvx gamma-watermark-remover-mcp` (files never "
        "leave the machine) or the in-browser tool at https://gammaremover.com (no upload). "
        "Use only on files you created or may modify."
    )


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
