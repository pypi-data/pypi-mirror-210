from typing import NamedTuple, Self

from bs4 import BeautifulSoup


class Footnote(NamedTuple):
    id: str
    markup: str

    @classmethod
    def collect(cls, html: BeautifulSoup) -> list[Self]:
        return [
            cls(id=note["id"], markup=note.text.strip())  # type: ignore
            for note in html.select("div.footnote ol li")
        ]
