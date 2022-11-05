import requests
import time


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
            result_dict['sex'] = user_info['sex']
        if 'country' in user_info:
            result_dict['country_id'] = user_info['country']['id']
        if 'city' in user_info:
            result_dict['city_id'] = user_info['city']['id']
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
        # Если у пользователя не стоит год, то запрос по году не делаем,
        if 'year' in params_dict:
            search_params = {'birth_year': params_dict['year'], 'sex': params_dict['sex'],
                             'country_id': params_dict['country_id'], 'city_id': params_dict['city_id'],
                             'has_photo': 1, 'sort': 0, 'count': 1000, 'company': 0,
                             'fields': 'bdate, sex, city, has_photo, country'}
        else:
            search_params = {'sex': params_dict['sex'], 'country_id': params_dict['country_id'], 'city_id': params_dict['city_id'],
                             'has_photo': 1, 'sort': 0, 'count': 1000, 'company': 0,
                             'fields': 'bdate, sex, city, has_photo, country'}

        res = requests.get('https://api.vk.com/method/users.search', params={**self.params, **search_params})
        found_users_list = res.json()['response']['items']  # Пока первая тысяча (vk выдаёт только 1000. Потом подумать как можно обойти)
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
        :return str: - строка вида "<user_id>photo<photo_id1>, <user_id>photo<photo_id2>, <user_id>photo<photo_id3>"
        '''
        get_photo_params = {'owner_id': user_id, 'album_id': album_id, 'extended': 1}
        res = requests.get('https://api.vk.com/method/photos.get', params={**self.params, **get_photo_params}).json()
        likes_id_dict_all = {}
        for photo in res['response']['items']:
            likes_id_dict_all[photo['likes']['count']] = photo['id']
        # Сортируем словарь likes_id_dict_all по ключу, т.е. по кол-ву лайков
        list_keys = []
        for key in likes_id_dict_all.keys():
            list_keys.append(key)
        list_keys.sort()
        list_keys.reverse()
        if len(list_keys) > 3:
            list_keys = list_keys[:3]
        three_max_photo_id = []
        for item in list_keys:
            three_max_photo_id.append(likes_id_dict_all[item])
        photo_attachment_list = []
        for foto_id in three_max_photo_id:
            photo_attachment_list.append(f'photo{user_id}_{foto_id}')
        attachment_str = ','.join(photo_attachment_list)
        time.sleep(0.35)
        return attachment_str


# Групповой токен для получения информации о пользователе, который общается с ботом
vk_group_token = get_token('vk_group_token.ini')
vk_group_client = VkUser(vk_group_token, '5.131')

# Токен пользователя вк (ваш токен) для поиска пользователей.(Групповой токен не наделён правами поиска)
vk_token = get_token('vk_token.ini')
vk_client = VkUser(vk_token, '5.131')


