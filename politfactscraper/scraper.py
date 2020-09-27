import bs4
import requests
import time
import random
import json
import dataclasses
import enum
from pprint import pp
from datetime import date

from post import PolitifactPost
from typing import List


def unique(l: List) -> List:
    return list(dict.fromkeys(l))


def generate_url(page_no: int) -> str:
    return f"https://www.politifact.com/factchecks/list/?page={page_no}&category=truth-o-meter"


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def main():
    posts = []
    # for i in range(1, 2):
    for i in range(1, 185 + 1):
        url = generate_url(i)
        print(url)

        today = date.today()

        html = requests.get(url).text

        with open(f"html/{today}-page-{i}.html", "w") as f:
            f.write(html)

        soup = bs4.BeautifulSoup(html, "lxml")
        tags = soup.find_all("li", class_="o-listicle__item")

        posts.extend([PolitifactPost.from_html_frag(tag) for tag in tags])

        if i % 10 == 0:
            with open("data.json", "w", encoding="utf8") as f:
                json.dump(posts, f, cls=EnhancedJSONEncoder, ensure_ascii=False)

        time.sleep(3.0 + random.random() * 2)

    posts = unique(posts)
    print(posts)
    print(len(posts))
    with open("data.json", "w", encoding="utf8") as f:
        json.dump(posts, f, cls=EnhancedJSONEncoder, ensure_ascii=False)


if __name__ == "__main__":
    main()