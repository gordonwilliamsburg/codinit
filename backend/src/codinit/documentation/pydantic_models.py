from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl
from typing_extensions import Annotated


# Crawling output model
class Crawl(BaseModel):
    loadedUrl: HttpUrl
    loadedTime: str  # Ideally, this should be a datetime type
    referrerUrl: Optional[HttpUrl] = None
    depth: int

    def model_dump(self):
        return {
            "loadedUrl": str(self.loadedUrl),
            "loadedTime": self.loadedTime,
            "referrerUrl": str(self.referrerUrl) if self.referrerUrl else None,
            "depth": self.depth,
        }


class Metadata(BaseModel):
    canonicalUrl: HttpUrl
    title: str
    description: str
    author: Optional[str] = None
    keywords: Optional[str] = None
    languageCode: str

    def model_dump(self):
        return {
            "canonicalUrl": str(self.canonicalUrl),
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "keywords": self.keywords,
            "languageCode": self.languageCode,
        }


class WebScrapingData(BaseModel):
    url: HttpUrl
    crawl: Crawl
    metadata: Metadata
    screenshotUrl: Optional[HttpUrl] = None
    text: str
    html: Optional[str] = None
    markdown: Optional[str] = None

    def model_dump(self):
        return {
            "url": str(self.url),
            "crawl": self.crawl.model_dump(),  # Assuming Crawl also has model_dump()
            "metadata": self.metadata.model_dump(),  # Assuming Metadata also has model_dump()
            "screenshotUrl": str(self.screenshotUrl) if self.screenshotUrl else None,
            "text": self.text,
            "html": self.html,
            "markdown": self.markdown,
        }


# Crawling input models
class StartUrl(BaseModel):
    url: HttpUrl


class ProxyConfiguration(BaseModel):
    useApifyProxy: bool = True


class RunInput(BaseModel):
    startUrls: List[StartUrl]
    crawlerType: str = Field(default="cheerio")
    includeUrlGlobs: List[str] = Field(default_factory=list)
    excludeUrlGlobs: List[str] = Field(default_factory=list)
    ignoreCanonicalUrl: bool = Field(default=False)
    maxCrawlDepth: Annotated[int, Field(gt=0)] = 20
    maxCrawlPages: Annotated[int, Field(gt=0)] = 9999999
    initialConcurrency: Annotated[int, Field(ge=0)] = 0
    maxConcurrency: Annotated[int, Field(gt=0)] = 200
    initialCookies: List[str] = Field(default_factory=list)
    proxyConfiguration: ProxyConfiguration = Field(default_factory=ProxyConfiguration)
    requestTimeoutSecs: Annotated[int, Field(gt=0)] = 60
    dynamicContentWaitSecs: Annotated[int, Field(gt=0)] = 10
    maxScrollHeightPixels: Annotated[int, Field(ge=0)] = 5000
    removeElementsCssSelector: str = """nav, footer, script, style, noscript, svg,
[role=\"alert\"],
[role=\"banner\"],
[role=\"dialog\"],
[role=\"alertdialog\"],
[role=\"region\"][aria-label*=\"skip\" i],
[aria-modal=\"true\"]"""
    removeCookieWarnings: bool = Field(default=True)
    clickElementsCssSelector: str = Field(default='[aria-expanded="false"]')
    htmlTransformer: Optional[str] = Field(default="readableText")
    readableTextCharThreshold: Annotated[int, Field(ge=0)] = 100
    aggressivePrune: bool = Field(default=False)
    debugMode: bool = Field(default=False)
    debugLog: bool = Field(default=False)
    saveHtml: bool = Field(default=False)
    saveMarkdown: bool = Field(default=True)
    saveFiles: bool = Field(default=False)
    saveScreenshots: bool = Field(default=False)
    maxResults: Annotated[int, Field(gt=0)] = 9999999


# library
class Library(BaseModel):
    libname: str
    links: List[str]
    exclude_dirs: Optional[List[str]] = None
    lib_desc: Optional[str] = None
