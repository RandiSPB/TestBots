import telebot
from telebot import apihelper
from telebot import types
from openpyxl import load_workbook
from telebot import apihelper
import re
import re
import os
from dotenv import load_dotenv
from threading import Timer
import cherrypy
import datetime


def parse_from_xlsx_data(data):
    pass


questions = ('Он хорошо себя чувствует', 'Он думает: «Это трудно, лучше закончить и доделать попозже»',
             'Он считает, что справится с этим', 'Он думает: «Я могу гордиться собой, потому что справился с этим»',
             'Он думает: «Похоже, снова не получится» ', 'Он недоволен тем, что у него получилось', 'Он устал',
             'Он думает: «Я попрошу лучше кого-нибудь мне помочь»', 'Он думает: «Хорошо бы это у меня получилось»',
             'Он думает, что все сделал правильно', 'Он боится, что что-то сделал не так', 'Это ему не нравится',
             'Он не хочет, чтобы у него плохо получилось', 'Он хочет сделать лучше остальных',
             'Он думает: «Я лучше сделаю что-нибудь потруднее»', 'Он предпочитает ничего не делать',
             'Он думает: «Если это трудно, то мне придется поработать дольше остальных»',
             'Он думает, что не сумеет сделать это')


class HeckHausenTest:
    def __init__(self, user_id: int, bot_ref, texts: dict):
        self.timer = None
        self.score_storage = {i: 0 for i in range(1, 19)}
        self.id = user_id
        self.texts = texts
        self.bot = bot_ref
        self.buffer = None
        self.state = 'START'
        self.flag = None
        self.cur_picture_ptr = 1

    def change_state(self, new_state: str):
        self.state = new_state

    def return_result(self) -> tuple:
        res = [0, 0, 0]
        for q_num in self.score_storage.keys():
            if q_num in (4, 9, 14, 15, 17):
                res[0] += self.score_storage[q_num]
            elif q_num in (5, 7, 11, 13):
                res[2] += self.score_storage[q_num]
            elif q_num in (2, 6, 8, 12, 16, 18):
                res[1] += self.score_storage[q_num]
            else:
                continue
        return tuple(res)

    def return_cur_text(self):
        return self.texts[self.state]

    def start_timer(self):
        self.timer = Timer(3, self.edit_photo)
        self.timer.start()

    def edit_photo(self):
        text = f'<b>Изображение {self.cur_picture_ptr} из 6</b>'
        self.bot.send_message(self.buffer.chat.id, text=text, parse_mode='html')

    def validate_editing(self, new_args):
        pass

    def handler(self, call):
        self.bot.send_message(call.message.chat.id, 'Не надо нажимать на эту кнопку')

    def disclaimer(self, chat_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Да, все понятно', callback_data='START_TEST'))
        self.bot.send_message(chat_id, self.return_cur_text(), reply_markup=markup, parse_mode='html')

    @staticmethod
    def return_question_list() -> str:
        global questions
        return '\n'.join(tuple(f'<b>{i + 1}</b>. {questions[i]}' for i in range(18)))

    def start(self, chat_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Да, я хочу пройти', callback_data='CALL_DISC'))
        self.bot.send_message(chat_id, self.return_cur_text(), reply_markup=markup, parse_mode='html')

    def process_right_answer(self, msg):
        try:
            questions_numbers = tuple(int(i.strip()) for i in msg.text.split(','))
            for number in questions_numbers:
                self.score_storage[number] += 1
            self.cur_picture_ptr += 1
            self.bot.delete_message(self.buffer.chat.id, self.buffer.message_id)
            self.send_question(msg.chat.id)
        except (ValueError, TypeError):
            if msg.text == '-':
                self.cur_picture_ptr += 1
                self.bot.delete_message(self.buffer.chat.id, self.buffer.message_id)
                self.send_question(msg.chat.id)
            else:
                self.bot.send_message(chat_id=msg.chat.id, text='Пожалуйста, убедитесь что ответ введен согласно всем'
                                                                ' правилам!')
                self.bot.register_next_step_handler(msg, self.process_right_answer)
        except KeyError:
            self.bot.send_message(chat_id=msg.chat.id, text='Вам дано всего-лишь 18 вопросов с номера 1 по номер 18!'
                                                            'Пожалуйста не выходите за данный диапазон!')
            self.bot.register_next_step_handler(msg, self.process_right_answer)

    def process_wrong_answer(self, msg):
        self.cur_picture_ptr += 1
        self.bot.delete_message(self.buffer.chat.id, self.buffer.message_id)
        self.send_question(msg.chat.id)

    def send_question(self, chat_id):
        try:
            with open(os.path.join('content', 'Heckhausen', f'{self.cur_picture_ptr}.jpg'), 'rb') as emotion_photo:
                self.bot.send_photo(chat_id, emotion_photo, caption=f'<b>Изображение {self.cur_picture_ptr} из 6</b>',
                                    parse_mode='html')
                self.buffer = self.bot.send_message(chat_id=chat_id, text=self.return_question_list(),
                                                    parse_mode='html')
                msg_txt = 'Напишите через запятую номера утверждений, которые, по Вашему мнению, <b>подходят</b> к ' \
                          'данному рисунку.\n\nНапример:\n1,6,9,13,18\n\n<i>Вы можете выбрать любое количество ' \
                          'утверждений или не проставить их совсем. В таком случае просто поставьте дефис</i>'
                self.bot.send_message(chat_id, text=msg_txt, parse_mode='html')
                self.bot.register_next_step_handler(self.buffer, self.process_right_answer)
        except (IndexError, FileNotFoundError) as error:
            self.finish_test(chat_id)

    def finish_test(self, chat_id):
        text = '<b>Ваш результат:</b>\n\n🔸 Стремление к успеху или надежда на успех - <b>{0}</b>\n🔸 Боязнь неудачи с '\
               'ощущением собственной неспособности - <b>{1}</b>\n🔸 Боязнь социальных последствий неудачи - <b>{2}</b>'\
               ''.format(*self.return_result())
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Хочу пройти еще раз', callback_data='RESTART_TEST'))
        self.bot.send_message(chat_id, text, reply_markup=markup, parse_mode='html')

    def start_test(self, chat_id):
        self.send_question(chat_id)


class SimpleUserHeckHausenTest:
    def __init__(self, msg, bot_ref, texts):
        self.on_test = False
        self.bot = bot_ref
        self.id = msg.chat.id
        self.try_times = 0
        self.test = HeckHausenTest(msg.chat.id, bot_ref, texts)
        self.auth(msg)

    def handler(self, message):
        if self.on_test:
            self.bot.send_message(message.chat.id, 'Вы уже проходите тест!')
        else:
            self.on_test = True
            self.test.start(message.chat.id)

    def auth(self, msg):
        self.bot.send_message(msg.chat.id, 'Пожалуйста, введите код доступа заглавными буквами <b>без пробелов</b> и'
                                           ' знаков препинания\n\n<b>Например:</b> <i>HW2L</i>', parse_mode='html')
        self.bot.register_next_step_handler(msg, self.get_code)

    def get_code(self, msg):
        date = datetime.datetime.now()
        date += datetime.timedelta(seconds=3600 * 3)
        key = f'SW{date.month}{date.day}{str(date.year)[2::]}'
        if msg.text == key:
            with open('logger.txt', 'a') as logger:
                logger.write(f'[Тестобот "Хекхаузен"]: Пользователь с id: {msg.chat.id} Авторизация прошла успешно!'
                             f' - {datetime.datetime.today()}\n')
            self.test.change_state('START')
            self.on_test = True
            self.test.start(msg.chat.id)
        else:
            self.try_times += 1
            if self.try_times <= 5:
                self.bot.send_message(msg.chat.id, f'Ой! Вы ввели неверный код.\nУточните код у тренера и повторите '
                                                   f'попытку.\n\nОсталось попыток: <b>{6 - self.try_times}</b>',
                                      parse_mode='html')
                self.bot.register_next_step_handler(msg, self.get_code)
            else:
                self.test.change_state('BLOCKED')
                with open('logger.txt', 'a') as logger:
                    logger.write(f'[Тестобот "Хекхаузен"]: Пользователь с id: {msg.chat.id} Ошибка авторизации!  - '
                                 f'{datetime.datetime.today()}\n')
                self.bot.send_message(msg.chat.id, 'Вы слишком много раз ввели неверный код.\n\nДля решения опишите'
                                                   ' проблему Лине, она поможет ;)\n@lina_chandler')

    def callback_handler(self, call):
        if call.data == 'CALL_DISC':
            self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       text=self.test.return_cur_text(), reply_markup=None, parse_mode='html')
            self.test.change_state('DISCLAIMER')
            self.test.disclaimer(call.message.chat.id)

        elif call.data == 'START_TEST':
            self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       text=self.test.return_cur_text(), reply_markup=None, parse_mode='html')
            self.test.start_test(call.message.chat.id)

        elif call.data == 'RESTART_TEST':
            self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       text=call.message.text, reply_markup=None, parse_mode='html')
            self.test = HeckHausenTest(call.message.chat.id, self.bot, self.test.texts)
            self.test.start(call.message.chat.id)
        else:
            self.test.handler(call)


env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
API_TOKEN = os.getenv('API_TOKEN_HECKHAUSEN')
bot = telebot.TeleBot(API_TOKEN)
users = {}
texts_literal = {
        'DISCLAIMER': 'Отлично!\n\nМы хотим показать вам 6 рисунков и узнать, что вы думаете по поводу того, что на них'
                      ' изображено. На рисунках вы увидите людей, которые участвуют в переговорной деятельности. '
                      '\n\n▫️Глядя на рисунки, вы наверняка определите, что они делают, о чем думают, что чувствуют. '
                      'Наверняка вы можете вспомнить о сходных ситуациях, в которых вам уже пришлось побывать.'
                      '\n\n▫️В таких ситуациях можно чувствовать себя по-разному. Можно заниматься делом охотно или '
                      'без желания. Можно радоваться и чувствовать себя счастливым или испытывать неуверенность в том,'
                      ' что ты что-то сможешь сделать. Кто-то, возможно, испытывает боязнь, что он все испортит или не '
                      'справится. По каждому рисунку можно сочинить историю. Вы наверняка могли бы придумать свой '
                      'небольшой рассказ.\n\n▫️Мы же поступим проще. Вам не надо будет рассказывать никаких историй.\n'
                      '\n<i>✅Нужно будет лишь найти из приложенного списка те предложения, которые подходят к тому или'
                      ' иному рисунку.</i>\n\n<b>⚠️Точность результатов зависит от того, насколько откровенны вы '
                      'будете. Пожалуйста, отвечайте как чувствуете, а не обдумывая, какой ответ будет признан '
                      'правильным.</b>',
        'START': 'Добрый день 👋🏼\n\n<b>Готовы пройти тест на мотивацию к достижениям?</b>\n\nЭтот тест поможет вам '
                 'понять, насколько сильно вы мотивированы на достижения. На основании его результатов вы сможете лучше'
                 ' понять себя и спланировать направление развития своей личности.'
    }


@bot.message_handler(content_types='text')
def handler(message):
    if message.text == '/start':
        try:
            users[message.chat.id].handler(message)
        except KeyError:
            users[message.chat.id] = SimpleUserHeckHausenTest(message, bot, texts_literal)
    elif users[message.chat.id].test.state == 'BLOCKED':
        bot.send_message(message.chat.id, 'Вам не нужно на данный момент вводить никакой текст. Просто нажимайт'
                                          'e кнопки! :)')
    else:
        bot.send_message(message.chat.id, 'Вам не нужно вводить никакой текст. Просто нажимайте кнопки! :)')


@bot.callback_query_handler(func=lambda call: True)
def smo(call):
    try:
        users[call.message.chat.id].callback_handler(call)
    except KeyError as e:
        users[call.message.chat.id] = SimpleUserHeckHausenTest(call.message, bot, texts_literal)


class WebhookServer(object):
    # index равнозначно /, т.к. отсутствию части после ip-адреса (грубо говоря)
    @cherrypy.expose
    def index(self):
        length = int(cherrypy.request.headers['content-length'])
        json_string = cherrypy.request.body.read(length).decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''


if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 7784,
        'engine.autoreload.on': False
    })
    cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
