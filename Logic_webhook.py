import telebot
from telebot import apihelper
import random
import datetime
from telebot import types
from openpyxl import load_workbook
from telebot import apihelper
import re
import re
import os
from dotenv import load_dotenv
from threading import Timer
import cherrypy


def create_test_data(path='LOGIC.xlsx', rows=50, cols=5):
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
            col = col[2:5]
        res.append(col)
    print(res)
    for i in res:
        if len(i) != 3:
            tmp = i[1:5]
            test.update([(tmp[0], {'a_numbers': [], 'answers': [], 'scores': []})])
            test[tmp[0]]['a_numbers'].append(tmp[1])
            test[tmp[0]]['answers'].append(tmp[2])
            test[tmp[0]]['scores'].append(tmp[3])
        else:
            test[tmp[0]]['a_numbers'].append(i[0])
            test[tmp[0]]['answers'].append(i[1])
            test[tmp[0]]['scores'].append(i[2])
    return test


class LogicTest:
    def __init__(self, bot_ref, texts):
        self.texts = texts
        self.bot = bot_ref
        self.timer = None
        self.tmp = None
        self.state = 'NO_REG'
        self.q_ptr = 0
        self.score = 0
        self.correct_answer = None
        self.flag = None
        self.cur_question = 1
        self.msg = None
        self.questions = create_test_data()

    def set_timer(self, seconds: int, func_name) -> Timer:
        return Timer(seconds, func_name)

    def timer1_alert(self) -> None:
        chat_id = self.tmp
        self.bot.send_message(chat_id, '<b>Ой-ой!\n🔶До окончания теста осталось 5 минут</b>\n\nПродолжайте вводить '
                                       'ответ в поле ниже', parse_mode='html')
        self.timer = self.set_timer(300, self.timers_end)
        self.timer.start()

    def timers_end(self) -> None:
        chat_id = self.tmp
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Хочу пройти еще раз', callback_data='RESTART_TEST'))
        self.bot.send_message(chat_id, '<b>Вы не успели пройти тест за отведенное время 😔</b>\n\nПопробуете еще раз?',
                              reply_markup=markup, parse_mode='html')

    @staticmethod
    def creating_word_base(words):
        return {i: 0 for i in words}

    def change_state(self, new_state):
        self.state = new_state

    def return_cur_text(self):
        return self.texts[self.state]

    def input_answer(self, message):
        tmp = 0
        answ = [int(i) for i in re.findall(r'\d', message.text)]
        print(answ)
        if len(answ) == 0:
            self.bot.send_message(message.chat.id, 'Вы не ввели ни одного числа, пожалуйста, повторите ввод!')
        elif self.q_ptr <= 5 and (len(answ) >= 2 or 0 in answ or max(answ) > 2):
            self.bot.send_message(message.chat.id, 'Тут нет такого варианта ответа 🤓\nПожалуйста, напишите вариант '
                                                   'ответа 1 или 2 и отправьте мне.')
        elif 0 in answ and len(answ) >= 2:
            self.bot.send_message(message.chat.id, 'Вы сломали мою логику)\n\nЕсли верные ответы есть, тогда зачем вы пишете 0? 🤓\n\n'
                                  '<b>Пожалуйста введите 0, если считаете, что ни один вариант не является верным,'
                                  ' либо впишите цифру(ы) варианта ответа.</b>', parse_mode='html')
        elif max(answ) > 5:
            self.bot.send_message(message.chat.id,
                                  'Вы сломали мою логику 🤓\nВарианты ответа от 0 до 5, пожалуйста, выбирайте из них\n\n'
                                  '<b>Пожалуйста введите 0, если считаете, что ни один вариант не является верным, '
                                  'либо впишите цифру(ы) варианта ответа.</b>', parse_mode='html')
        else:
            if answ == self.correct_answer:
                self.score += 1
            self.q_ptr += 1
            self.send_question(message.chat.id)

    def disclaimer(self, chat_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Да, все понятно', callback_data='START_TEST'))
        self.bot.send_message(chat_id, self.return_cur_text(), reply_markup=markup, parse_mode='html')

    def start(self, chat_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Да, я хочу пройти', callback_data='CALL_DISC'))
        self.bot.send_message(chat_id, self.return_cur_text(), reply_markup=markup, parse_mode='html')

    def load_correct_answers(self):
        ind = self.questions[list(self.questions.keys())[self.q_ptr]]['scores']
        tmp = []
        for i in range(len(ind)):
            if ind[i] == 1:
                if i == 5:
                    tmp.append(0)
                else:
                    tmp.append(i + 1)

        self.correct_answer = tmp
        print(tmp)

    def return_question_text(self):
        question = list(self.questions.keys())[self.q_ptr]
        numbers, answers = self.questions[question]['a_numbers'], self.questions[question]['answers']
        answers_text = ''
        for i,j in zip(numbers, answers):
            answers_text += f'<b>{i}</b>. {j}\n'
        if self.q_ptr <=5:
            return f'<b>{self.q_ptr + 1} из 12</b>\n\n<b>{question}</b>\n\n{answers_text}\n\nВведите ниже ваш ответ,' \
                   f' <i>например</i>: <b>1</b>'
        else:
            return f'<b>{self.q_ptr + 1} из 12</b>\n\n<b>{question}</b>\n\n{answers_text}\n\nВведите ниже ваш ответ,' \
                   f' <i>например</i>:<b> 2</b>\n\n<i>Если вы считаете, что верных ответов несколько, вводите их через ' \
                   f'запятую.</i>\n\n<i>В случае если вы считаете, что ни один вариант <b>не является верным, введите ' \
                   f'0 (ноль)</b></i>'

    def send_question(self, chat_id):
        try:
            self.bot.send_message(chat_id, self.return_question_text(), parse_mode='html')
            self.load_correct_answers()
        except IndexError:
            self.finish_test(chat_id)

    def finish_test(self, chat_id):
        self.change_state('END_TEST')
        text = f'Спасибо за прохождение теста!\n\n<b>✅Ваш результат: {self.score}</b>\n\n<b>0-2</b>: Вам стоит серьезно ' \
               f'задуматься...\n\n<b>3-6</b>: Логика у вас есть. Но ее мало. Показаны тренировки.\n\n<b>7-10</b>: Хороший' \
               f' результат! Есть и способности, и навыки\n\n<b>11-12</b>: Блестящий результат!'
        self.timer.cancel()
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Хочу пройти еще раз', callback_data='RESTART_TEST'))
        self.bot.send_message(chat_id, text, reply_markup=markup, parse_mode='html')

    def start_test(self, chat_id):
        self.tmp = chat_id
        self.timer = self.set_timer(600, self.timer1_alert)
        self.timer.start()
        self.change_state('INPUT_ANSWER')
        self.send_question(chat_id)


class SimpleUserLogicTest:
    def __init__(self, msg, bot_ref, texts):
        self.on_test = False
        self.bot = bot_ref
        self.id = msg.chat.id
        self.try_times = 0
        self.on_test = False
        self.test = LogicTest(bot_ref, texts)
        self.auth(msg)

    def auth(self, msg):
        self.bot.send_message(msg.chat.id, 'Пожалуйста, введите код доступа заглавными буквами <b>без пробелов</b> и'
                                           ' знаков препинания\n\n<b>Например:</b> <i>HW2L</i>', parse_mode='html')
        self.bot.register_next_step_handler(msg, self.get_code)

    def get_code(self, msg):
        date = datetime.datetime.now()
        date += datetime.timedelta(seconds=3600 * 3)
        key = f'SW{date.month}{date.day}{str(date.year)[2::]}'
        print(key)
        if msg.text == key:
            with open('logger.txt', 'a') as logger:
                logger.write(f'[Тестобот "Логика"]: Пользователь с id: {msg.chat.id} Авторизация прошла успешно!'
                             f' - {datetime.datetime.today()}\n')
            self.test.change_state('START')
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
                    logger.write(f'[Тестобот "Логика"]: Пользователь с id: {msg.chat.id} Ошибка авторизации!  - '
                                 f'{datetime.datetime.today()}\n')
                self.bot.send_message(msg.chat.id, 'Вы слишком много раз ввели неверный код.\n\nДля решения опишите'
                                                   ' проблему Лине, она поможет ;)\n@lina_chandler')

    def handler(self, message):
        self.bot.send_message(message.chat.id, 'У вас нет необходимости в данный момент писать мне. '
                                               'Просто нажимайте на кнопки :)')

    def callback_handler(self, call):
        self.test.msg = call.message
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
            self.test = LogicTest(self.bot, self.test.texts)
            self.test.start(call.message.chat.id)

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
API_TOKEN = os.getenv('API_TOKEN_LOGIC')
bot = telebot.TeleBot(API_TOKEN)
try:
    os.mkdir('logs')
    os.mkdir('logs/logic_logs')
except OSError as e:
    print(f'Already created - {e}')
users = {}
texts_literal = {
        'DISCLAIMER': 'Отлично!\n\nЭтот тест поможет вам оценить, насколько «чисто» вы умеете делать выводы с точки '
                      'зрения логики.\n\n<b>📍 Пожалуйста, внимательно прочитайте эту информацию:</b>\n\n✅В каждом '
                      'задании может быть несколько правильных ответов, один или не быть вообще.\n\n<b>Заранее '
                      'предупреждаем:</b> содержание утверждений абсурдно, но логически безупречно.\n\n⏳ На весь тест '
                      'отводится 15 минут\n\nПостарайтесь быстро и правильно ответить на следующие 12 утверждений:',
        'START': 'Добрый день 👋🏼\n\n<b>Готовы пройти тест на логику?</b>'
    }

@bot.message_handler(content_types='text')
def handler(message):
    if message.text == '/start':
        try:
            users[message.chat.id].handler(message)
        except KeyError:
            users[message.chat.id] = SimpleUserLogicTest(message, bot, texts_literal)
    else:
        try:
            if users[message.chat.id].test.state == 'INPUT_ANSWER':
                users[message.chat.id].test.input_answer(message)
            elif users[message.chat.id].test.state == 'BLOCKED':
                bot.send_message(message.chat.id, 'Вам не нужно на данный момент вводить никакой текст. Просто нажимайт'
                                                  'e кнопки! :)')
            else:
                bot.send_message(message.chat.id, 'Вам не нужно на данный момент вводить никакой текст. Просто нажимайт'
                                                      'e кнопки! :)')
        except KeyError:
            bot.send_message(message.chat.id, 'Введите команду <i>/start</i>', parse_mode='html')

@bot.callback_query_handler(func=lambda call: True)
def smo(call):
    try:
        users[call.message.chat.id].callback_handler(call)
    except KeyError as e:
        users[call.message.chat.id] = SimpleUserLogicTest(call.message, bot, texts_literal)

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
        'server.socket_port': 7778,
        'engine.autoreload.on': False
    })
    cherrypy.quickstart(WebhookServer(), '/', {'/': {}})