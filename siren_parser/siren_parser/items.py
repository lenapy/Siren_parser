# -*- coding: utf-8 -*-
from scrapy.item import Item, Field


class SirenParserItem(Item):
    name = Field()
    year_of_issue = Field()
    country = Field()
    genre = Field()
    quality = Field()
    duration = Field()
    translation = Field()
    update_date = Field()
    last_episode = Field()
    season = Field()
    link_to_watch_online = Field()
    description = Field()
    type = Field()
    photo = Field()

