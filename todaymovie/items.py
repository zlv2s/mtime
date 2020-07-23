# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy import Field


class MovieItem(scrapy.Item):
    id = Field()
    movie_title_cn = Field()
    movie_title_en = Field()
    release_date = Field()
    movie_type = Field()
    director = Field()
    duration = Field()
    actors = Field()
    plots = Field()
