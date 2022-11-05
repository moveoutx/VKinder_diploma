import re

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from ORM.class_ORM import *
from vk_request import get_token, vk_group_client, vk_client

# Авторизация токеном группы
GROUP_ID = get_token('group_id.ini')
GROUP_TOKEN = get_token('vk_group_token.ini')
API_VERSION = "5.131"

# Паттерны для бота на сообщение привет/пока
hello_patterns = [r"\.?([П|п]ривет)\.?", r"\.?([З|з]дравствуй)\.?", r"\.?([П|п]рив)\.?", r"\.?([З|з]доров[а|\s|о])\.?",
                  r"\.?([H|h]ello)\.?", r"[^|\s|,]([H|h]i[\s|,|!|.]?)\.?", r"(^[H,h]i)"]
bye_patterns = [r"\.?([П|п]ока)\.?", r"\.?([Д|д]о\s?свид)\.?", r"\.?([П|п]океда)\.?", r"\.?([B|b]ye)\.?",
                r"\.?([G|g]oodbye)\.?", r"\.?([С|с]частливо)\.?"]

# Запускаем бот
vk_session = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

# №1. Клавиатура с 2 кнопками
keyboard_2 = VkKeyboard(one_time=False, inline=True)
keyboard_2.add_callback_button(label="Да", color=VkKeyboardColor.POSITIVE, payload={"type": "type_yes", "text": "1"},)
keyboard_2.add_callback_button(label="Нет", color=VkKeyboardColor.NEGATIVE, payload={"type": "type_no", "text": "0"},)

# №2. Клавиатура с 4 кнопками (текущий отображаемый контакт НЕ в Избранном)
keyboard_4 = VkKeyboard(one_time=False, inline=True)
keyboard_4.add_callback_button(label="Далее", color=VkKeyboardColor.PRIMARY,
                               payload={"type": "type_next", "text": "1"},)
keyboard_4.add_callback_button(label="Избранное", color=VkKeyboardColor.SECONDARY,
                               payload={"type": "type_favour", "text": "2"},)
keyboard_4.add_callback_button(label="Blacklist", color=VkKeyboardColor.SECONDARY,
                               payload={"type": "type_blacklist", "text": "3"},)
keyboard_4.add_callback_button(label="Всё избранное", color=VkKeyboardColor.SECONDARY,
                               payload={"type": "type_all_favour", "text": "4"},)

# №3. Клавиатура с 4 кнопками (текущий отображаемый контакт в Избранном)
keyboard_4_likes = VkKeyboard(one_time=False, inline=True)
keyboard_4_likes.add_callback_button(label="Далее", color=VkKeyboardColor.PRIMARY,
                               payload={"type": "type_next", "text": "1"},)
keyboard_4_likes.add_callback_button(label="Избранное", color=VkKeyboardColor.SECONDARY,
                               payload={"type": "type_favour", "text": "2"},)
keyboard_4_likes.add_callback_button(label="Blacklist", color=VkKeyboardColor.SECONDARY,
                               payload={"type": "type_blacklist", "text": "3"},)
keyboard_4_likes.add_callback_button(label="Всё избранное", color=VkKeyboardColor.POSITIVE,
                               payload={"type": "type_all_favour", "text": "4"},)

# №4. Клавиатура с 4 кнопками (текущий отображаемый контакт добавили только что в BlackList)
keyboard_4_bl = VkKeyboard(one_time=False, inline=True)
keyboard_4_bl.add_callback_button(label="Далее", color=VkKeyboardColor.PRIMARY,
                               payload={"type": "type_next", "text": "1"},)
keyboard_4_bl.add_callback_button(label="Избранное", color=VkKeyboardColor.SECONDARY,
                               payload={"type": "type_favour", "text": "2"},)
keyboard_4_bl.add_callback_button(label="Blacklist", color=VkKeyboardColor.NEGATIVE,
                               payload={"type": "type_blacklist", "text": "3"},)
keyboard_4_bl.add_callback_button(label="Всё избранное", color=VkKeyboardColor.SECONDARY,
                               payload={"type": "type_all_favour", "text": "4"},)

# Подключаемся к БД
db = ORM()


count_users = 0  # Кол-во найденных контактов
found_users_list = []  # Все контакты найденные по критериям запроса
found_users_list_without_bl = []  # Все найденные контакты минус id-шники из blacklist
index_user = 0  # Номер индекса в листе найденных пользователей (нужен для перебора по листу)
user_id_likes_list = []  # Избранные контакты текущего пользователя
user_id = 0  # id вк текущего пользователя, общающегося с ботом

# Запускаем longpoll, получаем события из чата
for event in longpoll.listen():
    #  __________ Обработка новых сообщений в чате ________________________________________________________________
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_message = event.obj.message["text"]
        if user_message == "stop bot":  # Сообщение в чате для остановки бота
            break
        if user_message != "":
            if event.from_chat:
                answer_flag = False
                for pattern in hello_patterns:
                    hello_flag = re.match(pattern, user_message)
                    if hello_flag:
                        user_id = event.obj.message["from_id"]
                        if db.find_user_id(user_id):  # Если кто-то поздоровался, то смотрим его id в БД в Users
                            vk.messages.send(
                                peer_id=event.message.peer_id,
                                chat_id=event.chat_id,
                                random_id=get_random_id(),
                                keyboard=keyboard_2.get_keyboard(),
                                message="Привет! Рады видеть вас снова.\n Хотите продолжить поиск контактов?",
                            )
                            answer_flag = True
                            break
                        else:
                            db.add_user(user_id)  # Если пользователь первый раз в чате, добавляем его в базу
                            vk.messages.send(
                                peer_id=event.message.peer_id,
                                chat_id=event.chat_id,
                                random_id=get_random_id(),
                                keyboard=keyboard_2.get_keyboard(),
                                message="Привет! В нашем чате удобный поиск друзей из vk. Хотите попробовать?",
                            )
                            answer_flag = True
                            break
                if not answer_flag:
                    for pattern in bye_patterns:  # Если кто то говорит пока, то бот отвечает
                        bye_flag = re.match(pattern, user_message)
                        if bye_flag:
                            vk.messages.send(
                                peer_id=event.message.peer_id,
                                chat_id=event.chat_id,
                                random_id=get_random_id(),
                                message="До свидания! Заходите ещё.",
                            )
                            answer_flag = True
                            break

    # __________Обрабатываем клики по callback кнопкам___________________________________________________________
    elif event.type == VkBotEventType.MESSAGE_EVENT:
        event_type = event.object.payload.get("type")
        if event_type == "type_no":
            vk.messages.send(
                peer_id=event.obj.peer_id,
                chat_id=event.obj.chat_id,
                random_id=get_random_id(),
                message="Спасибо за внимание.",
            )
        elif event_type == "type_yes":
            # Получаем информацию пользователя, общающегося с ботом. (Для теста вместо event.obj.user_id - любой id )
            user_id = event.obj.user_id
            user_info = vk_group_client.get_users_info(user_id)
            # Находим список друзей по параметрам пользователя
            found_users_list = vk_client.search_users(user_info)
            # Выводим информацию 0-й записи из словаря найденных пользователей
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
                vk.messages.send(
                    peer_id=event.obj.peer_id,
                    random_id=get_random_id(),
                    chat_id=event.obj.chat_id,
                    message=name_soname_href,
                    attachment=three_photo_attachment,
                    keyboard=keyboard_4.get_keyboard(),
                )
            else:
                vk.messages.send(
                    peer_id=event.obj.peer_id,
                    random_id=get_random_id(),
                    chat_id=event.obj.chat_id,
                    message=name_soname_href,
                    attachment=three_photo_attachment,
                    keyboard=keyboard_4_likes.get_keyboard(),
                )

        elif event_type == "type_next":
            index_user += 1
            if index_user < count_users:
                # Если очередной пользователь уже в Избранном, то можно перекрасить кнопку Избранное в зелёный
                three_photo_attachment = vk_client.get_three_max_likes_photo(found_users_list_without_bl[index_user][0])
                name_soname_href = found_users_list_without_bl[index_user][1]
                if found_users_list_without_bl[index_user][0] not in user_id_likes_list:
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        chat_id=event.obj.chat_id,
                        message=name_soname_href,
                        conversation_message_id=event.obj.conversation_message_id,
                        attachment=three_photo_attachment,
                        keyboard=keyboard_4.get_keyboard(),
                    )
                else:
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        chat_id=event.obj.chat_id,
                        message=name_soname_href,
                        conversation_message_id=event.obj.conversation_message_id,
                        attachment=three_photo_attachment,
                        keyboard=keyboard_4_likes.get_keyboard(),
                    )
            else:
                # Снова смотрим пользователей по кругу, начиная с 0
                index_user = 0
                three_photo_attachment = vk_client.get_three_max_likes_photo(found_users_list_without_bl[index_user][0])
                name_soname_href = found_users_list[index_user][1]
                if found_users_list_without_bl[index_user][0] not in user_id_likes_list:
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        chat_id=event.obj.chat_id,
                        message='Вы просмотрели все найденные контакты.\nНачнём сначала\n' + name_soname_href,
                        conversation_message_id=event.obj.conversation_message_id,
                        attachment=three_photo_attachment,
                        keyboard=keyboard_4.get_keyboard(),
                    )
                else:
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        chat_id=event.obj.chat_id,
                        message='Вы просмотрели все найденные контакты.\nНачнём сначала\n' + name_soname_href,
                        conversation_message_id=event.obj.conversation_message_id,
                        attachment=three_photo_attachment,
                        keyboard=keyboard_4_likes.get_keyboard(),
                    )

        elif event_type == "type_favour":
            user_id = event.obj.user_id
            user_like_id = found_users_list_without_bl[index_user][0]
            if user_like_id not in user_id_likes_list:
                db.add_like(user_id, user_like_id)
            three_photo_attachment = vk_client.get_three_max_likes_photo(found_users_list_without_bl[index_user][0])
            name_soname_href = found_users_list_without_bl[index_user][1]
            vk.messages.edit(
                peer_id=event.obj.peer_id,
                chat_id=event.obj.chat_id,
                message='Контакт:\n' + name_soname_href + '\nдобавлен в Избранное',
                conversation_message_id=event.obj.conversation_message_id,
                attachment=three_photo_attachment,
                keyboard=keyboard_4_likes.get_keyboard(),
            )
        elif event_type == "type_blacklist":
            user_id = event.obj.user_id
            user_bl_id = found_users_list_without_bl[index_user][0]
            db.add_black_list(user_id, user_bl_id)
            three_photo_attachment = vk_client.get_three_max_likes_photo(user_bl_id)
            name_soname_href = found_users_list_without_bl[index_user][1]
            vk.messages.edit(
                peer_id=event.obj.peer_id,
                chat_id=event.obj.chat_id,
                message='Контакт:\n' + name_soname_href + '\nдобавлен в Blacklist',
                conversation_message_id=event.obj.conversation_message_id,
                attachment=three_photo_attachment,
                keyboard=keyboard_4_bl.get_keyboard(),
            )
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
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    chat_id=event.obj.chat_id,
                    message=message_like,
                    conversation_message_id=event.obj.conversation_message_id,
                    keyboard=keyboard_4_likes.get_keyboard(),
                )
            else:
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    chat_id=event.obj.chat_id,
                    message='У вас пока нет избранных контактов',
                    conversation_message_id=event.obj.conversation_message_id,
                    keyboard=keyboard_4_likes.get_keyboard(),
                )
