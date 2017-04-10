import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

from siren_parser import settings, items


class SerialsLoader(ItemLoader):
    default_item_class = items.SirenParserItem
    default_output_processor = TakeFirst()


class SerialsKinoProfiSpider(CrawlSpider):
    name = "serials_kp"
    start_urls = settings.START_URLS_KP
    allowed_domains = settings.ALLOWED_DOMAINS_KP
    rules = (

             Rule(LxmlLinkExtractor(allow='/serialy/')),
             Rule(LxmlLinkExtractor(allow='/serialy/zarubezhnye/')),
             Rule(LxmlLinkExtractor(allow='/serialy/russkie/')),
             Rule(LxmlLinkExtractor(allow='-season'), callback='parse_item', follow=True))

    def parse_item(self, response):

        sel = scrapy.Selector(response)
        ldr = SerialsLoader(items.SirenParserItem(), sel)

        photo = ldr.get_xpath('/html/body/div[2]/main/div/div/div[2]/div/div[2]/div[3]/div[1]/div[3]/div[1]/div/a/img')
        clean_link = (photo[0].partition('<img src="'))[2].partition('" ')
        photo_clean = clean_link[0]
        ldr.add_value('photo', photo_clean)

        name = (clean_link[2].partition('title="'))[2].partition('" ')
        name_clean = name[0]
        ldr.add_value('name', name_clean)

        season = \
            ldr.get_xpath(
                '/html/body/div[2]/main/div/div/div[2]/div/div[2]/div[3]/div[1]/div[3]/div[1]/div/span/em[1]/text()')
        season_clean = (season[0].partition(' сезон'))[0]
        ldr.add_value('season', season_clean)

        last_episode = \
            ldr.get_xpath(
                '/html/body/div[2]/main/div/div/div[2]/div/div[2]/div[3]/div[1]/div[3]/div[1]/div/span/em[2]/text()')
        last_episode_clean = (last_episode[0].partition(' серия'))[0]
        ldr.add_value('last_episode', last_episode_clean)

        description = \
            ldr.get_xpath('/html/body/div[2]/main/div/div/div[2]/div/div[2]/div[3]/div[1]/div[3]/div[2]/text()')
        desc = description[0].partition('\r\n\t\t\t')
        ldr.add_value('description', desc[2])

        time = \
            ldr.get_xpath('/html/body/div[2]/main/div/div/div[2]/div/div[2]/div[3]/div[1]/div[3]/p/span[2]/time/text()')
        ldr.add_value('update_date', time[0])

        country = ldr.get_xpath('/html/body/div[2]/main/div/div/div[2]/div/div[2]/div[3]/div[1]/div[3]/span[1]/text()')
        ldr.add_value('country', country[0])

        genre = ldr.get_xpath('/html/body/div[2]/main/div/div/div[2]/div/div[2]/div[3]/div[1]/div[3]/span[2]/a/text()')
        ldr.add_value('genre', genre[0])

        year = (name_clean.partition(' ('))[2].partition(')')
        ldr.add_value('year_of_issue', year[0])

        ldr.add_value('link_to_watch_online', response.url)
        ldr.add_value('type', 1)

        return ldr.load_item()








