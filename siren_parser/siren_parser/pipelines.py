from sqlalchemy.orm import sessionmaker
from siren_parser.models import Video, Website, db_connect, create_tables


class SerialsPipeline(object):
    """ pipeline for storing scraped items in the database"""
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine = db_connect()
        create_tables(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save deals in the database.

        This method is called for every item pipeline component.

        """
        print(item.fields)
        session = self.Session()

        video = Video(name=item['name'], year_of_issue=item['year_of_issue'],
                      country=item['country'], genre=item['genre'],
                      duration=item['duration'],
                      description=item['description'], photo=item['photo'],
                      type=item['type'], season=item['season'],
                      last_episode=item['last_episode'])
        website = Website(quality=item['quality'], translation=item['translation'],
                          update_date=item['update_date'],
                          link_to_watch_online=item['link_to_watch_online'])

        try:
            session.add(video)
            session.add(website)
            session.commit()
        except:
            session.rollback()
            print(item.fields)
            raise
        finally:
            session.close()

        return item
