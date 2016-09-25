# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DictionaryScraperItem(scrapy.Item):
    # define the fields for your item here like:
    word 		= scrapy.Field()
    sentences 	= scrapy.Field()
    mnemonics 	= scrapy.Field()
    meanings 	= scrapy.Field()
    origin		= scrapy.Field()
    reference   = scrapy.Field()

    