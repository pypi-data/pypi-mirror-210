from dataclasses import dataclass
from typing import Iterator, NamedTuple, Self

from bs4 import BeautifulSoup, Tag
from markdown import markdown

from .footnote import Footnote
from .segment import Segment
from .utils import cull_space, get_ul_sibling


class Item(NamedTuple):
    """Each item is a heading-divided, i.e. `<h1>` to `<h6>`, segment of a
    markdown-based document. The division is in accordance with a
    table of contents. Each `label` contains the name of the entry.

    Each `segment` contains non-overlapping text that forms part of the label,
    i.e. there should be no segments subsumed by an item since the terminal point of
    each item is the next heading element.

    The `text` is a markdown-variant of the segment's html markup... with footnotes
    inlined. Each `Item` can contain child nodes.

    This is automatically generated from each `Outline`'s `handle_toc()` function.
    """

    id: str
    label: str
    segment: Segment
    text: str
    children: list[Self]


@dataclass
class Outline:
    """Based on html markup as a string that contains headings like `<h1>` to `<h6>`
    and terminating in an `<hr>`, create a nested structure of segments whereby
    each segment consists of a heading and its included markup.

    Examples:
        >>> from pathlib import Path
        >>> from markdown_toc_segments import Outline
        >>> f = Path().cwd() / "temp.md"
        >>> obj = Outline(raw=f.read_text())
        >>> len(obj.segments)
        13
        >>> len(obj.footnotes)
        5
        >>> len(obj.tree)
        1
        >>> len(obj.tree[0])
        5
        >>> len(obj.items) # same number of segments
        13

    """

    raw: str

    def __post_init__(self):
        self.md = markdown(
            text=f"[TOC]\n\n{self.raw}",
            extensions=["toc", "footnotes", "tables"],
        )
        self.soup = BeautifulSoup(self.md, "html.parser")
        self.segments = Segment.collect(html=self.soup)
        self.footnotes = Footnote.collect(html=self.soup)
        self.tree = list(self.handle_toc(self.soup("div", class_="toc")[0]("ul")[0]))
        self.items: list[Item] = list(self.flatten(self.tree))

    def handle_toc(self, ul: Tag) -> Iterator[Item]:
        """Recursive function on each <ul> tag found in the table of contents.

        Args:
            ul (Tag): This should act on the table of contents `<div>` that is created by using the markdown table of content's extension.

        Yields:
            Iterator[Item]: Each item is supplied with relevant segment and footnotes.
        """  # noqa: E501
        for li in ul("li", recursive=False):
            entry: Tag = li("a")[0]
            toc_id = entry["href"].removeprefix("#")  # type: ignore
            ul_next = get_ul_sibling(entry)
            children = list(self.handle_toc(ul_next)) if ul_next else []
            matched_segment = next(s for s in self.segments if s.id == toc_id)
            inlined_footnotes = matched_segment.set_inline_footnotes(self.footnotes)
            yield Item(
                id=toc_id,
                label=cull_space(entry.text),
                segment=matched_segment,
                text=inlined_footnotes,
                children=children,
            )

    def flatten(self, items: list[Item]):
        """Removes the hierarchy from the tree-based items."""
        for item in items:
            yield item
            if item.children:
                yield from self.flatten(item.children)
