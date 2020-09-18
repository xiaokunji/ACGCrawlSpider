# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class AcgItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pic = Field()
    picName = Field()
    acgName = Field()
    totalPage = Field()
    id = Field()
