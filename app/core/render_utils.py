"""Render document types to other document types."""

from typing import List, Tuple

import pandoc
import weasyprint
from pandoc.types import Meta, Pandoc, Plain


def render_md_to_html(
    md: str,
    inline: bool = False,
    math_renderer: str = "--mathml",
) -> str:
    """
    Render the markdown string `md` to html.

    The html is not wrapped in any enclosing tag.
    It is just a stream of elements (`<p>`, `<h1>`, ...).

    The `math_renderer` argument can be set to any of:
    - `--mathml`
    - `--mathjax`
    - `--katex`
    The default is "--mathml", which has no external dependencies, except for a
    somewhat modern browser.
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
        options=[math_renderer],
    )
    return html


def render_html_to_pdf(html: str) -> bytes:
    """Render the html string `html` to an in-memory pdf file."""
    html_doc = weasyprint.HTML(string=html)
    pdf_doc: weasyprint.Document = html_doc.render()
    return pdf_doc.write_pdf()
