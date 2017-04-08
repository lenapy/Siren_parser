import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

from siren_parser import settings, items


class SerialsLoader(ItemLoader):
    default_item_class = items.SirenParserItem
    default_output_processor = TakeFirst()


class SerialsKinogoSpider(CrawlSpider):
    name = "serials_kinogo"
    start_urls = settings.START_URLS
    allowed_domains = settings.ALLOWED_DOMAINS
    rules = (

             Rule(LxmlLinkExtractor(allow='_serialy/'), follow=True),
             Rule(LxmlLinkExtractor(allow='-sezon.html'), callback='parse_item', follow=True))
    # Rule(LxmlLinkExtractor(allow='/zarubezhnye_serialy/')),
    # Rule(LxmlLinkExtractor(allow='/russkye_serialy/')),
    # Rule(LxmlLinkExtractor(allow='/turezkie_serialy/')),
    def parse_item(self, response):

        sel = scrapy.Selector(response)
        ldr = SerialsLoader(items.SirenParserItem(), sel)

        title = ldr.get_xpath('/html/body/div[3]/div[1]/div/div/div[2]/div[1]/div[1]/h1/text()')
        for season in title:
            for season_number in range(len(season)):
                if season[season_number] == '(':
                    ldr.add_value('season', season[season_number + 1])
        ldr.add_value('name', title)
        country_year_genre = \
            ldr.get_xpath('/html/body/div[3]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/a/text()')

        # ldr.add_value('year_of_issue', country_year_genre[0])
        # ldr.add_value('country', country_year_genre[1])
        ldr.add_value('genre', country_year_genre[2:])

        about_video_info = ldr.get_xpath('/html/body/div[3]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]')

        duration = about_video_info[0].rpartition('Продолжительность:</b> ~00:')
        duration_cleaned = duration[2].partition(':00')

        year_of_issue = about_video_info[0].rpartition('Год выпуска:</b>')
        year_of_issue_cleaning = year_of_issue[2].partition('<br>')
        if '<a href="' in year_of_issue_cleaning[0]:
            second_cleaning_year = ((year_of_issue_cleaning[0]).rpartition('</a>'))[0].rpartition('">')
            year_of_issue_cleaned = second_cleaning_year[2]
        else:
            year_of_issue_cleaned = year_of_issue_cleaning[0]

        quality = about_video_info[0].partition('<b>Качество:</b>')
        quality_cleaned = quality[2].partition('<br>')

        translation = about_video_info[0].partition('<b>Перевод:</b>')
        translation_cleaned = translation[2].partition('<br>')

        country = about_video_info[0].rpartition('<b>Страна:</b>')
        country_cleaned = (country[2].partition('</a>'))[0].partition('">')

        description = about_video_info[0].rpartition('<!--TEnd-->')
        description_cleaned = description[2].partition('<br>')

        ldr.add_value('duration', duration_cleaned[0])
        ldr.add_value('year_of_issue', year_of_issue_cleaned)
        ldr.add_value('quality', quality_cleaned[0])
        ldr.add_value('translation', translation_cleaned[0])
        ldr.add_value('country', country_cleaned[2])
        ldr.add_value('description', description_cleaned[0])

        ldr.add_xpath('update_date', '//*[@id="dle-content"]/span/span/text()')
        ldr.add_value('link_to_watch_online', response.url)
        ldr.add_value('type', 1)

        img_link = ldr.get_xpath('/html/body/div[3]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/a[1]')
        img_link_cleaned = \
            ((img_link[0].rpartition('href='))[2].partition(' onclick'))[0].partition('"')[2].rpartition('"')
        ldr.add_value('photo', img_link_cleaned)

        about_episode_info = ldr.get_xpath('//*[@id="dle-content"]/div[1]/div[2]/div[1]/div[2]/text()')
        if 'Все' in about_episode_info[0]:
            ldr.add_value('last_episode', about_episode_info[0])
        else:
            last_episode_tuple = (about_episode_info[0].rpartition('сезон'))[2].rpartition('серия')
            ldr.add_value('last_episode', last_episode_tuple[0])


        # self.logger.debug("(parse_item) response: status=%d, URL=%s" % (response.status, response.url))

        return ldr.load_item()

    # def logger_db(self, response):
    #     self.logger.debug("(logger_db) response: status=%d, URL=%s" % (response.status, response.url))
    #     if response.status in (302, 301) and 'Location' in response.headers:
    #         self.logger.debug("(parse_item) Location header: %r" % response.headers['Location'])
    #         yield scrapy.Request(
    #             response.urljoin(response.headers['Location']),
    #             callback=self.logger_db)
