from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Union, Set, Dict, Any

from bs4 import Tag


def remove_prefix(text, prefix) -> str:
    if text.startswith(prefix):
        return text[len(prefix) :]
    raise ValueError(f'String: "{text}" does not contain prefix: "{prefix}"')


def clean_contents(html: Tag) -> str:
    return str(html.string.strip())

# We use multiple inheritance to make dumping dead simple
class TruthMeter(str, Enum):
    PANTS_FIRE = "pants-fire"
    FALSE = "false"
    MOSTLY_FALSE = "barely-true"
    HALF_TRUE = "half-true"
    MOSTLY_TRUE = "mostly-true"
    TRUE = "true"

    @staticmethod
    def values() -> Set[str]:
        return {item.value for item in TruthMeter}


class FlipMeter(str, Enum):
    NO_FLIP = "no-flip"
    HALF_FLIP = "half-flip"
    FULL_FLOP = "full-flop"

    @staticmethod
    def values() -> Set[str]:
        return {item.value for item in FlipMeter}


@dataclass(eq=True, frozen=True)
class PolitifactPost:
    """Meta"""

    post_author: str
    meta_description: str
    statement: str
    evaluation: Union[TruthMeter, FlipMeter]
    author: str
    date_posted: str

    @staticmethod
    def from_html_frag(html: Tag) -> PolitifactPost:
        args: Dict[str, Any] = {}
        args["post_author"] = clean_contents(html.find("a", class_="m-statement__name"))
        args["meta_description"] = clean_contents(
            html.select_one("div.m-statement__desc")
        )
        args["statement"] = clean_contents(html.select_one(".m-statement__quote a"))

        evaluation = html.select_one("div.m-statement__meter img")["alt"]

        if evaluation in TruthMeter.values():
            args["evaluation"] = TruthMeter(evaluation)
        elif evaluation in FlipMeter.values():
            args["evaluation"] = FlipMeter(evaluation)
        else:
            raise ValueError(
                f"Evaluation: Alt tag {evaluation} is not a known truth meter value or flip meter value"
            )

        footer = clean_contents(html.select_one(".m-statement__footer"))
        [author, date] = footer.strip().split(" • ")
        args["author"] = remove_prefix(author, "By ").strip()
        args["date_posted"] = date.strip()

        return PolitifactPost(**args)


# TODO: Add author validation