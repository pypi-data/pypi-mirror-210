import re
from typing import Iterator, NamedTuple, Self

from bs4 import BeautifulSoup, PageElement
from markdownify import markdownify

from .footnote import Footnote


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


def set_fn_pattern(id: str) -> re.Pattern:
    return re.compile(rf"\[{id.removeprefix('fn:')}\]\(#{id}\)")


class Segment(NamedTuple):
    """Extracted text from an html document between a given table-of-content
    based heading."""

    id: str
    markup: str

    @classmethod
    def collect(cls, html: BeautifulSoup) -> list[Self]:
        header_tags = html("h1")
        if not header_tags:
            raise Exception("Need at least one <h1> tag.")

        terminal_tags = html("hr")
        if not terminal_tags:
            raise Exception("Need at least one <hr> tag.")

        generated_toc = html("div", class_="toc")
        if not generated_toc:
            raise Exception("Missing table of contents.")

        return [
            cls(**data)
            for data in slice_segments(
                html=str(html),
                start=header_tags[0],
                end=terminal_tags[-1],
            )
        ]

    @property
    def snippet_footnote_ids(self) -> list[str]:
        """Use the `markup`'s footnote tags to get the ids. These will
        later be used to determine what to replace in the markup itself
        during `set_inline_footnotes()`."""
        ids = []
        for fn in BeautifulSoup(self.markup, "html.parser")("sup"):
            ids.append(fn("a", class_="footnote-ref")[0]["href"].removeprefix("#"))
        return ids

    @property
    def md(self):
        """Create a markdown version of the `markup`."""
        return markdownify(self.markup).strip()

    def set_inline_footnotes(self, document_footnotes: list[Footnote]):
        """Move the relevant footnotes for each segment within the markdown variant
        of the `markup`. The `%% {text} %%` pattern will be used to insert the
        footnote's value."""
        content = self.md
        for id in self.snippet_footnote_ids:
            pattern = set_fn_pattern(id)
            for note in document_footnotes:
                if id == note.id:
                    inline_fn = note.markup.removesuffix("\xa0↩")
                    content = pattern.sub(f"%% {inline_fn} %%", content)
                    break
        return content
