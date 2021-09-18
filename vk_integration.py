import vk_api
from datetime import datetime

def validate_token(token):
    try:
        vk = vk_api.VkApi(token=token).get_api()
        print(vk.account.getProfileInfo()['id'])
        return True
    except:
        # TODO: Нормальная обработка ошибок
        # print(error_msg)
        return False


def wall_to_posts(wall):
    posts = []
    if "items" not in wall:
        return posts

    for post in wall["items"]:
        posts.append({
            "id": post["id"],
            "title": post["text"],
            "date": datetime.fromtimestamp(post["date"]).strftime("%Y-%m-%d %H:%M:%S")
        })
    return posts


def get_wall(token):
    vk = vk_api.VkApi(token=token).get_api()
    return vk.wall.get()
    # return my_response({
    #     'posts': [
    #         {'id': 123, 'title': 'Мой пост 1', 'date': '2021-09-18 13:45:19'},
    #         {'id': 123, 'title': 'Мой пост 2', 'date': '2021-11-10 23:11:00'}
    #     ]
    # })
#
if __name__ == '__main__':
    print(wall_to_posts(get_wall('f1c75b295180b27e469520bf90d69182f1db76d9f758f773407b9e3afb377d14b130000e7ec16ae65edf3')))