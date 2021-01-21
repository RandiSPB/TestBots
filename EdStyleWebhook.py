import telebot
from telebot import apihelper
from telebot import types
from openpyxl import load_workbook
from telebot import apihelper
import re
import re
import os
from dotenv import load_dotenv
import cherrypy
import datetime


def parse_from_xlsx_data(data):
    pass


class EDSTest:
    def __init__(self, filename, bot_ref, texts):
        self.texts = texts
        self.bot = bot_ref
        self.state = 'START'
        self.flag = None
        self.questions = self.create_test_data(filename)
        self.cur_q = 0
        self.types_scores = {
            'A': 0,
            'R': 0,
            'T': 0,
            'P': 0
        }

    def change_state(self, new_state):
        self.state = new_state

    def return_cur_text(self):
        return self.texts[self.state]

    def validate_editing(self, new_args):
        pass

    def handler(self, call):
        text = f'<b>{self.cur_q + 1} из 80</b>\n\n{list(self.questions.keys())[self.cur_q]}'
        if call.data == 'skip':
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton(text='Далее', callback_data='NO_CB'))
            self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       text=text, reply_markup=markup, parse_mode='html')
            self.cur_q += 1
            self.send_question(call.message.chat.id)
        elif call.data == 'NO_CB':
            self.bot.send_message(call.message.chat.id, 'Не надо нажимать на эту кнопку')
        else:
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton(text='✅', callback_data='NO_CB'))
            self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       text=text, reply_markup=markup, parse_mode='html')
            self.types_scores[call.data] += 1
            self.cur_q += 1
            self.send_question(call.message.chat.id)


    @staticmethod
    def create_test_data(path='TEST1.xlsx', rows=82, cols=2):
        wb = load_workbook(filename=path)
        sheet = wb.active
        alph = 'BCDEFGHIJKLMNOPQRSTUVWXYZ'
        res = []
        for i in range(2, rows):
            col = []
            for j in range(cols):
                tmp = ''.join((alph[j], str(i)))
                col.append(sheet[tmp].value)
            res.append(col)
        return {i[0]: i[1] for i in res}

    def disclaimer(self, chat_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Да, все понятно', callback_data='START_TEST'))
        self.bot.send_message(chat_id, self.return_cur_text(), reply_markup=markup, parse_mode='html')

    def start(self, chat_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Да, я хочу пройти', callback_data='CALL_DISC'))
        self.bot.send_message(chat_id, self.return_cur_text(), reply_markup=markup, parse_mode='html')

    def send_question(self, chat_id):
        try:
            text = f'<b>{self.cur_q + 1} из 80</b>\n\n{list(self.questions.keys())[self.cur_q]}'
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup_labels = ('✅', 'Далее')
            markup_cb = (list(self.questions.values())[self.cur_q], 'skip')
            markup.add(*tuple(types.InlineKeyboardButton(text=i, callback_data=j) for i,
                                                                                      j in zip(markup_labels,
                                                                                               markup_cb)))
            self.bot.send_message(chat_id, text, reply_markup=markup,
                                  parse_mode='html')
        except IndexError as e:
            print(e)
            self.finish_test(chat_id)

    def finish_test(self, chat_id):
        text = 'Спасибо за прохождение теста!👍\n\n✅Баллы отображают степень Вашего предпочтения тому или иному стилю' \
               ' обучения на <i>данный момент:</i>\n\n<b>Активатор - {0} ({4})\nРефлектор - {1} ({5})\n' \
               'Теоретик - {2} ({6})\nПрагматик - {3} ({7})</b>\n\n📌Успехов!'.format(*self.types_scores.values(),
                                                                                *self.return_preference())
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Хочу пройти еще раз', callback_data='RESTART_TEST'))
        self.bot.send_message(chat_id, text, reply_markup=markup, parse_mode='html')

    @staticmethod
    def return_activist_preference(value: int) -> str:
        return {
            0 <= value <= 3: 'Очень низкое',
            4 <= value <= 6: 'Низкое',
            7 <= value <= 10: 'Среднее',
            11 <= value <= 12: 'Высокое',
            13 <= value <= 20: 'Очень высокое'
        }[True]

    @staticmethod
    def return_reflector_preference(value: int) -> str:
        return {
            0 <= value <= 8: 'Очень низкое',
            9 <= value <= 11: 'Низкое',
            12 <= value <= 14: 'Среднее',
            15 <= value <= 17: 'Высокое',
            18 <= value <= 20: 'Очень высокое'
        }[True]

    @staticmethod
    def return_theorist_preference(value: int) -> str:
        return {
            0 <= value <= 7: 'Очень низкое',
            8 <= value <= 10: 'Низкое',
            11 <= value <= 13: 'Среднее',
            14 <= value <= 15: 'Высокое',
            16 <= value <= 20: 'Очень высокое'
        }[True]

    @staticmethod
    def return_pragmatist_preference(value: int) -> str:
        return {
            0 <= value <= 8: 'Очень низкое',
            9 <= value <= 11: 'Низкое',
            12 <= value <= 14: 'Среднее',
            15 <= value <= 16: 'Высокое',
            17 <= value <= 20: 'Очень высокое'
        }[True]

    def return_preference(self):
        tmp = tuple(self.types_scores.values())
        return (self.return_activist_preference(tmp[0]), self.return_reflector_preference(tmp[1]),
                self.return_theorist_preference(tmp[2]), self.return_pragmatist_preference(tmp[3]))

    def start_test(self, chat_id):
        self.send_question(chat_id)


class SimpleUserTestEDS:
    def __init__(self, msg, bot_ref, texts):
        self.on_test = False
        self.bot = bot_ref
        self.try_times = 0
        self.id = msg.chat.id
        self.test = EDSTest('eds.xlsx', bot_ref, texts)
        self.auth(msg)

    def auth(self, msg):
        print(msg.chat.id)
        self.bot.send_message(msg.chat.id, 'Пожалуйста, введите код доступа заглавными буквами <b>без пробелов</b> и'
                                           ' знаков препинания\n\n<b>Например:</b> <i>HW2L</i>', parse_mode='html')
        self.bot.register_next_step_handler(msg, self.get_code)

    def get_code(self, msg):
        date = datetime.datetime.now()
        date += datetime.timedelta(seconds=3600 * 3)
        print(date)
        key = f'SW{date.month}{date.day}{str(date.year)[2::]}'
        print(key)
        if msg.text == key:
            with open('logger.txt', 'a') as logger:
                logger.write(f'[Тестобот "Стиль результатов"]: Пользователь с id: {msg.chat.id} Авторизация прошла успешно!'
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
                    logger.write(f'[Тестобот "Стиль результатов"]: Пользователь с id: {msg.chat.id} Ошибка авторизации!  - '
                                 f'{datetime.datetime.today()}\n')
                self.bot.send_message(msg.chat.id, 'Вы слишком много раз ввели неверный код.\n\nДля решения опишите'
                                                   ' проблему Лине, она поможет ;)\n@lina_chandler')
    def handler(self, message):
        if self.on_test:
            self.bot.send_message(message.chat.id, 'Вы уже проходите тест!')
        else:
            self.on_test = True
            self.test.start(message.chat.id)

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
            self.test = EDSTest('DISC.xlsx', self.bot, self.test.texts)
            self.test.start(call.message.chat.id)
        else:
            self.test.handler(call)


env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
API_TOKEN = os.getenv('API_TOKEN_EDSTYLE')
bot = telebot.TeleBot(API_TOKEN)
users = {}
texts_literal = {
        'DISCLAIMER': 'Отлично!\n\n<b>Пожалуйста, внимательно прочитайте эту информацию:</b>\n\nВам будет предложено 80'
                      ' утверждений.\n\nЕсли Вы согласны с утверждением больше, чем не согласны, то нажмите кнопку с '
                      '✅.\n\nЕсли же вы в большей степени не согласны с высказыванием – жмите кнопку <i>"Далее"</i>'
                      '\n\nВсе утверждения относятся к вашему переговорному опыту.',
        'START': 'Добрый день 👋🏼\n\n<b>Готовы пройти тест "Стиль достижения результатов"?</b>'
    }


@bot.message_handler(content_types='text')
def handler(message):
    if message.text == '/start':
        try:
            users[message.chat.id].handler(message)
        except KeyError:
            users[message.chat.id] = SimpleUserTestEDS(message, bot, texts_literal)
    elif users[message.chat.id].test.state == 'BLOCKED':
        bot.send_message(message.chat.id, 'Вам не нужно на данный момент вводить никакой текст. Просто нажимайт'
                                          'e кнопки! :)')
    else:
        bot.send_message(message.chat.id, 'Вам не нужно вводить никакой текст. Просто нажимайте кнопки! :)')


@bot.callback_query_handler(func=lambda call: True)
def smo(call):
    try:
        print(call.data)
        print(users)
        users[call.message.chat.id].callback_handler(call)
    except KeyError as e:
        users[call.message.chat.id] = SimpleUserTestEDS(call.message, bot, texts_literal)


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
            'server.socket_port': 7783,
            'engine.autoreload.on': False
        })
    cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
