import requests
import time
import datetime


# Возвращает токен из файла. (Токены находятся в первой строке ini-файлов).
def get_token(file):
    with open(file) as f:
        token = f.read().strip()
    return token


class VkUser:

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version,
        }
        self.filename_list = []  # Список куда будут добавляться все уникальные имена файлов
        self.url_list = []  # Список со всеми url фото, которые нужно скачать

    def get_users_info(self, user_id):
        '''
        Получаем информацию о пользователе vk
        :param user_id: ID пользователя ВКонтакте
        :return: словарь вида {'id': , 'first_name': , 'last_name': , 'bdate': , 'sex': , 'country': , 'city': , 'has_photo':  }
        '''
        get_users_params = {'user_id': user_id, 'fields': 'bdate, sex, city, has_photo, country'}
        res = requests.get('https://api.vk.com/method/users.get', params={**self.params, **get_users_params})
        user_info = res.json()['response'][0]
        result_dict = {'id': user_id}
        if 'first_name' in user_info:
            result_dict['first_name'] = user_info['first_name']
        if 'last_name' in user_info:
            result_dict['last_name'] = user_info['last_name']
        if 'bdate' in user_info:
            bdate_dict = user_info['bdate'].split('.')
            if len(bdate_dict) == 3:
                result_dict['year'] = bdate_dict[2]  # Если дата есть и полная, то берём год, иначе не вносим в словарь
        if 'sex' in user_info:
            if user_info['sex'] == '1':
                result_dict['sex'] = '2'
            else:
                result_dict['sex'] = '1'
        if 'country' in user_info:
            result_dict['country_id'] = user_info['country']['id']
        if 'city' in user_info:
            result_dict['city_id'] = user_info['city']['id']
            result_dict['city_title'] = user_info['city']['title']
        if 'has_photo' in user_info:
            result_dict['has_photo'] = user_info['has_photo']
        time.sleep(0.35)
        return result_dict

    def search_users(self, params_dict):
        '''
        Функция поиска по году, полу, городу.
        :param params_dict: словарь вида {'id': , 'first_name': , 'last_name': , 'bdate': , 'sex': , 'country': , 'city': , 'has_photo':  }
        : return: Возвращает список вида [[user1_id, 'Имя Фамилия ссылка'], [user2_id, 'Имя Фамилия ссылка'], ...]
        '''
        search_params = {'sex': params_dict['sex'], 'country_id': params_dict['country_id'],
                         'city': str(params_dict['city_id']), 'hometown': params_dict['city_title'],
                         'has_photo': 1, 'sort': 0, 'count': 1000, 'company': 0, 'status': 6,
                         'fields': 'bdate, sex, city, has_photo, country'}
        if 'year' in params_dict:
            now_year = datetime.date.today().year
            search_params['age_from'] = str(now_year - int(params_dict['year']) - 3)
            search_params['age_to'] = str(now_year - int(params_dict['year']) + 3)
        res = requests.get('https://api.vk.com/method/users.search', params={**self.params, **search_params})
        found_users_list = res.json()['response']['items']
        time.sleep(0.35)  # Ограничение ВК - 3 запроса в секунду
        search_params['status'] = 1  # Теперь запрос по тем же параметрам, только status 1 - “не замужем”/“не женат”
        res = requests.get('https://api.vk.com/method/users.search', params={**self.params, **search_params})
        found_users_list.extend(res.json()['response']['items'])
        found_result_list = []
        for user in found_users_list:
            if not user['is_closed']:  # Берём пользователей, только с открытым профилем, чтобы были с фото.
                found_result_list.append([user['id'], f"{user['first_name']} {user['last_name']} \n"
                                                      f"https://vk.com/id{user['id']}"])
        time.sleep(0.35)
        return found_result_list

    def get_three_max_likes_photo(self, user_id, album_id='-6'):
        '''
        Возвращает строку с 1, 2 или 3 id_фото с максимальными лайками из профиля пользователя, начиная с
        максимальных лайков.
        Строка сформирована для отправки сообщения с фото в чат методом messege.send c параметром attachment
        :param user_id: ID пользователя ВКонтакте
        :param album_id: по умолчанию '-6' фото из профиля пользователя
        :return str: - строка вида "<user_id>photo<photo_id1>, <user_id>photo<photo_id2>, <user_id>photo<photo_id3>"
        '''
        get_photo_params = {'owner_id': user_id, 'album_id': album_id, 'extended': 1}
        res = requests.get('https://api.vk.com/method/photos.get', params={**self.params, **get_photo_params}).json()
        id_likes_lists = []  # Список списков вида: [[id фото, кол-во лайков],... ,...] всех фото из профиля
        for photo in res['response']['items']:
            id_likes_lists.append([photo['id'], photo['likes']['count']])
        # Сортируем список по лайкам
        id_likes_lists.sort(key=lambda x: x[1])
        id_likes_lists.reverse()
        if len(id_likes_lists) > 3:
            id_likes_lists = id_likes_lists[:3]  # Оставляем 3 фото с максимальным кол-вом лайков
        photo_attachment_list = []  # Список для формирования строки-attachments для отправки трёх фото в сообщении
        for item in id_likes_lists:
            photo_attachment_list.append(f'photo{user_id}_{item[0]}')
        attachment_str = ','.join(photo_attachment_list)  # attachment_str - параметр для отправки 3 фото в чат
        time.sleep(0.35)
        return attachment_str


# Групповой токен для получения информации о пользователе, который общается с ботом
vk_group_token = get_token('vk_group_token.ini')
vk_group_client = VkUser(vk_group_token, '5.131')

# Токен пользователя вк (ваш токен) для поиска пользователей.(Групповой токен не наделён правами поиска)
vk_token = get_token('vk_token.ini')
vk_client = VkUser(vk_token, '5.131')


