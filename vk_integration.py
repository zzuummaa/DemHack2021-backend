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
        response.append(vk.wall.delete(post_id=int(post_id)))

    return response


if __name__ == '__main__':
    token = '94f917c4e2882f05c7c5ea0c4a767f30a0f121ec38d441903f63059431b244af34f8ba7ebe6ef5d80ca48'
    print(wall_to_posts(get_wall(token)))
    print(clear_wall(token, [7]))
