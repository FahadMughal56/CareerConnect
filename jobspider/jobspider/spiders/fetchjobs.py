import scrapy


class FetchjobsSpider(scrapy.Spider):
    name = "fetchjobs"
    allowed_domains = ["abc"]
    start_urls = ["https://abc"]

    def parse(self, response):
        pass
