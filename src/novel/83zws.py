import os
import platform
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import random
import re
from typing import Callable, List, Tuple
import requests
from bs4 import BeautifulSoup
import time

href: str = 'https://www.83zws.com'


def get_html(url: str) -> str:
    return requests.get(url).text


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
        elif not re.compile(r'第\s*[0-9一二三四五六七八九十]+\s*章').match(t):
            return t, False
        else:
            return t, True

    url = f'{href}{book_url}'
    soup = BeautifulSoup(get_html(url), 'html.parser')
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
        soup = BeautifulSoup(get_html(url), 'html.parser')
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
    print(f'crawling {chapter_name}: {href}{chapter_url} ...')
    time.sleep(random.uniform(1, 3))
    content = get_chapter_content(href, chapter)
    return content


def main(book_url: str):
    title, chapters = get_chapters(href, book_url)

    cpu_cores = multiprocessing.cpu_count()
    with ThreadPoolExecutor(max_workers=cpu_cores * 2) as executor:
        futures = [executor.submit(task, href, chapter) for chapter in chapters]
        with open(f'{get_download_dir()}/{title}.txt', 'w', encoding='utf-8') as f:
            for future in futures:
                f.write(future.result())


if __name__ == '__main__':
    book_url = ''
    main(book_url)
