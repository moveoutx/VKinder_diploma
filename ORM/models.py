import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()

# Новые
class Users(Base):
    __tablename__ = "users"

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer)

class Likes(Base):
    __tablename__ = "likes"

    id = sq.Column(sq.Integer, primary_key=True)
    id_likes = sq.Column(sq.Integer)
    id_users = sq.Column(sq.Integer, sq.ForeignKey("users.id"))

    users = relationship(Users, backref="likes")

class Blacklist(Base):
    __tablename__ = "blacklist"

    id = sq.Column(sq.Integer, primary_key=True)
    id_black = sq.Column(sq.Integer)
    id_users = sq.Column(sq.Integer, sq.ForeignKey("users.id"))

    users = relationship(Users, backref="blacklist")

# Старые
# class Likes(Base):
#     __tablename__ = "likes"
#
#     id = sq.Column(sq.Integer, primary_key=True)
#     vk_id_likes = sq.Column(sq.Integer, nullable=False)
#
#
#
# class Black_list(Base):
#     __tablename__ = "black_list"
#
#     id = sq.Column(sq.Integer, primary_key=True)
#     vk_id_bl = sq.Column(sq.Integer, nullable=False)
#
#
# class User(Base):
#     __tablename__ = "user"
#
#     id = sq.Column(sq.Integer, primary_key=True)
#     vk_id_user = sq.Column(sq.Integer, nullable=False)
#     likes_id = sq.Column(sq.Integer, sq.ForeignKey("likes.id"))
#     black_list_id = sq.Column(sq.Integer, sq.ForeignKey("black_list.id"))
#
#     likes = relationship(Likes, backref="user")
#     black_list = relationship(Black_list, backref="user")


def create_tables(engine):
    Base.metadata.create_all(engine)
    print('Структура БД создана')


def delete_tables(engine):
    Base.metadata.drop_all(engine)
    print('Структура БД удалена')

def reload_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print('БД пересоздана, все данные удалены')
