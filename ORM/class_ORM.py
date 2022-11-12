from sqlalchemy.orm import sessionmaker
from ORM.models import *


class ORM:
    def __init__(self):
        self.DSN = "postgresql://postgres:your_password_posgtresql@localhost:5432/vk_bot2"
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
        user = Users(vk_id=user_id)
        self.session.add(user)
        self.session.commit()

    def find_user_id(self, user_id):
        '''
        Возвращает id (primary key) для user_id
        :param user_id: ID пользователя ВКонтакте
        :return: Users id
        '''
        id = self.session.query(Users).filter(Users.vk_id == user_id).first()
        if id:
            return id.id
        else:
            return None  # На случай, если БД с самого начала пустая

    def add_like(self, user_id, like_id):
        '''
        Добавляет пользователя  в понравившиеся
        :param user_id: ID Кто добавляет
        :param like_id: ID Кого добавляем
        :return:
        '''
        id_user = self.find_user_id(user_id)
        like = Likes(id_likes=like_id, id_users=id_user)
        self.session.add(like)
        self.session.commit()

    def add_black_list(self, user_id, black_list_id):
        '''
        Добавляет пользователя в черный список
        :param user_id: ID Кто добавляет
        :param black_list_id: ID Кого добавляем
        :return:
        '''
        id_user = self.find_user_id(user_id)
        black_list = Blacklist(id_black=black_list_id, id_users=id_user)
        self.session.add(black_list)
        self.session.commit()

    def find_all_likes(self, user_id):
        '''
        Находит все id понравившихся пользователей
        :param user_id: ID пользователя
        :return: Возвращает список ID в likes листе
        '''
        likes = []
        for l in self.session.query(Likes).join(Users).filter(Users.vk_id == user_id).all():
            likes.append(l.id_likes)
        return likes

    def find_all_bl(self, user_id):
        '''
        Находит все id пользователей из черного списка
        :param user_id:
        :return:
        '''
        blacklist = []
        for bl in self.session.query(Blacklist).join(Users).filter(Users.vk_id == user_id).all():
            blacklist.append(bl.id_black)
        return blacklist

    def all_users(self):
        '''
        Возвращает список id всех пользователей БД
        :return:
        '''
        user_list = []
        for user in self.session.query(Users):
            user_list.append(user.vk_id)
        return user_list


if __name__ == "__main__":
    db = ORM()

    db.create_tables()
    # db.delete_tables()
    # db.reload_tables()

    # Заполняем базу тестовыми данными, проверяем что id пользователя не дублируются
    # db.add_like(1, 1)
    # db.add_like(1, 2)
    # db.add_like(1, 3)
    # db.add_like(1, 4)
    # db.add_like(1, 5)
    # db.add_like(1, 6)
    # db.add_black_list(1, 7)
    # db.add_black_list(1, 8)
    # db.add_black_list(1, 9)
    # db.add_like(2, 2)
    # db.add_like(2, 7)
    # db.add_like(2, 5)
    # db.add_like(2, 12)
    # db.add_like(2, 17)
    # db.add_like(2, 18)
    # db.add_like(2, 20)
    # db.add_like(2, 21)
    # db.add_black_list(2, 3)
    # db.add_black_list(2, 4)
    # db.add_black_list(2, 8)

    #  Выборки
    # print(db.find_all_likes(2))
    # print(db.find_all_bl(1))
