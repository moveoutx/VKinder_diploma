import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from models import *
from pprint import pprint
import json


class ORM:
    def __init__(self):
        self.DSN = "postgresql://postgres:6950dc6c7@localhost:5432/vk_bot"
        self.engine = sq.create_engine(self.DSN)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()


    def create_tables(self):
        create_tables(self.engine)

    def delete_tables(self):
        delete_tables(self.engine)

    def reload_tables(self):
        reload_tables(self.engine)

    def _end_session(self):
        self.session.close()

    def _session_add(self, id, record):
        self.session.add(id, record)

    def add_user(self, user_id):
        '''
        Добавляет пользователя в БД
        :param user_id: ID пользователя ВКонтакте
        :return:
        '''
        user = User(vk_id_user=user_id)
        self.session.add(user)
        self.session.commit()

    def add_like(self, user_id, like_id):
        '''
        Добавляет пользователя  в понравившиеся
        :param user_id: ID Кто добавляет
        :param like_id: ID Кого добавляем
        :return:
        '''
        like = Likes(vk_id_likes=like_id)
        self.session.add(like)
        self.session.commit()
        user_like = User(vk_id_user=user_id, likes_id=like.id)
        self.session.add(user_like)
        self.session.commit()

    def add_black_list(self, user_id, black_list_id):
        '''
        Добавляет пользователя в черный список
        :param user_id: ID Кто добавляет
        :param black_list_id: ID Кого добавляем
        :return:
        '''
        black_list = Black_list(vk_id_bl=black_list_id)
        self.session.add(black_list)
        self.session.commit()
        user_black_list = User(vk_id_user=user_id, black_list_id=black_list.id)
        self.session.add(user_black_list)
        self.session.commit()

    def find_all_likes(self, user_id):
        '''
        Находит все id понравившихся пользователей
        :param user_id: ID пользователя
        :return: Возвращает список ID в likes листе
        '''
        likes = []
        for l in self.session.query(Likes).join(User.likes).filter(User.vk_id_user == user_id).all():
            likes.append(l.vk_id_likes)
        return likes

    def find_all_bl(self, user_id):
        '''
        Находит все id пользователей из черного списка
        :param user_id:
        :return:
        '''
        blacklist = []
        for bl in self.session.query(Black_list).join(User.black_list).filter(User.vk_id_user == user_id).all():
            blacklist.append(bl)
        return blacklist


if __name__ == "__main__":
    db = ORM()

    # db.create_tables()
    # db.delete_tables()
    # db.reload_tables()

    # db.add_user("1023568")
    # db.add_like("321","25648542")

    print(db.find_all_bl("321"))