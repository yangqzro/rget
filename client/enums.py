from enum import Enum


class OS(Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    UBUNTU = "Ubuntu"
    CHROME_OS = "Chrome OS"
    MAC_OS_X = "Mac OS X"
    ANDROID = "Android"
    IOS = "iOS"


class Browser(Enum):
    GOOGLE = "Google"
    CHROME = "Chrome"
    FIREFOX = "Firefox"
    EDGE = "Edge"
    OPERA = "Opera"
    SAFARI = "Safari"
    ANDROID = "Android"
    YANDEX_BROWSER = "Yandex Browser"
    SAMSUNG_INTERNET = "Samsung Internet"
    OPERA_MOBILE = "Opera Mobile"
    MOBILE_SAFARI = "Mobile Safari"
    FIREFOX_MOBILE = "Firefox Mobile"
    FIREFOX_IOS = "Firefox iOS"
    CHROME_MOBILE = "Chrome Mobile"
    CHROME_MOBILE_IOS = "Chrome Mobile iOS"
    MOBILE_SAFARI_UI_WKWEBVIEW = "Mobile Safari UI/WKWebView"
    EDGE_MOBILE = "Edge Mobile"
    DUCKDUCKGO_MOBILE = "DuckDuckGo Mobile"
    MIUIBROWSER = "MiuiBrowser"
    WHALE = "Whale"
    TWITTER = "Twitter"
    FACEBOOK = "Facebook"
    AMAZON_SILK = "Amazon Silk"


class Platform(Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
