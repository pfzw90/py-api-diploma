import requests, pprint, urllib
from urllib.parse import urljoin
from pprint import pprint


class Photo:
    name = ''

    def __init__(self, date, likes, sizes):
        self.date = date
        self.size = sizes['type']
        self.url = sizes['url']
        self.likes = likes

    def __str__(self):
        return f'date: {self.date}, likes: {self.likes}, size: {self.size}, url: {self.url}'


class VkAPI:
    BASE_URL = "https://api.vk.com/method/"

    def __init__(self):
        self.token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
        self.version = '5.124'

    def find_largest(self, sizes):
        sizes_chart = ['x', 'z', 'y', 'r', 'q', 'p', 'o', 'x', 'm', 's']
        for chart in sizes_chart:
            for size in sizes:
                if size['type'] == chart:
                    return size

    def get_photos(self, uid):
        get_url = urljoin(self.BASE_URL, 'photos.get')
        resp = requests.get(get_url, params={
            'access_token': self.token,
            'v': self.version,
            'owner_id': uid,
            'album_id': 'profile',
            'photo_sizes': 1,
            'extended': 1
        }).json().get('response').get('items')

        return [Photo(photo.get('date'),
                      photo.get('likes')['count'],
                      self.find_largest(photo.get('sizes'))) for photo in resp]


class YaAPI:
    def __init__(self, token: str):
        self.auth = f'OAuth {token}'

    def get_folders(self):
        return [p['name'] for p in (requests.get("https://cloud-api.yandex.net/v1/disk/resources",
                                                 params={"path": '/'},
                                                 headers={"Authorization": self.auth})
                                    .json().get('_embedded').get('items')) if p['type'] == 'dir']

    def check_folder_name(self, n_folder, ex_folders):
        if n_folder not in ex_folders:
            return n_folder
        n = 1
        n_folder += '_' + str(n)
        while n_folder in ex_folders:
            m = n + 1
            n_folder = n_folder.replace('_' + str(n), '_' + str(m))
            n += 1
        return n_folder

    def create_folder(self, folder_name):
        print(f'Creating folder "{folder_name}":' + str(
              requests.put("https://cloud-api.yandex.net/v1/disk/resources",
                           params={"path": '/' + folder_name},
                           headers={"Authorization": self.auth}).status_code))

    def create_file_names(self, photos):
        for photo in photos:
            photo.name = str(photo.likes)
            i = 1
            f = False
            for photo_1 in photos[i:]:
                if photo.likes == photo_1.likes and not f:
                    photo.name += '_' + str(photo.date)
                    f = True
            i += 1
            photo.name += '.jpg'

    def upload(self, uid, photos):
        upload_folder = self.check_folder_name(uid, self.get_folders())
        self.create_folder(upload_folder)
        self.create_file_names(photos)

        for photo in photos:
            response = requests.put("https://cloud-api.yandex.net/v1/disk/resources/upload",
                                    params={"path": '/' + upload_folder + '/' + photo.name,
                                            "url": photo.url},
                                    headers={"Authorization": self.auth})
            if response.status_code == '202':
                print(f'Photo "{photo["name"]}" uploaded.')
            else:
                print(
                    f'Error uploading photo "{photo.name}": {response.json().get("message")} : {response.status_code}')


def init():
    vk_api = VkAPI()
    ya_api = YaAPI('XXX')
    uid = '552934290'
    ya_api.upload(uid, vk_api.get_photos(uid))


if __name__ == '__main__':
    init()
