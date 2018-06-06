import scrapy


class WanDouJiaSpider(scrapy.Spider):
    name = 'wdj_spider'
    allowed_domain = ['wandoujia.com']
    start_urls = ['http://www.wandoujia.com/category/app']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse_catagory)

    def parse_catagory(self, response):
        selector = response.xpath('//div[@class="child-cate"]/a/@href')
        for url in selector.extract():
            print('catagory: ', url)
            yield scrapy.Request(url, callback=self.parse_app_list)

    def parse_app_list(self, response):
        selector = response.xpath('//li[@data-pn]')
        for app_sel in selector:
            yield {
                'app_name': app_sel.xpath(
                    './/div[@class="app-desc"]/h2/a/text()'
                    ).extract_first(),
                'appClass': app_sel.xpath(
                    './/a[@class="tag-link"]/text()').extract_first(),
                'apkName': app_sel.xpath('@data-pn').extract_first(),
            }

        next_list = response .xpath(
            '//a[@class="page-item next-page "]/@href').extract_first()
        if next_list is not None:
            yield scrapy.Request(next_list, callback=self.parse_app_list)


if __name__ == "__main__":
    a = True
    print('a is None?', a is None)
    print("all right.")
