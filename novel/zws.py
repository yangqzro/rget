import re
from typing import Callable, List, Tuple

from bs4 import BeautifulSoup

import client
import scheduler
from shared import get_download_dir, join

href: str = "https://www.83zws.com"
http = client.Http()


def get_chapters(href: str, book_uri: str) -> Tuple[str, List[Tuple[str, str]]]:
    def whether_to_append(text: str, handler: Callable[[str], str]) -> Tuple[str, bool]:
        t = handler(text)
        if not t:
            return t, False
        elif not re.compile(r"(第\s*[0-9一二三四五六七八九十]+\s*[章话回]|番外|\d+)").match(t):
            return t, False
        else:
            return t, True

    url = f"{href}{book_uri}"
    soup = BeautifulSoup(http.get(url), "html.parser")
    title = soup.select_one("div#info h1").text.strip()

    chapters: List[Tuple[str, str]] = []
    for x in soup.select('a[rel="chapter"]:not([title])'):
        t, ok = whether_to_append(x.text, lambda x: x.strip())
        if "dd" in x.decode_contents() and ok:
            chapters.append((t, x.attrs.get("href").strip()))

    return title, chapters


def get_chapter_content(href: str, chapter: Tuple[str, str]) -> str:
    chapter_name, chapter_uri = chapter

    def whether_to_append(text: str, handler: Callable[[str], str]) -> Tuple[str, bool]:
        t = handler(text)
        if not t:
            return t, False
        elif "本章完" in text:
            return t, False
        elif re.compile(r"第\s*[0-9一二三四五六七八九十]+\s*[章话回]").match(t):
            return t, False
        else:
            return t, True

    def get_content(href: str, chapter_uri: str) -> List[str]:
        url = f"{href}{chapter_uri}"
        soup = BeautifulSoup(http.get(url), "html.parser")
        content: List[str] = []
        for c in soup.select_one("div#content div#booktxt"):
            t, ok = whether_to_append(c.text, lambda x: x.strip())
            if c.name == "p" and ok:
                content.append(t)

        a = soup.select_one("a#next_url")
        has_next, next_url = "下一页" in a.text.strip(), a.attrs.get("href")
        if has_next:
            content.extend(get_content(href, next_url))
        return content

    return "\n".join([chapter_name] + get_content(href, chapter_uri)) + "\n\n"


def crawl(book_id: int, classify_id: int):
    def task(href: str, chapter: Tuple[str, str]) -> str:
        chapter_name, chapter_uri = chapter
        content = get_chapter_content(href, chapter)
        print(f"crawled {chapter_name}: {href}{chapter_uri} ...")
        return content

    book_uri = f"/book/{classify_id}/{book_id}/"
    title, chapters = get_chapters(href, book_uri)

    with scheduler.ConScheduler() as executor:
        futures = [executor.submit(task, href, chapter) for chapter in chapters]
        with open(join(get_download_dir(), f"{title}.txt"), "w", encoding="utf-8") as f:
            for future in futures:
                f.write(future.result())
