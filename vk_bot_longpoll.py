import re
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

from ORM.class_ORM import *
from vk_request import get_token, vk_group_client, vk_client
from keyboard import keyboard_2, keyboard_4, keyboard_4_likes, keyboard_4_bl
from patterns import hello_patterns, bye_patterns


# Данные для авторизации
GROUP_ID = get_token('group_id.ini')
GROUP_TOKEN = get_token('vk_group_token.ini')
API_VERSION = "5.131"

# Запускаем бот
vk_session = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

# Подключаемся к БД
db = ORM()


def send_text(event, text):
    vk.messages.send(
        peer_id=event.message.peer_id,
        chat_id=event.chat_id,
        random_id=get_random_id(),
        message=text
    )


def send_text_if_button(event, text):
    vk.messages.send(
        peer_id=event.obj.peer_id,
        chat_id=event.obj.chat_id,
        random_id=get_random_id(),
        message=text
    )


def send_text_button(event, text, keyboard):
    vk.messages.send(
        peer_id=event.message.peer_id,
        chat_id=event.chat_id,
        random_id=get_random_id(),
        message=text,
        keyboard=keyboard.get_keyboard()
    )


def send_text_button_photo(event, text, photo_attach, keyboard):
    vk.messages.send(
        peer_id=event.obj.peer_id,
        chat_id=event.obj.chat_id,
        random_id=get_random_id(),
        message=text,
        attachment=photo_attach,
        keyboard=keyboard.get_keyboard()
    )


def edit_text_photo_button(event, text, photo_attach, keyboard):
    vk.messages.edit(
        peer_id=event.obj.peer_id,
        chat_id=event.obj.chat_id,
        conversation_message_id=event.obj.conversation_message_id,
        message=text,
        attachment=photo_attach,
        keyboard=keyboard.get_keyboard()
    )


def edit_text_button(event, text, keyboard):
    vk.messages.edit(
        peer_id=event.obj.peer_id,
        chat_id=event.obj.chat_id,
        conversation_message_id=event.obj.conversation_message_id,
        message=text,
        keyboard=keyboard.get_keyboard()
    )


def if_message(event, user_message):
    if user_message != "":
        answer_flag = False
        for pattern in hello_patterns:
            hello_flag = re.match(pattern, user_message)
            if hello_flag:
                user_id = event.obj.message["from_id"]
                if db.find_user_id(user_id):  # Если кто-то поздоровался, то смотрим его id в БД в Users
                    message = "Привет! Рады видеть вас снова.\n Хотите продолжить поиск контактов?"
                    send_text_button(event, message, keyboard_2)
                    answer_flag = True
                    break
                else:
                    db.add_user(user_id)  # Если поздоровался пользователь и первый раз в чате, добавляем его в базу
                    message = "Привет! В нашем чате удобный поиск друзей из vk. Хотите попробовать?"
                    send_text_button(event, message, keyboard_2)
                    answer_flag = True
                    break
        if not answer_flag:
            for pattern in bye_patterns:  # Если кто то говорит пока, то бот отвечает
                bye_flag = re.match(pattern, user_message)
                if bye_flag:
                    message = "До свидания! Заходите ещё."
                    send_text(event, message)
                    break


def vk_bot_longpoll():
    count_users = 0  # Кол-во найденных контактов
    found_users_list = []  # Все контакты найденные по критериям запроса
    found_users_list_without_bl = []  # Все найденные контакты минус id-шники из blacklist
    index_user = 0  # Номер индекса в листе найденных пользователей (нужен для перебора по листу)
    user_id_likes_list = []  # Избранные контакты текущего пользователя
    # Запускаем longpoll, получаем события из чата
    for event in longpoll.listen():
        # Обработка сообщений
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_message = event.obj.message["text"]
            if user_message == "stop bot":  # Сообщение в чате для остановки бота
                break
            if_message(event, user_message)

        # Обработка кнопок
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            event_type = event.object.payload.get("type")
            if event_type == "type_no":
                send_text_if_button(event, "Спасибо за внимание. Можете попробовать потом.")
            elif event_type == "type_yes":
                # Получаем информацию пользователя, общающегося с ботом.(Для теста вместо event.obj.user_id - любой id)
                user_id = event.obj.user_id
                user_info = vk_group_client.get_users_info(user_id)
                # Находим список друзей по параметрам пользователя
                found_users_list = vk_client.search_users(user_info)
                # Берём из базы данных все id из блэклиста для данного пользователя
                user_id_bl_list = db.find_all_bl(user_id)
                # Исключаем из итога все id из блэклиста, чтобы их не выводить
                found_users_list_without_bl = [id_ for id_ in found_users_list if id_[0] not in user_id_bl_list]
                count_users = len(found_users_list_without_bl)
                # Найдём id-шники всех из Избранного
                user_id_likes_list = db.find_all_likes(user_id)
                # 1. Получаем 3 фото с макс лайками.(или 2 или 1 фото, если их всего столько в профиле пользователя)
                three_photo_attachment = vk_client.get_three_max_likes_photo(found_users_list_without_bl[0][0])
                # 2. Имя Фамилия, ссылка на профиль в качестве сообщения
                name_soname_href = found_users_list_without_bl[0][1]
                if found_users_list_without_bl[0][0] not in user_id_likes_list:
                    send_text_button_photo(event, name_soname_href, three_photo_attachment, keyboard_4)
                else:
                    send_text_button_photo(event, name_soname_href, three_photo_attachment, keyboard_4_likes)
            elif event_type == "type_next":
                no_photo_flag = True  # У некоторых контактов has_photo = 1, но фото из профиля не открывается.
                while no_photo_flag:
                    index_user += 1
                    if index_user < count_users:
                        # Если очередной пользователь уже в Избранном, то можно перекрасить кнопку Избранное в зелёный
                        three_photo_attachment = vk_client.get_three_max_likes_photo(
                            found_users_list_without_bl[index_user][0])
                        if three_photo_attachment == '':  # Если фото нет, то пропускаем контакт, берём следующий
                            continue
                        else:
                            no_photo_flag = False
                        name_soname_href = found_users_list_without_bl[index_user][1]
                        if found_users_list_without_bl[index_user][0] not in user_id_likes_list:
                            edit_text_photo_button(event, name_soname_href, three_photo_attachment, keyboard_4)
                        else:
                            edit_text_photo_button(event, name_soname_href, three_photo_attachment, keyboard_4_likes)
                    else:
                        # Снова смотрим пользователей по кругу, начиная с 0
                        index_user = 0
                        # Так как идём по кругу, то снова нужно сверить базу данных с блэклист и лайклист
                        user_id = event.obj.user_id
                        # Берём из базы данных все id из блэклиста для данного пользователя
                        user_id_bl_list = db.find_all_bl(user_id)
                        # Исключаем из итога все id из блэклиста, чтобы их не выводить
                        found_users_list_without_bl = [id_ for id_ in found_users_list if id_[0] not in user_id_bl_list]
                        count_users = len(found_users_list_without_bl)
                        # Найдём id-шники всех из Избранного
                        user_id_likes_list = db.find_all_likes(user_id)
                        three_photo_attachment = vk_client.get_three_max_likes_photo(
                            found_users_list_without_bl[index_user][0])
                        if three_photo_attachment == '':
                            continue
                        else:
                            no_photo_flag = False
                        name_soname_href = found_users_list[index_user][1]
                        if found_users_list_without_bl[index_user][0] not in user_id_likes_list:
                            message = 'Вы просмотрели все найденные контакты.\n Начнём сначала.\n\n' + name_soname_href
                            edit_text_photo_button(event, message, three_photo_attachment, keyboard_4)
                        else:
                            message = 'Вы просмотрели все найденные контакты.\nНачнём сначала\n' + name_soname_href
                            edit_text_photo_button(event, message, three_photo_attachment, keyboard_4_likes)

            elif event_type == "type_favour":
                user_id = event.obj.user_id
                user_like_id = found_users_list_without_bl[index_user][0]
                if user_like_id not in user_id_likes_list:
                    db.add_like(user_id, user_like_id)
                three_photo_attachment = vk_client.get_three_max_likes_photo(found_users_list_without_bl[index_user][0])
                name_soname_href = found_users_list_without_bl[index_user][1]
                message = 'Контакт:\n' + name_soname_href + '\nдобавлен в Избранное'
                edit_text_photo_button(event, message, three_photo_attachment, keyboard_4_likes)

            elif event_type == "type_blacklist":
                user_id = event.obj.user_id
                user_bl_id = found_users_list_without_bl[index_user][0]
                db.add_black_list(user_id, user_bl_id)
                three_photo_attachment = vk_client.get_three_max_likes_photo(user_bl_id)
                name_soname_href = found_users_list_without_bl[index_user][1]
                message = 'Контакт:\n' + name_soname_href + '\nдобавлен в Blacklist'
                edit_text_photo_button(event, message, three_photo_attachment, keyboard_4_bl)

            elif event_type == "type_all_favour":
                # Выводим всех в одном сообщении построчно: Имя Фамилия и ссылка на профиль. Без фото.
                user_id = event.obj.user_id
                user_id_likes_list = db.find_all_likes(user_id)
                if user_id_likes_list:
                    message_like = '    Избранное:\n'
                    for user_like in user_id_likes_list:
                        user_like_info_dict = vk_group_client.get_users_info(user_like)
                        message_like += f"{user_like_info_dict['first_name']} {user_like_info_dict['last_name']}    " \
                                        f"https://vk.com/id{user_like}\n"
                    edit_text_button(event, message_like, keyboard_4_likes)
                else:
                    message = 'У вас пока нет избранных контактов'
                    edit_text_button(event, message, keyboard_4_likes)
