# -*- coding: utf-8 -*-
import scrapy
from todaymovie.items import MovieItem


class MovieSpiderSpider(scrapy.Spider):
    name = 'movie_spider'
    allowed_domains = ['mtime.com']
    start_urls = ['http://theater.mtime.com/China_Sichuan_Province_Chengdu/']

    def parse(self, response):
        hot_movies = response.xpath('//div[@id="hotplayContent"]/div[1]')
        all_links = hot_movies.xpath(
            './/a[re:test(@href,"http://movie.mtime.com/\d+/$")][@title]/@href').getall()
        # all_links = hot_movies.xpath('.//a[re:test(@href,"http://movie.mtime.com/\d+/$")]/@href').getall()
        # all_links = list(set(all_links))
        for link in all_links:
            yield scrapy.Request(url=link, callback=self.parse_movie)

    def parse_movie(self, response):
        id = response.url.split('/')[-2]
        movie_title_cn = response.xpath(
            '//div[@class="db_head"]//h1/text()').get()
        movie_title_en = response.xpath('//p[@class="db_enname"]/text()').get()
        director = response.xpath(
            '//dl[@class="info_l"]/dd[1]//a//text()').getall()
        duration = response.xpath(
            '//span[@property="v:runtime"]/text()').get() or '未知'
        movie_type = response.xpath('//a[@property="v:genre"]/text()').getall()
        release_date = response.xpath(
            '//a[@property="v:initialReleaseDate"]/text()').get()
        actors = response.xpath(
            '//dl[@class="main_actor"]/dd/a/@title').getall()
        plots = response.xpath(
            '//dt[@pan="M14_Movie_Overview_PlotsSummary"]/p[1]/text()').get()

        movie = MovieItem()
        movie['id'] = id
        movie['movie_title_cn'] = movie_title_cn
        movie['movie_title_en'] = movie_title_en
        movie['movie_type'] = movie_type
        movie['release_date'] = release_date
        movie['director'] = director
        movie['duration'] = duration
        movie['actors'] = actors
        movie['plots'] = plots
        yield movie
