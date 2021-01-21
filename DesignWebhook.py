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


def create_test_data(path='TEST_design.xlsx', rows=66, cols=5):
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


def normalize_test(test):
    res = []
    for i in test:
        indexs = []
        delt = 0
        for j in test[i]['scores']:
            if j == 1:
                indexs.append(test[i]['scores'].index(j, delt) + 1)
                delt += 1
            else:
                delt += 1
                continue
        res.append(indexs)
    return res


class DISCTest:
    def __init__(self, filename, bot_ref, texts):
        self.texts = texts
        self.bot = bot_ref
        self.state = 'START'
        self.flag = None
        self.message_buffer = None
        self.questions = create_test_data(filename)
        print(self.questions)
        self.cur_q = 0
        self.test_score = 0

    def change_state(self, new_state):
        self.state = new_state

    def return_cur_text(self):
        return self.texts[self.state]

    def validate_editing(self, new_args):
        pass

    def get_answer(self, message):
        try:
            answ = [int(i) for i in re.findall(r'\d+', message.text)]
            print(answ)
            try:
                tmp = normalize_test(self.questions)
                print(tmp)
                iter_score = 0
                res = []
                print(self.cur_q)
                q_numbers = len(self.questions[list(self.questions)[self.cur_q]]['answers'])
                if not answ:
                    raise ValueError
                print(list(self.questions)[self.cur_q])
                for i in answ:
                    print(i)
                    try:
                        if i > q_numbers:
                            raise ValueError
                        if i in tmp[self.cur_q] and i not in res:
                            res.append(i)
                            iter_score += 1
                            print(f'res = {res}')
                        elif i in tmp[self.cur_q] and i in res:
                            iter_score += 0
                        else:
                            iter_score -= 1
                    except IndexError as e:
                        print(e)
                if iter_score < 0:
                    iter_score = 0
                self.test_score += iter_score
                numbers1 = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
                question = list(self.questions)[self.cur_q]
                numbers = list('❌' for i in range(q_numbers))
                for i in tmp[self.cur_q]:
                    numbers[i - 1] = '✅'
                tmp = ''.join(
                    ['<b>{0}{2}.</b> {1}\n'.format(i, j, z) for i, j, z in zip(numbers,
                                                                               self.questions[question]['answers'],
                                                                               numbers1)])
                msg = '<b>{0}.</b> {1}\n\n{2}'.format(self.cur_q + 1, question, tmp)
                self.bot.edit_message_text(chat_id=message.chat.id, message_id=self.message_buffer.message_id, text=msg,
                                           parse_mode='html')
                self.cur_q += 1
                if self.cur_q < 16:
                    self.send_question(message.chat.id)
                    self.bot.register_next_step_handler(message, self.get_answer)
                else:
                    self.finish_test(message.chat.id)

            except ValueError as e:
                print(e)
                self.bot.send_message(message.chat.id, 'Простите, я не могу понять Ваш ответ. Попробуйте ввести его еще раз.')
                self.bot.register_next_step_handler(message, self.get_answer)
            except AttributeError as e:
                print(e)
                self.bot.send_message(message.chat.id, 'Простите, я не могу понять Ваш ответ. Попробуйте ввести его еще раз.')
                self.bot.register_next_step_handler(message, self.get_answer)
        except TypeError as e:
            print(e)
            self.bot.send_message(message.chat.id, 'Простите, я не могу понять Ваш ответ. Попробуйте ввести его еще раз.')
            self.bot.register_next_step_handler(message, self.get_answer)

    def handler(self, call):
        if call.data != 'NO_CB':
            self.bot.send_message(call.message.chat.id, 'Не надо нажимать на эту кнопку')

    def disclaimer(self, chat_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Да, все понятно', callback_data='START_TEST'))
        self.bot.send_message(chat_id, self.return_cur_text(), reply_markup=markup, parse_mode='html')

    def start(self, chat_id, message):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Да, я хочу пройти', callback_data='CALL_DISC'))
        self.bot.send_message(chat_id, self.return_cur_text(), reply_markup=markup, parse_mode='html')

    def send_question(self, chat_id):
        question = list(self.questions)[self.cur_q]
        numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        tmp = ''.join(['<b>{0}.</b> {1}\n'.format(i, j) for i, j in zip(numbers, self.questions[question]['answers'])])
        msg = '<b>{0}.</b> {1}\n\n{2}'.format(self.cur_q + 1, question, tmp)
        self.message_buffer = bot.send_message(chat_id, msg, parse_mode='html')

    def finish_test(self, chat_id):
        text = f'Спасибо за прохождение теста!\n\n✅Ваш результат: {int(self.test_score / 35 * 100)}%\n\n' \
               f'👇Чтобы пройти тест повторно, нажмите кнопку ниже:'
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Хочу пройти еще раз', callback_data='RESTART_TEST'))
        self.bot.send_message(chat_id, text, reply_markup=markup, parse_mode='html')

    def start_test(self, chat_id, message):
        self.send_question(chat_id)
        self.bot.register_next_step_handler(message, self.get_answer)

class SimpleUserTestDISC:
    def __init__(self, msg, bot_ref, texts):
        self.on_test = False
        self.bot = bot_ref
        self.try_times = 0
        self.id = msg.chat.id
        self.test = DISCTest('TEST_design.xlsx', bot_ref, texts)
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
                logger.write(f'[Тестобот "Design"]: Пользователь с id: {msg.chat.id} Авторизация прошла успешно!'
                             f' - {datetime.datetime.today()}\n')
            self.test.change_state('START')
            self.on_test = True
            self.test.start(msg.chat.id, msg)
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
                    logger.write(f'[Тестобот "Design"]: Пользователь с id: {msg.chat.id} Ошибка авторизации!  - '
                                 f'{datetime.datetime.today()}\n')
                self.bot.send_message(msg.chat.id, 'Вы слишком много раз ввели неверный код.\n\nДля решения опишите'
                                                   ' проблему Лине, она поможет ;)\n@lina_chandler')
    def handler(self, message):
        if self.on_test:
            self.bot.send_message(message.chat.id, 'Вы уже проходите тест!')
        else:
            self.on_test = True
            self.test.start(message.chat.id, message)

    def callback_handler(self, call):
        if call.data == 'CALL_DISC':
            self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       text=self.test.return_cur_text(), reply_markup=None, parse_mode='html')
            self.test.change_state('DISCLAIMER')
            self.test.disclaimer(call.message.chat.id)

        elif call.data == 'START_TEST':
            self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       text=self.test.return_cur_text(), reply_markup=None, parse_mode='html')
            self.test.start_test(call.message.chat.id, call.message)

        elif call.data == 'RESTART_TEST':
            self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       text=call.message.text, reply_markup=None, parse_mode='html')
            self.test = DISCTest('TEST_design.xlsx', self.bot, self.test.texts)
            self.test.start(call.message.chat.id, call.message)
        else:
            self.test.handler(call)


env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
API_TOKEN = os.getenv('API_TOKEN_DESIGN_TEST')
bot = telebot.TeleBot(API_TOKEN)
users = {}
texts_literal = {
        'DISCLAIMER': 'Предлагаю вам пройти небольшой тест из 15 вопросов.  Это займёт не более 10 минут. Тест '
                      'поможет проверить свои знания,полученные на тренинге, а также подготовит Вас к практике.\n\n'
                      '<b>Ответы вводятся через запятую в одну строку</b>\nНапример: 1,4',
        'START': 'Добрый день 👋🏼\n\nГотовы пройти тест на знания  "Профессиональная подготовка и дизайн соглашения"?'
    }


@bot.message_handler(content_types='text')
def handler(message):
    if message.text == '/start':
        try:
            users[message.chat.id].handler(message)
        except KeyError:
            users[message.chat.id] = SimpleUserTestDISC(message, bot, texts_literal)
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
        users[call.message.chat.id] = SimpleUserTestDISC(call.message, bot, texts_literal)


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
        'server.socket_port': 7781,
        'engine.autoreload.on': False
    })
    cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
