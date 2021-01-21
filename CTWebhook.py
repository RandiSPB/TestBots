import telebot
from telebot import apihelper
import random
from telebot import types
from openpyxl import load_workbook
from telebot import apihelper
import re
import re
import os
from dotenv import load_dotenv
from SimpleNaturalLanguageProccesor import NaturalLanguageProcessor
from threading import Timer
import cherrypy
import datetime


def parse_from_xlsx_data(data):
    pass


class CreativeThinkingTest:
    def __init__(self, bot_ref, texts, nlp_ref, words=('я', 'мне', 'меня', 'мной', 'мое', 'моя', 'мои', 'моего', 'моей',
                                                       'моих', 'моему', 'моим', 'мою', 'моими', 'о моем', 'о моей',
                                                       'о моих', 'мною', 'мой', 'по-моему', 'моё')):
        self.natural_language_processor = nlp_ref
        self.texts = texts
        self.bot = bot_ref
        self.timer = None
        self.tmp = None
        self.state = 'START'
        self.flag = None
        self.cur_question = 1
        self.msg = None
        self.word_base = self.creating_word_base(words)
        self.questions = ['Лет так через двенадцать ...', 'В прошлом ...', 'В настоящее время ...', 'Условие для ...',
                          'Принимая во внимание ...', 'В случае ...', 'Если бы даже ...', 'До сих пор ...',
                          'С недавнего времени ...', 'Только с тех пор как ...', 'Легче всего ...', 'На самом деле ...',
                          'Несмотря на то, что ...', 'Чем дольше ...', 'Жаль, что ...',  'Несколько лет тому назад ...',
                          'Неправда, что ...', 'Придет такой день, когда ...', 'Самое большое ...',
                          'Вряд ли возможно, что ...']

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
        self.natural_language_processor.simple_process(self.word_base, message.text)
        print(self.word_base)
        self.send_question(message.chat.id)

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
            cur_question = random.choice(self.questions)
            self.bot.send_message(chat_id, f'{self.cur_question} из 20\n\n<b>{cur_question}</b>\n\n<i>Продолжите '
                                           f'фразу в поле ниже</i>', parse_mode='html')
            self.questions.pop(self.questions.index(cur_question))
            self.cur_question += 1
        except IndexError:
            self.finish_test(chat_id)

    def finish_test(self, chat_id):
        self.change_state('END_TEST')
        text = f'Спасибо за прохождение теста!\n\n<b>Ваш индекс: {sum(list(self.word_base.values()))}</b>\n\nПодробную'\
               f' интерпретацию результата Вы узнаете у тренера\n\nУспехов!'
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


class SimpleUserCreativeThinkingTest:
    def __init__(self, msg, bot_ref, texts, nlp_ref):
        self.on_test = False
        self.bot = bot_ref
        self.try_times = 0
        self.id = msg.chat.id
        self.test = CreativeThinkingTest(bot_ref, texts, nlp_ref)
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
                logger.write(f'[Тестобот "Креативное мышление"]: Пользователь с id: {msg.chat.id} Авторизация прошла успешно!'
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
                    logger.write(f'[Тестобот "Креативное мышление"]: Пользователь с id: {msg.chat.id} Ошибка авторизации!  - '
                                 f'{datetime.datetime.today()}\n')
                self.bot.send_message(msg.chat.id, 'Вы слишком много раз ввели неверный код.\n\nДля решения опишите'
                                                   ' проблему Лине, она поможет ;)\n@lina_chandler')

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
            self.test = CreativeThinkingTest(self.bot, self.test.texts, self.test.natural_language_processor)
            self.test.start(call.message.chat.id)


env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
natural_language_processor = NaturalLanguageProcessor()
API_TOKEN = os.getenv('API_TOKEN_CREATIVE_THINKING')
bot = telebot.TeleBot(API_TOKEN)
users = {}
texts_literal = {
        'DISCLAIMER': 'Отлично!\n\n<b>☝Пожалуйста, внимательно прочитайте эту информацию:</b>\n\nТест содержит 20 '
                      'незаконченных предложений. Вам необходимо дополнить каждое из них так, чтобы получились '
                      'предложения, в которых выражена законченная мысль.\n\n<b>✅Сразу записывайте первое пришедшее в '
                      'голову</b> окончание незаконченного предложения.\n\nПишите без страха, этот тест останется с '
                      'вами и никто его не увидит. Старайтесь работать быстро.\n\n⏰Время на выполнение задания:\n'
                      '<b>15 минут.</b>\n\nВсе прочитали? 😊',
        'START': 'Приветствую!\n\n<b>Готовы пройти тест на творческое мышление?</b>'
    }


@bot.message_handler(content_types='text')
def handler(message):
    if message.text == '/start':
        try:
            users[message.chat.id].handler(message)
        except KeyError:
            users[message.chat.id] = SimpleUserCreativeThinkingTest(message, bot, texts_literal,
                                                                        natural_language_processor)
    else:
        if users[message.chat.id].test.state == 'INPUT_ANSWER':
            users[message.chat.id].test.input_answer(message)
        elif users[message.chat.id].test.state == 'BLOCKED':
            bot.send_message(message.chat.id, 'Вам не нужно на данный момент вводить никакой текст. Просто нажимайт'
                                              'e кнопки! :)')
        else:
            bot.send_message(message.chat.id, 'Вам не нужно на данный момент вводить никакой текст. Просто нажимайт'
                                                  'e кнопки! :)')


@bot.callback_query_handler(func=lambda call: True)
def smo(call):
    try:
        users[call.message.chat.id].callback_handler(call)
    except KeyError as e:
        users[call.message.chat.id] = SimpleUserCreativeThinkingTest(call.message, bot, texts_literal,
                                                                         natural_language_processor)

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
        'server.socket_port': 7772,
        'engine.autoreload.on': False
    })
    cherrypy.quickstart(WebhookServer(), '/', {'/': {}})


