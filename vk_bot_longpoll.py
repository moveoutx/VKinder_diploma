from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import re
from vk_request import get_token, VkUser, vk_group_client, vk_client


# Авторизация токеном группы
GROUP_ID = get_token('group_id.ini')
GROUP_TOKEN = get_token('vk_group_token.ini')
API_VERSION = "5.131"

# Паттерны для привет/пока
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

# №2. Клавиатура с 4 кнопками
keyboard_4 = VkKeyboard(one_time=False, inline=True)
keyboard_4.add_callback_button(label="Далее", color=VkKeyboardColor.PRIMARY,
                               payload={"type": "type_next", "text": "1"},)
keyboard_4.add_callback_button(label="Избранное", color=VkKeyboardColor.POSITIVE,
                               payload={"type": "type_favour", "text": "2"},)
keyboard_4.add_callback_button(label="Blacklist", color=VkKeyboardColor.NEGATIVE,
                               payload={"type": "type_blacklist", "text": "3"},)
keyboard_4.add_callback_button(label="Всё избранное", color=VkKeyboardColor.SECONDARY,
                               payload={"type": "type_all_favour", "text": "4"},)


# Запускаем longpoll, получаем события из чата
index_user = 0
count_users = 0
found_users_list = []
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_message = event.obj.message["text"]
        if user_message != "":
            if event.from_chat:
                answer_flag = False
                for pattern in hello_patterns:
                    hello_flag = re.match(pattern, user_message)
                    if hello_flag:
                        user_id = event.obj.user_id  # Если кто-то поздоровался, то смотрим его id
                        # !!!!!!!!!!!!!!!! Здесь будет проверка, есть ли user_id в БД
                        # Если есть в БД, то сообщение "Рады видеть вас снова" и сообщение с 4 кнопками
                        # Если нет в БД, то сообщение как ниже.
                        vk.messages.send(
                            chat_id='1',
                            random_id=get_random_id(),
                            peer_id=2000000001,
                            keyboard=keyboard_2.get_keyboard(),
                            message="Привет! В нашем чате удобный поиск друзей из vk. Хотите попробовать?",
                        )
                        answer_flag = True
                        break
                if not answer_flag:
                    for pattern in bye_patterns:
                        bye_flag = re.match(pattern, user_message)
                        if bye_flag:
                            vk.messages.send(
                                chat_id='1',
                                random_id=get_random_id(),
                                peer_id=2000000001,
                                message="До свидания! Заходите ещё.",
                            )
                            answer_flag = True
                            break
                # # Третий вариант ответов(на будущее), если ещё нужен какой-то диалог на конкретную фразу
                # # Кроме привет/пока.
                # # Можно сделать счётчик и после 5 сообщений пользователя, рассказать ему о боте.
                # if not answer_flag:
                #     vk.messages.send(chat_id='1', random_id=get_random_id(), peer_id=2000000001,
                #     keyboard=keyboard_2.get_keyboard(), message="",)
                #     answer_flag = True
                #     break

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
            user_info = vk_group_client.get_users_info(event.obj.user_id)
            # Находим список друзей по параметрам пользователя
            found_users_list = vk_client.search_users(user_info)
            count_users = len(found_users_list)
            # Выводим информацию 0-й записи из словаря найденных пользователей
            # +++++++++++++++ Добавить проверку на id из блэклист. Если из блэклист, то пропускать увеличив счётчик
            # 1. Получаем 3 фото с макс лайками.(или 2 или 1 фото, если их всего столько в профиле пользователя)
            three_photo_attachment = vk_client.get_three_max_likes_photo(found_users_list[0][0])
            # 2. Имя Фамилия, ссылка на профиль в качестве сообщения
            name_soname_href = found_users_list[0][1]
            vk.messages.send(
                peer_id=event.obj.peer_id,
                random_id=get_random_id(),
                chat_id=event.obj.chat_id,
                message=name_soname_href,
                attachment=three_photo_attachment,
                keyboard=keyboard_4.get_keyboard(),
            )
        elif event_type == "type_next":
            index_user += 1
            if index_user < count_users:
                # Выводим сообщение о следующем пользователе
                # ++++++++++++ Добавить проверку на id из блэклист. Если из блэклист, то пропускать увеличив счётчик
                # Если очередной пользователь уже в Избранном, то можно перекрасить кнопку Избранное в зелёный
                three_photo_attachment = vk_client.get_three_max_likes_photo(found_users_list[index_user][0])
                name_soname_href = found_users_list[index_user][1]
                vk.messages.edit(
                    peer_id=2000000001,
                    chat_id=1,
                    message=name_soname_href,
                    conversation_message_id=event.obj.conversation_message_id,
                    attachment=three_photo_attachment,
                    keyboard=keyboard_4.get_keyboard(),
                )
            else:
                # Снова смотрим пользователей по кругу, начиная с 0
                # +++++++++++++ Добавить проверку на id из блэклист. Если из блэклист, то пропускать увеличив счётчик
                index_user = 0
                three_photo_attachment = vk_client.get_three_max_likes_photo(found_users_list[index_user][0])
                name_soname_href = found_users_list[index_user][1]
                vk.messages.edit(
                    peer_id=2000000001,
                    chat_id=1,
                    message='Вы просмотрели все найденные контакты.\nНачнём сначала\n' + name_soname_href,
                    conversation_message_id=event.obj.conversation_message_id,
                    attachment=three_photo_attachment,
                    keyboard=keyboard_4.get_keyboard(),
                )

        elif event_type == "type_favour":
            # !!!!!!!!!!!!!!!!!!!!!!!!!  id текущего выбранного пользователя записать в БД в Избранное
            three_photo_attachment = vk_client.get_three_max_likes_photo(found_users_list[index_user][0])
            name_soname_href = found_users_list[index_user][1]
            vk.messages.edit(
                peer_id=2000000001,
                chat_id=1,
                message='Контакт:\n' + name_soname_href + '\nдобавлен в Избранное',
                conversation_message_id=event.obj.conversation_message_id,
                attachment=three_photo_attachment,
                keyboard=keyboard_4.get_keyboard(),
            )
        elif event_type == "type_blacklist":
            # Если пользователь нажал на Blacklist
            # +++++++++++++++++++++++ Заносим его id в БД blacklist
            pass
        elif event_type == "type_all_favour":
            # !!!!!!!!!!!!!!!!!!!!!!!!!!  Если пользователь нажал на Всё избранное
            # Выводим всех в одном сообщении построчно: Имя Фамилия и ссылка на профиль. Без фото.
            pass

# Для запуска проекта запускаем этот файл
