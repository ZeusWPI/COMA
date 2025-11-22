"""Render document types to other document types."""

import logging
from typing import List, Tuple

import pandoc
import weasyprint
from pandoc.types import Meta, Pandoc, Plain

logging.getLogger("weasyprint").addHandler(logging._StderrHandler())
logging.getLogger("weasyprint").setLevel(logging.INFO)


def plumbum_call_with_log(self, args):
    """Wrap LocalCommand() for logging pandoc stdout/stderr."""
    res = self.run(args)
    print(f"{self.executable} {' '.join(args)}:")
    print(f"  status: {res[0]}")
    print(f"  stdout: {res[1]}")
    print(f"  stderr: {res[2]}")
    return res[1]


pandoc.plumbum.machines.LocalCommand.__call__ = plumbum_call_with_log


def render_md_to_html(md: str, inline: bool = False) -> str:
    """
    Render the markdown string `md` to html.

    The html is not wrapped in any enclosing tag.
    It is just a stream of elements (`<p>`, `<h1>`, ...).

    Use the `inline` parameter to return the children of the first, topmost
    element.

    Math expressions `$expr$` and `$$expr$$` are rendered as svg's.
    """
    doc: Tuple(Meta, List[Pandoc]) = pandoc.read(
        source=md,
        format="markdown",
    )
    if inline:
        doc[1][0] = Plain(*doc[1][0])
    html = pandoc.write(
        doc=doc,
        format="html",
        options=[
            "--lua-filter=pandoc-filters/math2svg.lua",
            "--mathml",  # Fallback
        ],
    )
    return html


def render_html_to_pdf(html: str) -> bytes:
    """Render the html string `html` to an in-memory pdf file."""
    html_doc = weasyprint.HTML(string=html)
    pdf_doc: weasyprint.Document = html_doc.render()
    return pdf_doc.write_pdf()
