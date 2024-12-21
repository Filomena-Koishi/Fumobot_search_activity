
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message
)
from nonebot.params import CommandArg

import requests
# URL链接
urls: list[str] = [
    "https://thonly.cc/proxy_google_doc/v4/spreadsheets/13ykPzw9cKqQVXXEwhCuX_mitQegHdFHjZtGdqT6tlmk/values:batchGet?ranges=THO!A2:E200&ranges=THP%26tea-party!A2:E200&ranges=School!A2:E200&ranges=LIVE!A2:E200&key=AIzaSyAKE37_qaMY4aYDHubmX_yfebfYmnx2HUw",
    "https://thonly.cc/proxy_google_doc/v4/spreadsheets/1mMUsvTdyz07BtnLbs0WEr5gdvsRkjftnrek_n5HSdNU/values:batchGet?ranges=THO!A2:E200&ranges=THP%26tea-party!A2:E200&ranges=School!A2:E200&ranges=LIVE!A2:E200&key=AIzaSyAKE37_qaMY4aYDHubmX_yfebfYmnx2HUw"
]

# 合并两个 URL 的数据
def fetch_data() -> dict[str, list]:
    combined_data: dict[str, list] = {"valueRanges": []}
    for url in urls:
        response: requests.Response = requests.get(url)
        data = response.json()
        combined_data["valueRanges"].extend(data.get("valueRanges", []))
    return combined_data

# NoneBot 命令注册
search_activity = on_command('fumo 搜索活动', priority=4, block=True)

# 统一处理搜索活动命令
@search_activity.handle()
async def search_activity_handler(bot: Bot, event: Event, args: Message = CommandArg()):
    keyword = args.extract_plain_text()
    event_list = search_event_by_name(keyword)
    
    if event_list:
        event_names = [event['name'] for event in event_list]

        # 根据匹配活动数量处理不同的情况
        if len(event_names) > 18:
            await search_activity.finish(f'匹配的结果过多（{len(event_names)}个），请使用更精细的条件进行搜索!')
        elif len(event_names) > 3:
            # 多个活动匹配，显示活动列表
            activity_names = "\n".join(event_names)
            await search_activity.finish("匹配的活动名：\n" + activity_names)
        else:
            # 只有一个活动匹配，显示活动详情
            # event = list(event_list.values())[0]
            msg = ""
            count = 1
            for event in event_list:
                msg += f"{count}. 活动名: {event['name']}\n--状态: {event['status']}\n--地区: {event['location']}\n--日期: {event['date']}\n--QQ群: {event['id']}\n\n"
                count += 1

            await search_activity.finish(msg.strip())
    else:
        await search_activity.finish("未找到匹配的活动，请确保字符的大小写正确！")
# 获取活动数据
# def fetch_data():
#     response = requests.get(url1)
#     return response.json()


def search_event_by_name(event_name)-> list:
    data = fetch_data()
    matched_events = []
    
    for value_range in data.get("valueRanges", []):
        for row in value_range.get("values", []):
            # 检查当前行是否包含足够的列
            if len(row) >= 5:
                activity_name = row[1]
                location = row[2]
                # 如果活动名匹配（部分匹配）
                if event_name in activity_name or event_name in location:
                    matched_events.append({
                        "status": row[0],
                        "name": activity_name,
                        "location": row[2],
                        "date": row[3],
                        "id": row[4]
                    })
    
    return matched_events

