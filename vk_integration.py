import vk_api

def validate_token(token):
    try:
        vk = vk_api.VkApi(token=token).get_api()
        print(vk.account.getProfileInfo()['id'])
        return True
    except:
        # TODO: Нормальная обработка ошибок
        # print(error_msg)
        return False


def get_posts(token):
    try:
        vk = vk_api.VkApi(token=token).get_api()
        print(vk.wall.get())
        return True
    except:
        return None
    # return my_response({
    #     'posts': [
    #         {'id': 123, 'title': 'Мой пост 1', 'date': '2021-09-18 13:45:19'},
    #         {'id': 123, 'title': 'Мой пост 2', 'date': '2021-11-10 23:11:00'}
    #     ]
    # })
#
if __name__ == '__main__':
    print(get_posts('d98c31da692d0cc01d6130144fae15a28b6af879097b9a9cdf92e4802ce398c2d7f34ffe0949d563f5a55'))