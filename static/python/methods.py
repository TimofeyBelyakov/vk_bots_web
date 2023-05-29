import vk_api
import requests
import re
from datetime import datetime
import statistics as st
import pandas as pd


# Класс сбора информации о пользователе
class UserInformation:
    # Константные переменные
    MAX_OBJECTS = 100
    # Поля личной информации пользователя
    STR_FIELDS = ["about", "activities", "bdate", "books", "games", "interests", "home_town", "movies", "music",
                  "nickname", "quotes", "site", "status", "tv", "mobile_phone", "home_phone"]
    INT_FIELDS = ["relation", "sex"]
    ARR_FIELDS = ["schools", "universities", "career", "military", "relatives", "personal", "city", "country"]
    OTHER_FIELDS = ["counters", "contacts", "last_seen"]
    # Счётчики
    COUNTERS = ["friends", "audios", "followers"]
    # Признаки постов
    POSTS_FEATURES = ["likes", "comments", "reposts", "views"]
    # Имена столбцов
    COLUMNS = ["score", "friends", "audios", "followers", "subs", "groups", "posts_count", "posts_med_int", "avg_likes",
               "avg_comm", "avg_rep", "avg_views", "videos_count", "videos_avg_int", "photos_count", "photos_avg_int",
               "gifts_count", "gifts_med_int", "age_acc"]

    # Конструктор класса
    def __init__(self, url, access_token):
        # Подключение к VK API
        self.session = vk_api.VkApi(token=access_token)
        self.user_id = self.get_id(url)
        self.user_info = None
        if self.user_id is not None:
            fields = self.STR_FIELDS + self.INT_FIELDS + self.ARR_FIELDS + self.OTHER_FIELDS + ["photo_100"]
            try:
                self.user_info = self.session.method("users.get", {
                    "user_ids": self.user_id,
                    "fields": ",".join(fields)
                })
            except vk_api.exceptions.ApiError:
                pass

    # Методы
    # Возвращает id страницы
    def get_id(self, url):
        user_id = None
        screen_name = url.replace("https://vk.com/", "").strip()
        try:
            user_id = int(screen_name)
        except (ValueError, TypeError):
            if screen_name[:1] == "id":
                try:
                    user_id = int(screen_name[1:])
                except ValueError:
                    pass
            if user_id is None:
                try:
                    user_id = int(self.session.method("utils.resolveScreenName", {
                        "screen_name": screen_name
                    })["object_id"])
                except (ValueError, TypeError, vk_api.exceptions.ApiError):
                    pass
        return user_id

    # Возвращает личный балл пользователя
    def get_personal_score(self):
        score = 0
        for field in self.STR_FIELDS:
            try:
                if self.user_info[0][field] != "":
                    score += 1
            except KeyError:
                pass
        for field in self.INT_FIELDS:
            try:
                if self.user_info[0][field] != 0:
                    score += 1
            except KeyError:
                pass
        for field in self.ARR_FIELDS:
            try:
                score += len(self.user_info[0][field])
            except KeyError:
                pass
        return score

    # Возвращает личную информацию
    def get_personal_info(self):
        # Подсчёт личного балла пользователя и др. признаков
        result = [self.get_personal_score()]
        # Добавление счётчиков
        for counter in self.COUNTERS:
            try:
                result.append(self.user_info[0]["counters"][counter])
            except KeyError:
                result.append(-1)
        return result

    # Возвращает подписки: другие пользователи, группы и паблики
    def get_subs_info(self):
        try:
            subs = self.session.method("users.getSubscriptions", {"user_id": self.user_id})["users"]["count"]
        except (vk_api.exceptions.ApiError, KeyError):
            subs = -1
        try:
            groupsAndPublics = self.session.method("groups.get", {
                "user_id": self.user_id,
                "filter": "groups,publics"
            })["count"]
        except (vk_api.exceptions.ApiError, KeyError):
            try:
                groupsAndPublics = self.session.method("groups.get", {
                    "user_id": self.user_id,
                    "filter": "publics"
                })["count"]
            except (vk_api.exceptions.ApiError, KeyError):
                groupsAndPublics = -1
        return [subs, groupsAndPublics]

    # Возвращает информацию о постах
    def get_posts_info(self):
        # По умолчанию все значения -1, это соответствует ошибке при сборе данных. -2 - пустое значение.
        postsTotalCount = -1  # Количество постов на стене
        postsMedInterval = -1  # Медианный промежуток времени между постами
        postsAvgValues = [-1 for _ in self.POSTS_FEATURES]  # Список средних значений метрик постов
        try:
            # Вызов метода API
            posts = self.session.method("wall.get", {"owner_id": self.user_id, "count": self.MAX_OBJECTS})
            if "count" in posts:
                postsTotalCount = posts["count"]
            if "items" in posts:
                # Список дат постов
                postsDates = []
                # Список списков метрик постов
                postsValues = [[] for _ in self.POSTS_FEATURES]
                for post in posts["items"]:
                    if "date" in post:
                        if post["date"] > 0:
                            postsDates.append(post["date"])
                    for ind in range(len(postsValues)):
                        # Если метод API не вернул какую-то метрику поста, то считаем это за 0,
                        # т.к., например, при отсутствии просмотров у поста API не возвращает значение views
                        try:
                            postsValues[ind].append(post[self.POSTS_FEATURES[ind]]["count"])
                        except KeyError:
                            postsValues[ind].append(0)
                postsDates.sort(reverse=True)
                # Список промежутков времени между постами
                postsIntervals = [postsDates[ind] - postsDates[ind + 1] for ind in range(len(postsDates) - 1)]
                if postsIntervals:
                    postsMedInterval = round(st.median(postsIntervals), 1)
                # Если список интервалов пуст и количество постов 0 или 1, тогда -2
                # Если список интервалов пуст, а количество постов > 1, тогда остаётся -1
                # (где-то ошибка при сборе данных)
                elif len(posts["items"]) <= 1:
                    postsMedInterval = -2
                # Если количество постов > 0, то считаем средние метрик
                if len(posts["items"]) > 0:
                    postsAvgValues = [round(st.mean(postsValues[ind]), 2) for ind in range(len(postsValues))]
                # Если количество постов 0, то -2
                else:
                    postsAvgValues = [-2 for _ in range(len(postsValues))]
        except vk_api.exceptions.ApiError:
            # Если ошибка в вызове метода wall.get, то все значения остаются -1
            pass
        return [postsTotalCount, postsMedInterval] + postsAvgValues

    # Возвращает информацию о видео
    def get_videos_info(self):
        # По умолчанию все значения -1, это соответствует ошибке при сборе данных. -2 - пустое значение.
        videosTotalCount = -1  # Количество добавленных видео
        videosAvgInterval = -1  # Средний промежуток времени между видео
        try:
            videos = self.session.method("video.get", {"owner_id": self.user_id, "count": self.MAX_OBJECTS})
            if "count" in videos:
                videosTotalCount = videos["count"]
            if "items" in videos:
                # Список дат видео
                videosDates = []
                for video in videos["items"]:
                    if "adding_date" in video:
                        if video["adding_date"] > 0:
                            videosDates.append(video["adding_date"])
                videosDates.sort(reverse=True)
                # Список промежутков времени между видео
                videosIntervals = [videosDates[ind] - videosDates[ind + 1] for ind in range(len(videosDates) - 1)]
                if videosIntervals:
                    videosAvgInterval = round(st.mean(videosIntervals), 1)
                # Если список интервалов пуст и количество видео 0 или 1, тогда -2
                # Если список интервалов пуст, а количество видео > 1, тогда остаётся -1
                # (где-то ошибка при сборе данных)
                elif len(videos["items"]) <= 1:
                    videosAvgInterval = -2
        except vk_api.exceptions.ApiError:
            # Если ошибка в вызове метода video.get, то все значения остаются -1
            pass
        return [videosTotalCount, videosAvgInterval]

    # Возвращает информацию о фото
    def get_photos_info(self):
        # По умолчанию все значения -1, это соответствует ошибке при сборе данных. -2 - пустое значение.
        photosTotalCount = -1  # Количество добавленных фото
        photosAvgInterval = -1  # Средний промежуток времени между фото
        try:
            photos = self.session.method("photos.getAll", {"owner_id": self.user_id, "count": self.MAX_OBJECTS})
            if "count" in photos:
                photosTotalCount = photos["count"]
            if "items" in photos:
                # Список дат фото
                photosDates = []
                for photo in photos["items"]:
                    if "date" in photo:
                        if photo["date"] > 0:
                            photosDates.append(photo["date"])
                photosDates.sort(reverse=True)
                # Список промежутков времени между фото
                photosIntervals = [photosDates[ind] - photosDates[ind + 1] for ind in range(len(photosDates) - 1)]
                if photosIntervals:
                    photosAvgInterval = round(st.mean(photosIntervals), 1)
                # Если список интервалов пуст и количество фото 0 или 1, тогда -2
                # Если список интервалов пуст, а количество фото > 1, тогда остаётся -1
                # (где-то ошибка при сборе данных)
                elif len(photos["items"]) <= 1:
                    photosAvgInterval = -2
        except vk_api.exceptions.ApiError:
            # Если ошибка в вызове метода photos.getAll, то все значения остаются -1
            pass
        return [photosTotalCount, photosAvgInterval]

    # Возвращает информацию о подарках
    def get_gifts_info(self):
        # По умолчанию все значения -1, это соответствует ошибке при сборе данных. -2 - пустое значение.
        giftsTotalCount = -1  # Количество подарков
        giftsMedInterval = -1  # Медианный промежуток времени между подарками
        try:
            gifts = self.session.method("gifts.get", {"user_id": self.user_id, "count": self.MAX_OBJECTS})
            if "count" in gifts:
                giftsTotalCount = gifts["count"]
            if "items" in gifts:
                # Список дат подарков
                giftsDates = []
                for gift in gifts["items"]:
                    if "date" in gift:
                        if gift["date"] > 0:
                            giftsDates.append(gift["date"])
                giftsDates.sort(reverse=True)
                # Список промежутков времени между подарками
                giftsIntervals = [giftsDates[ind] - giftsDates[ind + 1] for ind in range(len(giftsDates) - 1)]
                if giftsIntervals:
                    giftsMedInterval = round(st.median(giftsIntervals), 1)
                # Если список интервалов пуст и количество подарков 0 или 1, тогда -2
                # Если список интервалов пуст, а количество подарков > 1, тогда остаётся -1
                # (где-то ошибка при сборе данных)
                elif len(gifts["items"]) <= 1:
                    giftsMedInterval = -2
        except vk_api.exceptions.ApiError:
            # Если ошибка в вызове метода gifts.get, то все значения остаются -1
            pass
        return [giftsTotalCount, giftsMedInterval]

    # Возвращает возраст аккаунта
    def get_account_age(self):
        age = -1
        try:
            res = requests.get("https://vk.com/foaf.php?id=" + str(self.user_id))
            listDate = re.findall(r'created dc:date="(.*)"', res.text)
            if len(listDate) > 0:
                regDate = datetime.timestamp(
                    datetime.strptime(str(listDate[0]), "%Y-%m-%dT%H:%M:%S%z")
                )
                age = round(datetime.timestamp(datetime.now()) - regDate, 1)
        except:
            pass
        return age

    # Проверка на доступность аккаунта
    def check_user(self):
        # Словарь, содержащий информацию: активна ли страница, есть ли к ней доступ (открыта или нет)
        # и возникли ли ошибки при проверке аккаунта
        result = {"deactivated": False, "can_access_closed": True, "errors": False}
        try:
            # Поле deactivated возвращается, только если страница неактивна
            if "deactivated" in self.user_info[0]:
                result["deactivated"] = self.user_info[0]["deactivated"]
            # Поле can_access_closed должно возвращаться всегда
            if "can_access_closed" in self.user_info[0]:
                result["can_access_closed"] = self.user_info[0]["can_access_closed"]
            else:
                result["errors"] = True
        except (IndexError, KeyError, TypeError):
            result["errors"] = True
        return result

    # Сбор информации
    def collect_info(self):
        result = {"features": None, "name": None, "photo": None, "message": "error"}
        if self.user_info is not None:
            check_user = self.check_user()
            # Если проверка страницы не вызвала внешних ошибок
            if not check_user["errors"]:
                # Если страница открыта и активна
                if check_user["can_access_closed"] and not check_user["deactivated"]:
                    features = pd.DataFrame([
                        self.get_personal_info() +
                        self.get_subs_info() +
                        self.get_posts_info() +
                        self.get_videos_info() +
                        self.get_photos_info() +
                        self.get_gifts_info() +
                        [self.get_account_age()]
                    ], columns=self.COLUMNS, index=[self.user_id])
                    result["features"] = features
                    result["message"] = "success"
                # Если страница закрыта и активна
                elif not check_user["can_access_closed"] and not check_user["deactivated"]:
                    result["message"] = "closed"
                # Если страница неактивна
                elif check_user["deactivated"]:
                    result["message"] = check_user["deactivated"]
                if "first_name" in self.user_info[0] and "last_name" in self.user_info[0]:
                    result["name"] = f"{self.user_info[0]['first_name']} {self.user_info[0]['last_name']}"
                if "photo_100" in self.user_info[0]:
                    result["photo"] = str(self.user_info[0]["photo_100"])
        return result
