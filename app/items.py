# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst

class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AppItem(scrapy.Item):
    apk_name = scrapy.Field(output_processor=TakeFirst())
    app_class = scrapy.Field(output_processor=TakeFirst())
    app_name = scrapy.Field(output_processor=TakeFirst())