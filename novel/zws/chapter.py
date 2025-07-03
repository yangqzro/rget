from typing import List, Tuple

from bs4 import BeautifulSoup

from client.http import Http
from scheduler.concurrent_scheduler import ConScheduler
from shared.book import whether_append_chapter, whether_append_content
from shared.filepath import get_download_dir, join

href: str = "https://www.83zws.com"
http = Http(base_uri=href)


def get_chapters(book_id: int, classify_id: int) -> Tuple[str, List[Tuple[str, str]]]:
    soup = BeautifulSoup(http.get(f"/book/{classify_id}/{book_id}/").text, "html.parser")
    title = soup.select_one("div#info h1").text.strip()

    chapters: List[Tuple[str, str]] = []
    for c in soup.select('a[rel="chapter"]:not([title])'):
        t, ok = whether_append_chapter(c.text)
        if "dd" in c.decode_contents() and ok:
            chapters.append((t, c.attrs.get("href").strip()))

    return title, chapters


def get_chapter_content(chapter: Tuple[str, str]) -> str:
    chapter_name, chapter_uri = chapter

    def get_content(chapter_uri: str) -> List[str]:
        soup = BeautifulSoup(http.get(chapter_uri).text, "html.parser")
        content: List[str] = []
        for c in soup.select_one("div#content div#booktxt"):
            t, ok = whether_append_content(c.text)
            if c.name == "p" and ok:
                content.append(t)

        a = soup.select_one("a#next_url")
        has_next, next_url = "下一页" in a.text.strip(), a.attrs.get("href")
        if has_next:
            content.extend(get_content(next_url))
        return content

    return "\n".join([chapter_name] + get_content(chapter_uri)) + "\n\n"


def crawl(book_id: int, classify_id: int):
    def task(href: str, chapter: Tuple[str, str]) -> str:
        chapter_name, chapter_uri = chapter
        content = get_chapter_content(chapter)
        print(f"crawled {chapter_name}: {href}{chapter_uri} ...")
        return content

    title, chapters = get_chapters(book_id, classify_id)
    with ConScheduler() as executor:
        futures = [executor.submit(task, href, chapter) for chapter in chapters]
        with open(join(get_download_dir(), f"{title}.txt"), "w", encoding="utf-8") as f:
            for future in futures:
                f.write(future.result())
