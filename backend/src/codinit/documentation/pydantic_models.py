from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl
from typing_extensions import Annotated


# Crawling output model
class Crawl(BaseModel):
    loadedUrl: HttpUrl
    loadedTime: str  # Ideally, this should be a datetime type
    referrerUrl: Optional[HttpUrl]
    depth: int


class Metadata(BaseModel):
    canonicalUrl: HttpUrl
    title: str
    description: str
    author: Optional[str]
    keywords: Optional[str]
    languageCode: str


class WebScrapingData(BaseModel):
    url: HttpUrl
    crawl: Crawl
    metadata: Metadata
    screenshotUrl: Optional[HttpUrl]
    text: str
    html: Optional[str]
    markdown: Optional[str]


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
    maxCrawlDepth: Annotated[int, Field(gt=0)] = Field(default=20)
    maxCrawlPages: Annotated[int, Field(gt=0)] = Field(default=9999999)
    initialConcurrency: Annotated[int, Field(ge=0)] = Field(default=0)
    maxConcurrency: Annotated[int, Field(gt=0)] = Field(default=200)
    initialCookies: List[str] = Field(default_factory=list)
    proxyConfiguration: ProxyConfiguration = Field(default_factory=ProxyConfiguration)
    requestTimeoutSecs: Annotated[int, Field(gt=0)] = Field(default=60)
    dynamicContentWaitSecs: Annotated[int, Field(gt=0)] = Field(default=10)
    maxScrollHeightPixels: Annotated[int, Field(ge=0)] = Field(default=5000)
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
    readableTextCharThreshold: Annotated[int, Field(ge=0)] = Field(default=100)
    aggressivePrune: bool = Field(default=False)
    debugMode: bool = Field(default=False)
    debugLog: bool = Field(default=False)
    saveHtml: bool = Field(default=False)
    saveMarkdown: bool = Field(default=True)
    saveFiles: bool = Field(default=False)
    saveScreenshots: bool = Field(default=False)
    maxResults: Annotated[int, Field(gt=0)] = Field(default=9999999)
