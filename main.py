import telebot
import config
import parsing
import requests
import database
import datetime


TOKEN = config.token

if __name__ == '__main__':
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def start(message):
        chat_id = message.chat.id
        bot.send_message(chat_id, 'Привет, отправь мне ссылку на товар Вайлдберриз')


    @bot.message_handler(content_types='text')
    def message_handler(message):
        text = message.text
        chat_id = message.chat.id

        data_base = database.Users()
        user = tuple(data_base.get_user(int(chat_id)))
        if user == ():
            data_base.create_user(int(chat_id))
            user = tuple(data_base.get_user(int(chat_id)))
        until = datetime.datetime.date(datetime.datetime.strptime(user[0][2], '%Y-%m-%d'))
        '''Часть кода закоментированна/изменена по причине того, что на данный момент сервис оплаты подписки не подключен'''
        if 'https://www.wildberries.ru/catalog/' in text and len(text.split('/')) == 6 and user[0][1] != True:  # and datetime.date.today() <= until:
            try:
                r = requests.get(text)
                art = parsing.get_art(text)
                data = parsing.data_parse(art)
            except requests.exceptions.MissingSchema:
                bot.send_message(chat_id, 'Отправь мне ссылку на товар Вайлдберриз')
            else:
                if data is not None:
                    data_base.last_atr_update(int(chat_id), int(art))

                    stocks = data["stocks"]
                    stocks_text = ''

                    for i in stocks:
                        stocks_text += f'Склад {i["wh"]}, остаток {i["qty"]} шт.\n'
                    message_text = f'Имя товара: {data["imt_name"]}\n' \
                                   f'Стоимость товара: {int(data["price"]) / 100} ₽\n' \
                                   f'Количесвто отзывов: {data["feedbacks"]}\n\n' \
                                   f'Выручка: База данных пока что не подключена\n' \
                                   f'Продажи: База данных пока что не подключена\n' \
                                   f'Комиссия Wildberries: {data["commission"][0]}% ({data["commission"][1]}%)\n' \
                                   f'Стоимость логистики: {data["commission"][2]} ₽\n' \
                                   f'Стоимость хранения: {data["commission"][3]} ₽\n\n' \
                                   f'Остатки на складах:\n\n' \
                                   f'{stocks_text}'

                    markup = telebot.types.ReplyKeyboardMarkup()
                    markup.add(telebot.types.KeyboardButton(text='Собрать SEO ключи'))
                    markup.add(telebot.types.KeyboardButton(text='Выйти в главное меню'))

                    bot.send_message(chat_id, message_text, reply_markup=markup)
                else:
                    bot.send_message(chat_id, 'Отправьте правильную ссылку Wildberries')
        #elif datetime.date.today() > until or user[0][1] != True:
        #    pass
        elif text == 'Собрать SEO ключи':
            user = tuple(data_base.get_user(int(chat_id)))
            keys = parsing.get_keys(user[0][3])
            data = {'Ключи': keys, 'Место в выдаче': [parsing.get_search_rating(i, int(user[0][3])) for i in keys]}
            message_text = 'Ключи:\n'
            for i in range(len(keys)):
                message_text += f'Ключ: {keys[i]}\nМесто в выдаче: {data["Место в выдаче"][i] + 1 if data["Место в выдаче"][i] is not None else ">100"}\n\n'
            bot.send_message(chat_id, message_text)
        else:
            bot.send_message(chat_id, 'Отправь мне ссылку на товар Вайлдберриз')


    @bot.message_handler(commands=['button'])
    def button(call):
        print(call)


    bot.infinity_polling()
