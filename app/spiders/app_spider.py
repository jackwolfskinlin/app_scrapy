import scrapy


class AppSpider(scrapy.Spider):
    name = 'app_spider'
    start_urls = ['http://sj.qq.com/myapp/']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse_catagory)
    
    def parse_catagory(self, response):
        ctg = response.xpath('//div[@class="ind-catelist"]')
        for link in ctg.xpath('.//dd/a[@href]'):
            url = response.urljoin(link.xpath('@href').extract_first())
            print('catagory: ', url)
            yield scrapy.Request(url, callback=self.parse_app_list)

    def parse_app_list(self, response):
        page = response.xpath('//div[@class="app-info-desc"]')
        for link in page.xpath('.//a[@class="name ofh"]'):
            url = response.urljoin(link.xpath('@href').extract_first())
            yield scrapy.Request(url, callback=self.parse_app_msg)

    def parse_app_msg(self, response):
        yield {
            'app_name': response.xpath("//div[@class='det-name-int']/text()").extract_first(),
            'appClass': response.xpath("//a[@class='det-type-link']/text()").extract_first(),
            'apkName': response.xpath("//a[@class='det-down-btn']/@apk").extract_first(),
        }

if __name__ == "__main__":
    print("all right.")