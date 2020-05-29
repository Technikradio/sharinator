import markdown
from pyembed.markdown import PyEmbedMarkdown


def compile_markdown(markdown_sources: str):
    """
    This function is designed to be a small shortcut for converting md sources to html (required by the caching).
    :param markdown_sources: The markdown source code
    :return: The HTML code
    """
    loaded_extensions = [
        "markdown.extensions.extra",
        "markdown.extensions.admonition",
        "markdown.extensions.toc",
        "markdown.extensions.wikilinks",
        "markdown_checklist.extension",
        "superscript",
        "subscript",
        PyEmbedMarkdown(),
    ]
    return markdown.markdown(markdown_sources, extensions=loaded_extensions)