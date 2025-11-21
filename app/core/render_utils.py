"""Does things."""

import pandoc


def render_md_to_html(md: str, math_renderer: str = "--mathml"):
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
    doc = pandoc.read(
        source=md,
        format="markdown",
    )
    html = pandoc.write(
        doc=doc,
        format="html",
        options=[math_renderer],
    )
    return html
