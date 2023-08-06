import re

from bs4 import Tag


def cull_space(text: str):
    return re.sub(r"\s+", " ", text).strip()


def get_ul_sibling(item: Tag) -> Tag | None:
    if (
        item.next_sibling
        and isinstance(item.next_sibling, Tag)
        and item.next_sibling.name == "ul"
    ):
        return item.next_sibling
    return None
