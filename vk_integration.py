import vk_api

def validate_token(token):
    vk = None

    try:
        vk = vk_api.VkApi(token=token).get_api()
        print(vk.account.getProfileInfo()['id'])
        return True
    except:
        # TODO: Нормальная обработка ошибок
        # print(error_msg)
        return False