import os
import platform
from concurrent.futures import ThreadPoolExecutor
import re
import threading
from typing import Callable, List, Tuple, TypeVar, TypeVarTuple
import requests
from bs4 import BeautifulSoup

href: str = 'https://www.83zws.com'

TaskParams = TypeVarTuple("TaskParams")
TaskResult = TypeVar("TaskResult")


class ConControl:
    def __init__(self, max_concurrent: int):
        self._semaphore = threading.Semaphore(max_concurrent)

    def call(self, callback: Callable[[*TaskParams], TaskResult], *args: *TaskParams) -> TaskResult:
        with self._semaphore:
            return callback(*args)


class Http:
    def __init__(self):
        self._session = requests.Session()

    def get(self, url: str) -> str:
        return self._session.get(url).text


http = Http()


def get_download_dir() -> str:
    system = platform.system()
    if system == 'Windows':
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:  # Linux / macOS
        return os.path.expanduser('~/Downloads')


def get_chapters(href: str, book_url: str) -> Tuple[str, List[Tuple[str, str]]]:
    def whether_to_append(text: str, handler: Callable[[str], bool]) -> Tuple[str, bool]:
        t = handler(text)
        if not t:
            return t, False
        elif not re.compile(r'(第\s*[0-9一二三四五六七八九十]+\s*章|番外|\d+)').match(t):
            return t, False
        else:
            return t, True

    url = f'{href}{book_url}'
    soup = BeautifulSoup(http.get(url), 'html.parser')
    title = soup.select_one('div#info h1').text.strip()

    chapters: List[Tuple[str, str]] = []
    for x in soup.select('a[rel="chapter"]:not([title])'):
        t, ok = whether_to_append(x.text, lambda x: x.strip())
        if 'dd' in x.decode_contents() and ok:
            chapters.append((t, x.attrs.get('href').strip()))

    return title, chapters


def get_chapter_content(href: str, chapter: Tuple[str, str]) -> str:
    chapter_name, chapter_url = chapter

    def whether_to_append(text: str, handler: Callable[[str], bool]) -> Tuple[str, bool]:
        t = handler(text)
        if not t:
            return t, False
        elif '本章完' in text:
            return t, False
        elif re.compile(r'第\s*[0-9一二三四五六七八九十]+\s*章').match(t):
            return t, False
        else:
            return t, True

    def get_content(href: str, chapter_url: str) -> List[str]:
        url = f'{href}{chapter_url}'
        soup = BeautifulSoup(http.get(url), 'html.parser')
        content: List[str] = []
        for c in soup.select_one('div#content div#booktxt'):
            t, ok = whether_to_append(c.text, lambda x: x.strip())
            if c.name == 'p' and ok:
                content.append(t)

        a = soup.select_one('a#next_url')
        has_next, next_url = '下一页' in a.text.strip(), a.attrs.get('href')
        if not has_next:
            return content

        for n in get_content(href, next_url):
            t, ok = whether_to_append(n, lambda x: x.strip())
            if ok:
                content.append(t)
        return content

    return '\n'.join([chapter_name] + get_content(href, chapter_url)) + '\n\n'


def task(href: str, chapter: Tuple[str, str]) -> str:
    chapter_name, chapter_url = chapter
    content = get_chapter_content(href, chapter)
    print(f'crawled {chapter_name}: {href}{chapter_url} ...')
    return content


def main(book_url: str):
    title, chapters = get_chapters(href, book_url)

    cpu_cores = os.cpu_count()
    cc = ConControl(8)
    with ThreadPoolExecutor(max_workers=cpu_cores + 4) as executor:
        futures = [executor.submit(cc.call, task, href, chapter)
                   for chapter in chapters]
        with open(os.path.join(get_download_dir(), f"{title}.txt"), 'w', encoding='utf-8') as f:
            for future in futures:
                f.write(future.result())


if __name__ == '__main__':
    book_url = ''
    main(book_url)
