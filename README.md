# Data Scraping / Spider

---

## What is Data Scraping / Spider?
Data scraping (or spidering) is basically when you build a small bot that visits a website, reads the HTML structure, and automatically pulls out the info you care about like product names, prices, reviews, or whatever data you need. Instead of manually copy-pasting stuff from a site like Amazon, your spider does the heavy lifting for you. Think of it like a smart digital intern that never gets tired and can browse hundreds of pages in minutes.

---

## What’s the purpose of it?
The main goal of scraping is to collect data at scale so you can analyze it, compare stuff, build datasets, or power another system. For example, you might scrape product prices to compare competitors, gather reviews for sentiment analysis, or collect quotes for a text analysis project. In short, scraping turns messy web pages into structured data you can actually work with like JSON or CSV so it becomes useful for analytics, dashboards, machine learning, or just straight-up research.

---

## How does it work?
At a basic level, a spider sends an HTTP request to a webpage, gets back the HTML response, then parses that HTML using selectors (CSS or XPath) to grab specific elements. In tools like Scrapy, the spider starts from a URL, extracts the data inside the `parse()` function, and then optionally follows pagination links to keep crawling. So the flow is simple but powerful: request → response → parse → extract → yield → repeat. It’s like telling your bot, “Go here, grab this part, then follow that next button and do it again.”

---

## What should we pay attention to (strategy & technical side)?
Strategically, you need to understand the website structure first inspect the HTML, identify stable selectors, and make sure the data is actually in the static HTML (not fully rendered by JavaScript). From a technical perspective, you need clean selectors, proper scoping (use `product.css()` not `response.css()` inside loops), handle pagination, clean your data, and avoid being blocked by anti bot systems. Also, don’t just scrape blindly think about what you’ll analyze later. If you’ll calculate averages, clean the currency. If you’ll compare brands, normalize the names. Scraping isn’t just about grabbing data it’s about grabbing the *right* data in a way that makes analysis smooth later.

---

## Short description of each file in project structure
In this small Scrapy project, `scrapy.cfg` is the root config file that tells Scrapy where your project settings live. Inside the main `tutorial/` folder, `items.py` defines the structure of the data you want to collect (like product_name and product_price). `middlewares.py` is where you can hook into the request/response process for example, modifying headers or handling special behaviors. `pipelines.py` is used to process scraped data after extraction—like cleaning, validating, or saving it to a database. `settings.py` controls global behavior like user agents, download delays, and concurrency. Then inside `spiders/`, `amazon_spider.py` is your custom spider for scraping Amazon search results, while `quotes_spider.py` is probably a practice spider for scraping quotes from a demo site basically your training ground before hitting real world targets.

---

## How to run this

Clone this repository to your computer:

    ```bash
    git clone https://github.com/zerocool979/Data-Engineering.git
    cd Data-Engineering
    ```

Create and Activate a Virtual Environment:

  - **Windows** :

    ```bash
    python -m venv venv
    .\venv\Scripts\Activate
    ```

  - **Mac/Linux**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

Install Dependencies

    ```bash
    pip install scrapy lxml
    ```

Run Spider Basic commands:

    ```bash
    scrapy crawl amazon
    ```
    ```bash
    scrapy crawl amazon -o items.json
    ```
    ```bash
    scrapy crawl amazon -o items.csv
    ```

If the Spider Doesn't Work
Check the spider list:

    ```bash
    scrapy list
    ```
