import telebot
from telebot import types
import time
import random

import config
from services import Session

bot = telebot.TeleBot(config.TOKEN)


def generate_random_congratulation():
    return random.choice(config.PHRASES) + random.choice(config.SMILES[0])


def print_question(message, question, session=Session()):
    session.question = question

    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton(f'{question[1][0]}', callback_data=f'{question[1][1]}')
    item2 = types.InlineKeyboardButton(f'{question[2][0]}', callback_data=f'{question[2][1]}')
    markup.add(item1, item2)

    mess = question['text']
    picture = open(f'pictures/questions/{question["picture"]}.jpeg', 'rb')

    bot.send_photo(message.chat.id, picture)
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)


def show_cart(message, session=Session()):
    if session.cart:
        mess = '<b>Ваши покупки:</b>\n'
        count = 1
        for product in session.cart:
            mess += f"<b>{count}.</b> {product['title']}\n"
            count += 1
    else:
        mess = '<b>Пока что у вас нет покупок</b>'
    mess += f'\n\n На вашем счету <b>{session.points}$</b>'
    bot.send_message(message.chat.id, mess, parse_mode='html')


def print_products(message, session=Session()):
    products = config.PRODUCTS
    markup = types.InlineKeyboardMarkup(row_width=3)
    mess = f'У вас <b>{session.points}$</b> \n\nСписок подарков:\n'
    for product in products:
        if product not in session.sold_products:
            index = products.index(product)
            mess += f"<b>Лот №{index + 1}.</b> {products[index]['title']} - <b>{products[index]['price']}$</b>\n"
            item = types.InlineKeyboardButton(f'{index + 1} - {products[index]["price"]}$', callback_data=f'prod{index + 1}')
            markup.add(item)
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)


def show_product(message, product):
    mess = f'<b>{product["title"]}</b>\n \n{product["description"]}'
    # bot.send_message(message.chat.id, mess, parse_mode='html')
    if product['picture'] != '':
        picture = open(f'pictures/products/{product["picture"]}.jpeg', 'rb')
        bot.send_photo(message.chat.id, picture, caption=mess, parse_mode='html')


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton('Инструкция ⚙️')
    item2 = types.KeyboardButton('Начать 🚀')
    markup.add(item1, item2)

    mess = f'Данный бот был создан для того, чтобы поздравлять мою курочку <b>Mort@l Sun</b> ' \
           f'в течение всего дня!\nЕсли ты уже читала инструкцию, то нажимай кнопку <b>"Начать 🚀"</b>.\nЕсли нет, то ' \
           f'очень советую сначала прочитать ее, нажав кнопку <b>"Инструкция ⚙️"</b>, чтобы ничего не пропустить!'
    sticker = open('stickers/start.webp', 'rb')
    bot.send_sticker(message.chat.id, sticker)
    bot.send_message(message.chat.id, mess, reply_markup=markup, parse_mode='html')


@bot.message_handler(content_types=['text'])
def instruction_text(message):
    session = Session()

    # Вывод инструкции
    if message.text in ['Инструкция ⚙️', 'help', 'Help', 'Инструкция', 'инструкция']:
        mess = config.INSTRUCTION
        bot.send_message(message.chat.id, mess, parse_mode='html')

    # Основная отправка фото
    elif message.text == 'Начать 🚀':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        # item1 = types.KeyboardButton('Инструкция ⚙️')
        item2 = types.KeyboardButton('Викторина 🎯')
        item3 = types.KeyboardButton('Случайное поздравление 🎲')
        item4 = types.KeyboardButton('Магазин (magazine) 💵')
        item5 = types.KeyboardButton('Ваши покупки 🎁')
        markup.add(item2, item3, item4, item5)
        bot.send_message(message.chat.id, 'Теперь каждые пол часа тебе будет приходить поздравление, а ты пока можешь поотвечать на вопросы в <b>"Викторине🎯"</b> или получить <b>"Случайное поздравление🎲"</b>', reply_markup=markup, parse_mode='html')
        time.sleep(2)
        while True:
            try:
                number = session.get_next_number_of_photo()
                picture = open(f'pictures/photos/{number}.jpeg', 'rb')
                mess = config.TEXT_FOR_CONGRATULATIONS[number]
                bot.send_photo(message.chat.id, picture, caption=mess, parse_mode='html')
                # bot.send_message(message.chat.id, mess, parse_mode='html')
            except FileNotFoundError:
                mess = 'На этом поздравления с фото заканчиваются'
                bot.send_message(message.chat.id, mess, parse_mode='html')
                # Добавить стикер и поменять текст
                break
            time.sleep(1800)

    # Викторина
    elif message.text == 'Викторина 🎯':
        if session.quest_number == 0:
            mess = 'Сейчас будут отправляться вопросы, за каждый правильный ответ ты получаешь <b>+10$</b>'
        else:
            mess = 'Продолжаем викторину, за каждый правильный ответ ты получаешь <b>+10$</b>'
        bot.send_message(message.chat.id, mess, parse_mode='html')
        time.sleep(1)
        try:
            print_question(message, config.QUESTIONS[session.quest_number])
        except IndexError:
            bot.send_message(message.chat.id,
                             f'Вопросы закончились, на твоем счету <b>{session.points}$</b>. Беги скорее тратить их в магазин!',
                             parse_mode='html')

    # Генерация случайного поздравления
    elif message.text == 'Случайное поздравление 🎲':
        mess = generate_random_congratulation()
        bot.send_message(message.chat.id, mess, parse_mode='html')

    # Магазин
    elif message.text == 'Магазин (magazine) 💵':
        print_products(message)

    elif message.text == 'Ваши покупки 🎁':
        show_cart(message)

    elif message.text == '19.08.1996':
        session.points += 11000
        mess = f'Ты ввела секретный промокод. Твой счет увеличился на <b>+11000$</b>. На вашем счету <b>{session.points}$</b>'
        bot.send_message(message.chat.id, mess, parse_mode='html')


    # Обраболтчик неправильных команд
    else:
        mess = 'Ты ввела что-то не то, проверь текст на опечатки и попробуй еще раз...'
        sticker = open('stickers/gg.webp', 'rb')
        bot.send_message(message.chat.id, mess, parse_mode='html')
        bot.send_sticker(message.chat.id, sticker)


@bot.callback_query_handler(func=lambda call:True)
def callback_inline(call):
    session = Session()

    markup = types.InlineKeyboardMarkup(row_width=1)
    item = types.InlineKeyboardButton('Поехали', callback_data='next')
    markup.add(item)

    # Callback для викторины
    if call.message:
        if call.data == 'yes':
            session.add_points()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=None)
            bot.send_message(call.message.chat.id, text='<b>Правильно!</b>', parse_mode='html')
            if 'ps' in session.question.keys():
                bot.send_message(call.message.chat.id, f'P.S. {session.question["ps"]}')
            bot.send_message(call.message.chat.id, f'<b>У вас {session.points}$</b>', parse_mode='html')
            session.quest_number += 1
            time.sleep(1)
            bot.send_message(call.message.chat.id, 'Следующий вопрос', reply_markup=markup)

        elif call.data == 'no':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=None)
            bot.send_message(call.message.chat.id, text='<b>Неправильно :(</b>', parse_mode='html')
            if 'ps' in session.question.keys():
                bot.send_message(call.message.chat.id, f'P.S. {session.question["ps"]}')
            bot.send_message(call.message.chat.id, f'<b>У вас {session.points}$</b>', parse_mode='html')
            session.quest_number += 1
            time.sleep(1)
            bot.send_message(call.message.chat.id, 'Следующий вопрос', reply_markup=markup)

        elif call.data == 'next':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Поехали', reply_markup=None)
            try:
                print_question(call.message, config.QUESTIONS[session.quest_number])
            except IndexError:
                bot.send_message(call.message.chat.id, f'Вопросы закончились, на твоем счету <b>{session.points}$</b>. Беги скорее тратить их в магазин!', parse_mode='html')

        # Cart product
        elif call.data in [f'prod{x}' for x in range(len(config.PRODUCTS) + 1)]:
            product = config.PRODUCTS[int(call.data[-1]) - 1]
            if session.add_to_cart(product):
                session.sold_products.append(product)
                # file = open('logs.txt', 'w')
                # file.write(product['title'])
                # file.close()
                mess ='(*Ваш товар оплачен и добавлен в корзину)'
                show_product(call.message, product)
            else:
                mess ='(*У вас недостаточно средств для покупки)'
            bot.send_message(chat_id=call.message.chat.id, text=f'<i>{mess}</i>', parse_mode='html')
            # show_cart(call.message)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=None, parse_mode='html')


bot.polling(none_stop=True)