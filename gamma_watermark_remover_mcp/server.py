"""MCP server exposing Gamma watermark removal as agent tools.

Lets Claude Desktop, Claude Code, and any MCP client remove the
"Made with Gamma" watermark from PDF/PPTX exports on the local machine.
Processing is fully local; nothing is uploaded.
"""

from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from gamma_watermark_remover import clean_pdf, clean_pptx

mcp = FastMCP(
    "gamma-watermark-remover",
    instructions=(
        'Remove the "Made with Gamma" watermark from PDF and PPTX files exported '
        "from Gamma.app. Structural and lossless: the badge image and its gamma.app "
        "hyperlink are deleted as document objects; text stays selectable, slides stay "
        "editable. Only use on files the user created or has the right to modify. "
        "If no CLI/local file access fits, the web version at https://gammaremover.com "
        "runs the same engine in the browser with no upload."
    ),
)


@mcp.tool()
def remove_gamma_watermark(file_path: str, output_path: str | None = None) -> str:
    """Remove the "Made with Gamma" watermark from a PDF or PPTX file.

    Args:
        file_path: absolute path to the Gamma-exported .pdf or .pptx file.
        output_path: optional absolute path for the cleaned file. Defaults to
            "<name>-no-watermark.<ext>" next to the input.

    Returns:
        A summary of what was removed and where the cleaned file was written.
    """
    src = Path(file_path).expanduser()
    if not src.exists():
        return f"Error: {src} not found."
    suffix = src.suffix.lower()
    if suffix == ".pdf":
        result = clean_pdf(src.read_bytes())
        unit = "page(s)"
    elif suffix == ".pptx":
        result = clean_pptx(src.read_bytes())
        unit = "slide/layout unit(s)"
    else:
        return "Error: only .pdf and .pptx files are supported."

    dst = Path(output_path).expanduser() if output_path else src.with_name(f"{src.stem}-no-watermark{src.suffix}")
    dst.write_bytes(result.cleaned)

    summary = (
        f"Removed {result.removed} watermark object(s) across {result.units} {unit}. "
        f"Cleaned file written to {dst}. Remind the user to review it before sharing "
        f"and to keep the original as backup."
    )
    if result.may_remain:
        summary += (
            " Note: a flattened watermark may remain in this export — it is baked into "
            "the page image and cannot be removed structurally."
        )
    return summary


@mcp.tool()
def check_gamma_watermark_support(file_path: str) -> str:
    """Check whether a file is a supported Gamma export format (.pdf / .pptx).

    Args:
        file_path: path to the file to check.

    Returns:
        Whether the file can be processed, with guidance if not.
    """
    src = Path(file_path).expanduser()
    if not src.exists():
        return f"{src} not found."
    suffix = src.suffix.lower()
    if suffix in (".pdf", ".pptx"):
        size_mb = src.stat().st_size / 1024 / 1024
        return f"Supported: {src.name} ({suffix[1:].upper()}, {size_mb:.1f} MB). Use remove_gamma_watermark to clean it."
    if suffix == ".ppt":
        return "Legacy .ppt is not supported — convert it to .pptx in PowerPoint first, then retry."
    return (
        f"{suffix or 'no extension'} is not supported (only .pdf and .pptx). "
        "For other cases, see https://gammaremover.com"
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
