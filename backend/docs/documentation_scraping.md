# Scraping

## Using ApifyActor

### Input

The [input schema](https://apify.com/apify/website-content-crawler/input-schema) follows:

```json
{
    "title": "Input schema for Website Content Crawler",
    "description": "Enter the start URL(s) of the website(s) to crawl, configure other optional settings, and run the Actor to crawl the pages and extract their text content.",
    "type": "object",
    "schemaVersion": 1,
    "properties": {
        "startUrls": {
            "title": "Start URLs",
            "type": "array",
            "description": "One or more URLs of the pages where the crawler will start. Note that the Actor will additionally only crawl sub-pages of these URLs. For example, for the start URL `https://www.example.com/blog`, it will crawl pages like `https://example.com/blog/article-1`, but will skip `https://example.com/docs/something-else`.",
            "editor": "requestListSources",
            "prefill": [{ "url": "https://docs.apify.com/" }]
        },
        "crawlerType": {
            "sectionCaption": "Crawler settings",
            "title": "Crawler type",
            "type": "string",
            "enum": ["playwright:chrome", "cheerio", "jsdom"],
            "enumTitles": ["Headless web browser (Chrome+Playwright)", "Raw HTTP client (Cheerio)", "Raw HTTP client with JS execution (JSDOM) (experimental!)"],
            "description": "Select the crawling engine:\n- **Headless web browser** (default) - Useful for modern websites with anti-scraping protections and JavaScript rendering. It recognizes common blocking patterns like CAPTCHAs and automatically retries blocked requests through new sessions. However, running web browsers is more expensive as it requires more computing resources and is slower. It is recommended to use at least 8 GB of RAM.\n- **Raw HTTP client** - High-performance crawling mode that uses raw HTTP requests to fetch the pages. It is faster and cheaper, but it might not work on all websites.",
            "default": "playwright:chrome"
        },
        "maxCrawlDepth": {
            "title": "Max crawling depth",
            "type": "integer",
            "description": "The maximum number of links starting from the start URL that the crawler will recursively descend. The start URLs have a depth of 0, the pages linked directly from the start URLs have a depth of 1, and so on.\n\nThis setting is useful to prevent accidental crawler runaway. By setting it to 0, the Actor will only crawl start URLs.",
            "minimum": 0,
            "default": 20
        },
        "maxCrawlPages": {
            "title": "Max pages",
            "type": "integer",
            "description": "The maximum number pages to crawl. It includes the start URLs, pagination pages, pages with no content, etc. The crawler will automatically finish after reaching this number. This setting is useful to prevent accidental crawler runaway.",
            "minimum": 0,
            "default": 9999999
        },
        ...
    }
}
```

Major speed improvement after using `cheerio` crawlerType instead of `playwright:firefox`
For same starting URL `"https://docs.apify.com/academy/web-scraping-for-beginners"`:

- `cheerio`: 27 seconds.
- `playwright:firefox`: 3:09 minutes.

### Output

Here's is how the crawling result looks in JSON format. The main page content can be found in the text field, and it only contains the valuable content, without menus and other noise:

```json
{
    "url": "https://docs.apify.com/academy/web-scraping-for-beginners",
    "crawl": {
        "loadedUrl": "https://docs.apify.com/academy/web-scraping-for-beginners",
        "loadedTime": "2023-04-05T16:26:51.030Z",
        "referrerUrl": "https://docs.apify.com/academy",
        "depth": 0
    },
    "metadata": {
        "canonicalUrl": "https://docs.apify.com/academy/web-scraping-for-beginners",
        "title": "Web scraping for beginners | Apify Documentation",
        "description": "Learn how to develop web scrapers with this comprehensive and practical course. Go from beginner to expert, all in one place.",
        "author": null,
        "keywords": null,
        "languageCode": "en"
    },
    "screenshotUrl": null,
    "text": "Skip to main content\nOn this page\nWeb scraping for beginners\nLearn how to develop web scrapers with this comprehensive and practical course. Go from beginner to expert, all in one place.\nWelcome to Web scraping for beginners, a comprehensive, practical and long form web scraping course that will take you from an absolute beginner to a successful web scraper developer. If you're looking for a quick start, we recommend trying this tutorial instead.\nThis course is made by Apify, the web scraping and automation platform, but we will use only open-source technologies throughout all academy lessons. This means that the skills you learn will be applicable to any scraping project, and you'll be able to run your scrapers on any computer. No Apify account needed.\nIf you would like to learn about the Apify platform and how it can help you build, run and scale your web scraping and automation projects, see the Apify platform course, where we'll teach you all about Apify serverless infrastructure, proxies, API, scheduling, webhooks and much more.\nWhy learn scraper development?​\nWith so many point-and-click tools and no-code software that can help you extract data from websites, what is the point of learning web scraper development? Contrary to what their marketing departments say, a point-and-click or no-code tool will never be as flexible, as powerful, or as optimized as a custom-built scraper.\nAny software can do only what it was programmed to do. If you build your own scraper, it can do anything you want. And you can always quickly change it to do more, less, or the same, but faster or cheaper. The possibilities are endless once you know how scraping really works.\nScraper development is a fun and challenging way to learn web development, web technologies, and understand the internet. You will reverse-engineer websites and understand how they work internally, what technologies they use and how they communicate with their servers. You will also master your chosen programming language and core programming concepts. When you truly understand web scraping, learning other technology like React or Next.js will be a piece of cake.\nCourse Summary​\nWhen we set out to create the Academy, we wanted to build a complete guide to modern web scraping - a course that a beginner could use to create their first scraper, as well as a resource that professionals will continuously use to learn about advanced and niche web scraping techniques and technologies. All lessons include code examples and code-along exercises that you can use to immediately put your scraping skills into action.\nThis is what you'll learn in the Web scraping for beginners course:\nWeb scraping for beginners\nBasics of data extraction\nBasics of crawling\nBest practices\nRequirements​\nYou don't need to be a developer or a software engineer to complete this course, but basic programming knowledge is recommended. Don't be afraid, though. We explain everything in great detail in the course and provide external references that can help you level up your web scraping and web development skills. If you're new to programming, pay very close attention to the instructions and examples. A seemingly insignificant thing like using [] instead of () can make a lot of difference.\nIf you don't already have basic programming knowledge and would like to be well-prepared for this course, we recommend taking a JavaScript course and learning about CSS Selectors.\nAs you progress to the more advanced courses, the coding will get more challenging, but will still be manageable to a person with an intermediate level of programming skills.\nIdeally, you should have at least a moderate understanding of the following concepts:\nJavaScript + Node.js​\nIt is recommended to understand at least the fundamentals of JavaScript and be proficient with Node.js prior to starting this course. If you are not yet comfortable with asynchronous programming (with promises and async...await), loops (and the different types of loops in JavaScript), modularity, or working with external packages, we would recommend studying the following resources before coming back and continuing this section:\nasync...await (YouTube)\nJavaScript loops (MDN)\nModularity in Node.js\nGeneral web development​\nThroughout the next lessons, we will sometimes use certain technologies and terms related to the web without explaining them. This is because the knowledge of them will be assumed (unless we're showing something out of the ordinary).\nHTML\nHTTP protocol\nDevTools\njQuery or Cheerio​\nWe'll be using the Cheerio package a lot to parse data from HTML. This package provides a simple API using jQuery syntax to help traverse downloaded HTML within Node.js.\nNext up​\nThe course begins with a small bit of theory and moves into some realistic and practical examples of extracting data from the most popular websites on the internet using your browser console. So let's get to it!\nIf you already have experience with HTML, CSS, and browser DevTools, feel free to skip to the Basics of crawling section.\nWhy learn scraper development?\nCourse Summary\nRequirements\nJavaScript + Node.js\nGeneral web development\njQuery or Cheerio\nNext up",
    "html": null,
    "markdown": "  Web scraping for beginners | Apify Documentation       \n\n[Skip to main content](#docusaurus_skipToContent_fallback)\n\nOn this page\n\n# Web scraping for beginners\n\n**Learn how to develop web scrapers with this comprehensive and practical course. Go from beginner to expert, all in one place.**\n\n* * *\n\nWelcome to **Web scraping for beginners**, a comprehensive, practical and long form web scraping course that will take you from an absolute beginner to a successful web scraper developer. If you're looking for a quick start, we recommend trying [this tutorial](https://blog.apify.com/web-scraping-javascript-nodejs/) instead.\n\nThis course is made by [Apify](https://apify.com), the web scraping and automation platform, but we will use only open-source technologies throughout all academy lessons. This means that the skills you learn will be applicable to any scraping project, and you'll be able to run your scrapers on any computer. No Apify account needed.\n\nIf you would like to learn about the Apify platform and how it can help you build, run and scale your web scraping and automation projects, see the [Apify platform course](/academy/apify-platform), where we'll teach you all about Apify serverless infrastructure, proxies, API, scheduling, webhooks and much more.\n\n## Why learn scraper development?[​](#why-learn \"Direct link to Why learn scraper development?\")\n\nWith so many point-and-click tools and no-code software that can help you extract data from websites, what is the point of learning web scraper development? Contrary to what their marketing departments say, a point-and-click or no-code tool will never be as flexible, as powerful, or as optimized as a custom-built scraper.\n\nAny software can do only what it was programmed to do. If you build your own scraper, it can do anything you want. And you can always quickly change it to do more, less, or the same, but faster or cheaper. The possibilities are endless once you know how scraping really works.\n\nScraper development is a fun and challenging way to learn web development, web technologies, and understand the internet. You will reverse-engineer websites and understand how they work internally, what technologies they use and how they communicate with their servers. You will also master your chosen programming language and core programming concepts. When you truly understand web scraping, learning other technology like React or Next.js will be a piece of cake.\n\n## Course Summary[​](#summary \"Direct link to Course Summary\")\n\nWhen we set out to create the Academy, we wanted to build a complete guide to modern web scraping - a course that a beginner could use to create their first scraper, as well as a resource that professionals will continuously use to learn about advanced and niche web scraping techniques and technologies. All lessons include code examples and code-along exercises that you can use to immediately put your scraping skills into action.\n\nThis is what you'll learn in the **Web scraping for beginners** course:\n\n*   [Web scraping for beginners](/academy/web-scraping-for-beginners)\n    *   [Basics of data extraction](/academy/web-scraping-for-beginners/data-collection)\n    *   [Basics of crawling](/academy/web-scraping-for-beginners/crawling)\n    *   [Best practices](/academy/web-scraping-for-beginners/best-practices)\n\n## Requirements[​](#requirements \"Direct link to Requirements\")\n\nYou don't need to be a developer or a software engineer to complete this course, but basic programming knowledge is recommended. Don't be afraid, though. We explain everything in great detail in the course and provide external references that can help you level up your web scraping and web development skills. If you're new to programming, pay very close attention to the instructions and examples. A seemingly insignificant thing like using `[]` instead of `()` can make a lot of difference.\n\n> If you don't already have basic programming knowledge and would like to be well-prepared for this course, we recommend taking a [JavaScript course](https://www.codecademy.com/learn/introduction-to-javascript) and learning about [CSS Selectors](https://www.w3schools.com/css/css_selectors.asp).\n\nAs you progress to the more advanced courses, the coding will get more challenging, but will still be manageable to a person with an intermediate level of programming skills.\n\nIdeally, you should have at least a moderate understanding of the following concepts:\n\n### JavaScript + Node.js[​](#javascript-and-node \"Direct link to JavaScript + Node.js\")\n\nIt is recommended to understand at least the fundamentals of JavaScript and be proficient with Node.js prior to starting this course. If you are not yet comfortable with asynchronous programming (with promises and `async...await`), loops (and the different types of loops in JavaScript), modularity, or working with external packages, we would recommend studying the following resources before coming back and continuing this section:\n\n*   [`async...await` (YouTube)](https://www.youtube.com/watch?v=vn3tm0quoqE&ab_channel=Fireship)\n*   [JavaScript loops (MDN)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Loops_and_iteration)\n*   [Modularity in Node.js](https://www.section.io/engineering-education/how-to-use-modular-patterns-in-nodejs/)\n\n### General web development[​](#general-web-development \"Direct link to General web development\")\n\nThroughout the next lessons, we will sometimes use certain technologies and terms related to the web without explaining them. This is because the knowledge of them will be **assumed** (unless we're showing something out of the ordinary).\n\n*   [HTML](https://developer.mozilla.org/en-US/docs/Web/HTML)\n*   [HTTP protocol](https://developer.mozilla.org/en-US/docs/Web/HTTP)\n*   [DevTools](/academy/web-scraping-for-beginners/data-collection/browser-devtools)\n\n### jQuery or Cheerio[​](#jquery-or-cheerio \"Direct link to jQuery or Cheerio\")\n\nWe'll be using the [**Cheerio**](https://www.npmjs.com/package/cheerio) package a lot to parse data from HTML. This package provides a simple API using jQuery syntax to help traverse downloaded HTML within Node.js.\n\n## Next up[​](#next \"Direct link to Next up\")\n\nThe course begins with a small bit of theory and moves into some realistic and practical examples of extracting data from the most popular websites on the internet using your browser console. So [let's get to it!](/academy/web-scraping-for-beginners/introduction)\n\n> If you already have experience with HTML, CSS, and browser DevTools, feel free to skip to the [Basics of crawling](/academy/web-scraping-for-beginners/crawling) section.\n\n*   [Why learn scraper development?](#why-learn)\n*   [Course Summary](#summary)\n*   [Requirements](#requirements)\n    *   [JavaScript + Node.js](#javascript-and-node)\n    *   [General web development](#general-web-development)\n    *   [jQuery or Cheerio](#jquery-or-cheerio)\n*   [Next up](#next)"
}
```
