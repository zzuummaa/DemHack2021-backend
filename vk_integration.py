import vk_api
from utils import *

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
            "date": timestamp_to_string(post["date"])
        })
    return posts


def get_wall(token):
    vk = vk_api.VkApi(token=token).get_api()
    return vk.wall.get()


def clear_wall(token, post_ids):
    response = []
    vk = vk_api.VkApi(token=token).get_api()
    for post_id in post_ids:
        response.append(vk.wall.delete(post_id=int(post_id))

    return response


if __name__ == '__main__':
    token = 'f1c75b295180b27e469520bf90d69182f1db76d9f758f773407b9e3afb377d14b130000e7ec16ae65edf3'
    print(wall_to_posts(get_wall(token)))
    print(clear_wall(token, [2]))
