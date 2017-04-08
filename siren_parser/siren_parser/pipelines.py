from sqlalchemy.orm import sessionmaker

from sqlalchemy.sql import select

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from siren_parser.models import Video, Website, db_connect, create_tables, User, UserSubscription
from siren_parser import settings


def send_email(subject, body, mail_address):

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = settings.MAIL
    msg['To'] = mail_address
    msg.attach(MIMEText(body))
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(settings.MAIL, settings.PASS)
    s.send_message(msg)
    s.quit()


class SerialsPipeline(object):
    """ pipeline for storing scraped items in the database"""
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates table.
        """
        engine = db_connect()
        create_tables(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """

        This method is called for every item pipeline component.

        """
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
            video_db = session.query(Video).filter_by(name=video.name).first()
            if not video_db:
                session.add(video)
                session.commit()
                website.video_id = video.id
                session.add(website)
                session.commit()
            else:
                if video_db.last_episode != video.last_episode:
                    video_db.last_episode = video.last_episode
                    session.commit()
                    website_db = session.query(Website).filter_by(video_id=video_db.id).first()
                    website_db.update_date = website.update_date
                    session.commit()
                    mails = session.query(User.mail_address).join(UserSubscription,
                                                                  User.id == UserSubscription.user_id). \
                        filter(UserSubscription.video_id == 578).all()
                    for mail in mails:
                        send_email("Siren: вышла новая серия",
                                   "Вышла новая серия {}  на сайте {}. "
                                   "Ссылка для просмотра онлайн {}".format(video_db.name,
                                                                           website_db.title,
                                                                           website_db.link_to_watch_online),
                                   mail)

        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item
