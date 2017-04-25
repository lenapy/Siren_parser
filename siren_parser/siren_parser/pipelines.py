from sqlalchemy.orm import sessionmaker

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pickle

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


def read_data_file():
    try:
        with open(settings.DATA_FILE, 'rb') as f:
            return pickle.load(f)
    except IOError:
        return []


def save_data_file(sended):
    with open(settings.DATA_FILE, 'wb') as f:
        pickle.dump(sended, f)


def prepare_name_for_search(name):
    clean_name = name.rpartition(' (')
    second_clean_name = (clean_name[0].partition(' '))
    if second_clean_name[2]:
        return second_clean_name[2]
    else:
        return second_clean_name[0]


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

                    video_clean_name = prepare_name_for_search(video.name)
                    search_name = '%' + video_clean_name + '%'
                    user_subs = session.query(Video.name, Video.season,
                                              Video.last_episode, User.mail_address).\
                        join(UserSubscription, Video.id == UserSubscription.video_id).\
                        join(User, UserSubscription.user_id == User.id).\
                        filter(Video.name.like(search_name),
                               Video.season == video.season).all()
                    if user_subs:
                        sended = read_data_file()
                        for tv_show_data in user_subs:
                            data_to_save = (video_clean_name, tv_show_data[1],
                                            tv_show_data[2], tv_show_data[3])
                            if data_to_save in sended:
                                continue
                            else:
                                send_email("Siren: вышла новая серия",
                                           "Вышла новая серия {}  на сайте {}. "
                                           "Ссылка для просмотра онлайн {}".format(video_db.name,
                                                                                   website_db.title,
                                                                                   website_db.link_to_watch_online),
                                           data_to_save[3])
                                sended.append(data_to_save)
                                save_data_file(sended)

        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item


class PKSerialsPipeline(object):

    def __init__(self):

        engine = db_connect()
        create_tables(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):

        session = self.Session()

        video = Video(name=item['name'], year_of_issue=item['year_of_issue'],
                      country=item['country'], genre=item['genre'],

                      description=item['description'], photo=item['photo'],
                      type=item['type'], season=item['season'],
                      last_episode=item['last_episode'])

        website = Website(
                          update_date=item['update_date'],
                          link_to_watch_online=item['link_to_watch_online'])

        try:
                session.add(video)
                session.commit()
                website.video_id = video.id
                session.add(website)
                session.commit()

        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item
