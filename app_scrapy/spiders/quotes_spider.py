import scrapy


class QuoteScrapy(scrapy.Spider):
    name = 'quotes'

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
#            'http://quotes.toscrape.com/page/2/',           
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        for quote in response.xpath("//div[@class='quote']"):
            yield {
                'text': quote.xpath('span[@class="text"]/text()').extract_first(),
                'author': quote.xpath('small[@class="author"]/text()').extract_first(),
                'tags': quote.xpath('div[@class="tags"]/a[@class="tag"]/text()').extract(),
            }
        
        next_page = response.xpath('//li[@class="next"]/a/@href').extract_first()
        if next_page is not None:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, callback=self.parse)
            #yield response.follow(next_url, self.parse)


if __name__ == "__main__":
    print("all right.")