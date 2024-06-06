import requests
import json

from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async, run_js
from NLP_prod import Matcher_topics

import asyncio

chat_msgs = []
MAX_MESSAGE_COUNT = 100
matcher = Matcher_topics()

async def main():
    global chat_msgs

    put_markdown("Добро пожаловать в чат!")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    while True:
        data = await input_group("Новое сообщение:", [
            input(placeholder="Текст сообщения", name="msg"),
            actions(name="cmd", buttons=["Отправить", {'label': "Выйти из чата", 'type': 'cancel'}])
        ], validate=lambda m: ('msg', "Введите текст сообщения: ") if m["cmd"] == "Отправить" and not m[
            "msg"] else None)

        if data is None:
            break
        # человек
        msg_box.append(put_markdown(f"`{'Name'}:` {data['msg']}"))

        # bot
        # chat_msgs.append((botname, data['msg'])) #необходим для теста эхо
        #get_topic_task = run_async(get_topic(botname, msg_box, data['msg']))
        #get_search_task = run_async(get_search(botname, msg_box, data['msg']))
        #get_weather_task = run_async(get_weather("botname", msg_box, data['msg']))
        get_matching_task = run_async(matching_topic(msg_box, data['msg']))

    #get_weather_task.close()
    get_matching_task.close()
    toast("Вы вышли из чата!")

    put_buttons(["Перезайти"], onclick=lambda btn: run_js('window.location.reload()'))


async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)

        for m in chat_msgs[last_idx:]:
            if m[0] != nickname:
                msg_box.append(put_markdown(f"`{m[0]}`:`{m[1]}`"))

            # удаляем переполнение чата
            if len(chat_msgs) > MAX_MESSAGE_COUNT:
                chat_msgs = chat_msgs[len(chat_msgs) // 2:]

            last_idx = len(chat_msgs)


# асинхронные сервисы для бота
async def get_topic(botname1, msg_box, msg):
    global chat_msgs
    chat_msgs.append(("⚠ ", f" {botname1} ищет тему \" {msg} \"..."))
    await asyncio.sleep(2)
    chat_msgs.append(("⚠ ", f" {botname1} типа нашёл тему \" {msg} \"..."))

async def get_search(botname1, msg_box, search_str):

    blok_list = search_str.split()     # разбиваем слова по пробелам
    url_query = '%20'.join(blok_list)  # разделяем их через %20
    url = 'https://yandex.ru/search/?text=' + url_query + '&lr=213'  # подставляем
    r = requests.get(url)

    chat_msgs.append((f"{botname1}", f" Нашёл в яндексе: \" {r} \" "))

async def get_weather(botname1, msg_box, search_str):
    try:
        res = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=61.241778&lon=73.393032&appid=6545f8fa9439776a69436d7d3acb4010&units=metric")
        data = res.json()
        msg_box.append(put_markdown(f"`{botname1}`: возможно вы искали погоду: \" {data.get('name')}:  {data.get('main').get('temp')} °C \" "))
    except Exception as e:
        msg_box.append(put_markdown(f"`{botname1}`: погоду не нашёл, и вот в чём причина: \" {e} \" "))
        pass

async def matching_topic(msg_box, message):
    try:
        msg_box.append(matcher.matching_topic(message))
    except Exception as e:
        msg_box.append(put_markdown(f"Ошибка: \" {e} \" "))
        pass

if __name__ == "__main__":
    start_server(main, debag=True, port=8081, cdn=False)
