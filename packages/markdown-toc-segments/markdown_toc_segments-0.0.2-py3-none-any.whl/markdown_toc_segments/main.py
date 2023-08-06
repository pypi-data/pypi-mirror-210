from dataclasses import dataclass
from typing import Iterator, NamedTuple, Self

from bs4 import BeautifulSoup, Tag
from markdown import markdown

from .footnote import Footnote
from .segment import Segment
from .utils import cull_space, get_ul_sibling


class Item(NamedTuple):
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
        self.toc = list(self.unpack_ul(self.soup("div", class_="toc")[0]("ul")[0]))

    def unpack_ul(self, ul: Tag) -> Iterator[Item]:
        for li in ul("li", recursive=False):
            entry: Tag = li("a")[0]
            toc_id = entry["href"].removeprefix("#")  # type: ignore
            ul_next = get_ul_sibling(entry)
            children = list(self.unpack_ul(ul_next)) if ul_next else []
            matched_segment = next(s for s in self.segments if s.id == toc_id)
            inlined_footnotes = matched_segment.set_inline_footnotes(self.footnotes)
            yield Item(
                id=toc_id,
                label=cull_space(entry.text),
                segment=matched_segment,
                text=inlined_footnotes,
                children=children,
            )
