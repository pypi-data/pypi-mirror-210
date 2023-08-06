import re
from typing import Iterator, NamedTuple

from bs4 import BeautifulSoup, PageElement
from markdown import markdown
from markdownify import markdownify


class Segment(NamedTuple):
    id: str
    markup: str


def standardize_toc(content: str):
    return markdown(
        text=f"[TOC]\n\n{content}",
        extensions=["toc", "footnotes", "tables"],
    )


def find_next_heading(element: PageElement) -> PageElement:
    """Assumes heading elements, i.e. `<h1>`-`<h6>` and a terminal `<hr>` tag."""
    next_element = element.find_next_sibling()
    while next_element is not None:
        if next_element.name and next_element.name.startswith("h"):
            return next_element
        next_element = next_element.find_next_sibling()
    raise Exception("Could not find next heading.")


def slice_segments(html: str, start: PageElement, end: PageElement) -> Iterator[dict]:
    """Slice each segment of `html` based on a heading tag i.e. `<h1>`-`<h6>` and/or a
    terminal `<hr>` tag marked as `end`."""
    while start != end:
        next = find_next_heading(start)
        s = html.find(str(start)) + len(str(start))
        e = html.find(str(next))
        yield {"id": start["id"], "markup": html[s:e].strip()}  # type: ignore
        start = next


def treeify_toc(toc_ul: PageElement, segments: list[Segment]) -> list[dict]:
    def parse_ul(ul):
        result = []
        for li in ul.find_all("li", recursive=False):
            id = li.next_element["href"].removeprefix("#")
            segment = next(s for s in segments if s.id == id)
            snippet = markdownify(segment.markup).strip()
            item = dict(
                id=id,
                heading=re.sub(r"\s+", " ", li.next_element.text).strip(),
                snippet=snippet,
            )
            nested_ul = li.find("ul")
            if nested_ul:
                item["children"] = parse_ul(nested_ul)  # type: ignore
            result.append(item)
        return result

    return parse_ul(toc_ul)


def create_outline(html: BeautifulSoup) -> list[dict]:
    """Assumes html contains a table of contents (toc) mapped to headings.
    Will create a tree structure where each node of the tree will contain
    compartamentalized segments.

    Examples:
        >>> from pathlib import Path
        >>> from bs4 import BeautifulSoup
        >>> from markdown_toc_segments import create_outline, standardize_toc
        >>> f = Path().cwd() / "temp.md"
        >>> content = standardize_toc(f.read_text())
        >>> html = BeautifulSoup(content, "html.parser")
        >>> outline = create_outline(html)
        >>> len(outline[0]['children']) == 4
        True

    Args:
        html (BeautifulSoup): The BeautifulSoup object made to parse HTML

    Returns:
        list[dict]: Each result contains the snippet in markdown format with its heading
    """

    header_tags = html("h1")
    if not header_tags:
        raise Exception("Need at least one <h1> tag.")

    terminal_tags = html("hr")
    if not terminal_tags:
        raise Exception("Need at least one <hr> tag.")

    generated_toc = html("div", class_="toc")
    if not generated_toc:
        raise Exception("Missing table of contents.")

    return treeify_toc(
        toc_ul=generated_toc[-1]("ul")[0],
        segments=[
            Segment(**data)
            for data in slice_segments(
                html=str(html),
                start=header_tags[0],
                end=terminal_tags[-1],
            )
        ],
    )
