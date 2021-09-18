from database import *
import vk_integration

# Дёргается, если один из триггеров группы "триггернулся".
# Нужно выполнить все экшоны этой группы.
def process_group_triggered(group_id):
    user_id = get_db().get_user_by_group(group_id)
    vk_api_token = get_db().get_vk_api(user_id)

    # Delete Posts
    post_ids_to_delete = get_db().get_all_post_ids_from_action_vk_delete_posts(group_id)
    vk_integration.clear_wall(vk_api_token, post_ids_to_delete)

    # Delete Messages
    # Urealized!