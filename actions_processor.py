from datetime import datetime
import vk_integration

# Дёргается, если один из триггеров группы "триггернулся".
# Нужно выполнить все экшоны этой группы.
def process_group_triggered(db, group_id):
    user_id = db.get_user_by_group(group_id)
    vk_api_token = db.get_vk_api(user_id)

    # Delete Posts
    post_ids_to_delete = db.get_all_post_ids_from_action_vk_delete_posts(group_id)
    vk_integration.clear_wall(vk_api_token, post_ids_to_delete)

    # Delete Messages
    # Urealized!

    # Delete groups after all
    db.clear_group_after_trigger(group_id)

def check_trigger_timers(db):
    for group_id, expiration_dt in db.get_all_timers():
        if datetime.now() > expiration_dt:
            process_group_triggered(db, group_id)