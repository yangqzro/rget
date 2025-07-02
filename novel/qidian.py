import re
from typing import List, Tuple

from bs4 import BeautifulSoup
from selenium import webdriver

from client.browsers import ChromeBrowser
from client.http import Http
from scheduler.concurrent_scheduler import ConScheduler
from shared.book import whether_append_chapter, whether_append_content
from shared.filepath import get_download_dir, join

href: str = "https://www.qidian.com"
http = Http()


def get_chapters(href: str, book_uri: str) -> Tuple[str, List[Tuple[str, str]]]:
    url = f"{href}{book_uri}"
    soup = BeautifulSoup(http.get(url), "html.parser")
    title = soup.select_one("h1#bookName").text.strip()

    chapters: List[Tuple[str, str]] = []
    for x in soup.select("#allCatalog li.chapter-item a"):
        t, ok = whether_append_chapter(x.text, lambda x: x.strip())
        if not ok:
            continue
        href = re.compile(r"(https:)?\/\/www\.qidian\.com").sub("", x.attrs.get("href").strip())
        chapters.append((t, href))

    return title, chapters


def get_chapter_content(href: str, chapter: Tuple[str, str]) -> str:
    chapter_name, chapter_uri = chapter

    def get_content(href: str, chapter_uri: str) -> List[str]:
        url = f"{href}{chapter_uri}"
        soup = BeautifulSoup(http.get(url), "html.parser")
        content: List[str] = []
        for c in soup.select("main.content p"):
            t, ok = whether_append_content(c.text, lambda x: x.strip())
            if ok:
                content.append(t)
        return content

    return "\n".join([chapter_name] + get_content(href, chapter_uri)) + "\n\n"


def crawl(book_id: int):
    def task(href: str, chapter: Tuple[str, str]) -> str:
        chapter_name, chapter_uri = chapter
        content = get_chapter_content(href, chapter)
        print(f"crawled {chapter_name}: {href}{chapter_uri} ...")
        return content

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    with ChromeBrowser.open(href, options) as browser:
        http.headers.update({"User-Agent": browser.execute_script("return navigator.userAgent")})
        http.cookies.update(browser.get_cookies())

    title, chapters = get_chapters(href, f"/book/{book_id}/")

    with ConScheduler() as executor:
        futures = [executor.submit(task, href, chapter) for chapter in chapters]
        with open(join(get_download_dir(), f"{title}.txt"), "w", encoding="utf-8") as f:
            for future in futures:
                f.write(future.result())
