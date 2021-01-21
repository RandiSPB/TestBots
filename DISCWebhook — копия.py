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


class DISCTest:
    def __init__(self, filename, bot_ref, texts):
        self.texts = texts
        self.bot = bot_ref
        self.state = 'START'
        self.flag = None
        self.questions = self.create_test_data(filename)
        self.cur_q = 1
        self.types_scores = {
            'Д': 0,
            'В': 0,
            'У': 0,
            'С': 0
        }

    def change_state(self, new_state):
        self.state = new_state

    def return_cur_text(self):
        return self.texts[self.state]

    def validate_editing(self, new_args):
        pass

    def handler(self, call):
        if call.data != 'NO_CB':

            self.types_scores[call.data] += 1
            index = tuple(self.questions.keys())[self.cur_q - 1]['scores'].index(call.data)
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton(text='' + call.message.json['reply_markup']['inline_keyboard'][int(index)][0]['text'],
                                                  callback_data='NO_CB'))

            self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       text=f'Вы выбрали:\n\n{tuple(self.questions.keys())[self.cur_q - 1]["scores"][index]}',
                                                              reply_markup=markup, parse_mode='html')
            self.send_question(call.message.chat.id)
        else:
            self.bot.send_message(call.message.chat.id, 'Не надо нажимать на эту кнопку')


    @staticmethod
    def create_test_data(path='TEST1.xlsx', rows=58, cols=5):
        test = {}
        wb = load_workbook(filename=path)
        sheet = wb.active
        alph = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        res = []
        for i in range(2, rows):
            col = []
            for j in range(cols):
                tmp = ''.join((alph[j], str(i)))
                col.append(sheet[tmp].value)
            if col[0] is None:
                col = col[2:4]
            res.append(col)

        for i in res:
            if len(i) != 2:
                tmp = i[1:4]
                test.update([(tmp[0], {'answers': [], 'scores': []})])
                test[tmp[0]]['answers'].append(tmp[1])
                test[tmp[0]]['scores'].append(tmp[2])
            else:
                test[tmp[0]]['answers'].append(i[0])
                test[tmp[0]]['scores'].append(i[1])
        return test

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
            q_data = tuple(self.questions.keys())[self.cur_q - 1]
            question_text = '<b>{0} из 15\n\n{1}\n\n{2}\n{3}\n{4]\n{5}</b>'.format(self.cur_q, q_data,
                                                                                   *self.questions[q_data]['answers'])
            button_labels = ('А', 'Б', 'В', 'Г')
            buttons_callback = self.questions[q_data]['scores']
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(*(types.InlineKeyboardButton(text=i, callback_data=j) for i, j in zip(button_labels,
                                                                                             buttons_callback)))
            self.bot.send_message(chat_id, question_text, reply_markup=markup, parse_mode='html')
        except IndexError:
            self.finish_test(chat_id)

    def finish_test(self, chat_id):
        with open('content/psyho_types.png', 'rb') as psyho_types_image:
            self.bot.send_photo(chat_id, psyho_types_image)
        text = 'Спасибо за прохождение теста<b>\n"✅Ваш результат: </b>\n\nДоминирующий:  {0}\nВлиятельный: {1}\n' \
               'Устойчивый: {2}\nСоотвествующий: {3}\n\n📌Вашим ведущим психотипом является тот, который набрал ' \
               'наибольшее количество очков.\n\nЕсли все остальные психотипы набрали значительно меньше очков, то они' \
               ' вам не свойственны.\n\n🔸Если есть еще один выраженный психотип, который набрал столько же или на 1-2' \
               ' очка меньше, то это – ваш второстепенный стиль поведения, который может вносить коррективы в ' \
               'поведение.\n\n\nУспехов!'.format(*self.types_scores.values())
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Хочу пройти еще раз', callback_data='RESTART_TEST'))
        self.bot.send_message(chat_id, text, reply_markup=markup, parse_mode='html')

    def start_test(self, chat_id):
        self.send_question(chat_id)


class SimpleUserTestTeamwork:
    def __init__(self, msg, bot_ref, texts):
        self.on_test = False
        self.bot = bot_ref
        self.try_times = 0
        self.id = msg.chat.id
        self.test = DISCTest('DISC.xlsx', bot_ref, texts)
        self.auth(msg)

    def auth(self, msg):
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
                logger.write(f'[Тестобот "DISC"]: Пользователь с id: {msg.chat.id} Авторизация прошла успешно!'
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
                    logger.write(f'[Тестобот "DISC"]: Пользователь с id: {msg.chat.id} Ошибка авторизации!  - '
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
            self.test = DISCTest('DISC.xlsx', self.bot, self.test.texts)
            self.test.start(call.message.chat.id)
        else:
            self.test.handler(call)


env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
API_TOKEN = os.getenv('API_TOKEN_ILYIN')
bot = telebot.TeleBot(API_TOKEN)
users = {}
texts_literal = {
        'DISCLAIMER': 'Отлично!\n\n<b>Пожалуйста, внимательно прочитайте эту информацию:</b>\n\nПрочитайте ситуации,'
                      ' вживитесь в них.\n\n☝️Отвечайте так, как вы обычно поступаете (если вы были в подобной '
                      'ситуации) или как вам действительно хочется поступить (если ситуация вам не знакома).',
        'START': 'Добрый день 👋🏼\n\n<b>Готовы пройти тест на определение своего психотипа?</b>'
    }


@bot.message_handler(content_types='text')
def handler(message):
    if message.text == '/start':
        try:
            users[message.chat.id].handler(message)
        except KeyError:
            users[message.chat.id] = SimpleUserTestTeamwork(message, bot, texts_literal)
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
        users[call.message.chat.id] = SimpleUserTestTeamwork(call.message, bot, texts_literal)


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
        'server.socket_port': 7779,
        'engine.autoreload.on': False
    })
    cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
