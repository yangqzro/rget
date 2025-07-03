import re
from typing import List, Tuple
import warnings

from bs4 import BeautifulSoup

from client.http import Http
from scheduler.concurrent_scheduler import ConScheduler
from shared.book import whether_append_chapter, whether_append_content
from shared.filepath import get_download_dir, join

href: str = "https://www.ciweimao.com"
http = Http(base_uri=href, options={"auto_referer": True})
codecs_http = Http(base_uri="http://localhost:3000")


def decrypt(content: str = "", keys: list[str] = [], access_key: str = "") -> str:
    encrypted = {"content": content, "keys": keys, "accessKey": access_key}
    data = {"kind": "novel", "website": "ciweimao", "data": encrypted}
    return codecs_http.post("/decrypt", json=data).json().get("data")


def get_chapters(book_id: int) -> Tuple[str, List[Tuple[str, str]]]:
    book_url = f"/book/{book_id}/"
    soup = BeautifulSoup(http.get(book_url).text, "html.parser")
    title = soup.select_one("h1.title").text.split(" ")[0].strip()

    chapter_url = "/chapter/get_chapter_list_in_chapter_detail"
    soup = BeautifulSoup(http.post(chapter_url, data={"book_id": book_id}).text, "html.parser")
    chapters: List[Tuple[str, str]] = []
    for v in soup.select("div.book-chapter-box")[1:-1]:
        for c in v.select("a"):
            t, ok = whether_append_chapter(c.text, lambda t: re.compile(r"\s*：").sub(" ", t).strip())
            if not ok:
                continue
            href = re.compile(r"(https?:)?\/\/www\.ciweimao\.com").sub("", c.attrs.get("href").strip())
            chapters.append((t, href))

    return title, chapters


def get_chapter_content(chapter: Tuple[str, str]) -> str:
    chapter_name, chapter_uri = chapter

    chapter_id = chapter_uri.split("/")[-1].split("_")[-1]
    data = {"chapter_id": chapter_id}
    chapter_access_key: dict = http.post("/chapter/ajax_get_session_code", data=data).json().get("chapter_access_key")
    data.update({"chapter_access_key": chapter_access_key})
    resp: dict = http.post("/chapter/get_book_chapter_detail_info", data=data).json()
    if resp.get("code") != 100000:
        warnings.warn(f"{chapter_name}: {resp.get("tip")}", UserWarning)
        return ""

    decrypted = decrypt(resp.get("chapter_content"), resp.get("encryt_keys"), chapter_access_key)
    content: List[str] = []
    for c in BeautifulSoup(decrypted, "html.parser").select("p"):
        t, ok = whether_append_content(c.text, lambda t: re.compile(r"\s*2bF6Bu\s*").sub("", t).strip())
        if ok:
            content.append(t)

    return "\n".join([chapter_name] + content) + "\n\n"


def crawl(book_id: int):
    def task(href: str, chapter: Tuple[str, str]) -> str:
        chapter_name, chapter_uri = chapter
        content = get_chapter_content(chapter)
        print(f"crawled {chapter_name}: {href}{chapter_uri} ...")
        return content

    title, chapters = get_chapters(book_id)
    with ConScheduler(max_workers=1) as executor:
        futures = [executor.submit(task, href, chapter) for chapter in chapters]
        with open(join(get_download_dir(), f"{title}.txt"), "w", encoding="utf-8") as f:
            for future in futures:
                f.write(future.result())
