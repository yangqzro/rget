import re
from typing import Callable, Tuple


def whether_append_chapter(name: str, handle: Callable[[str], str] = lambda t: t.strip()) -> Tuple[bool, str]:
    t = handle(name)
    regex = r"(第\s*[0-9一二三四五六七八九十]+[章话回]|简章|番外|\d+\.?|ep\s*\d+)"
    if not t:
        return t, False
    elif not re.compile(regex, flags=re.I).match(t):
        return t, False
    else:
        return t, True


def whether_append_content(content: str, handle: Callable[[str], str] = lambda t: t.strip()) -> Tuple[bool, str]:
    t = handle(content)
    if not t:
        return t, False
    elif "本章完" in t:
        return t, False
    elif re.compile(r"第\s*[0-9一二三四五六七八九十]+\s*[章话回]").match(t):
        return t, False
    else:
        return t, True
