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


class PaulEcmanTest:
    def __init__(self, user_id, bot_ref, texts):
        self.timer = None
        self.id = user_id
        self.texts = texts
        self.bot = bot_ref
        self.buffer = None
        self.state = 'START'
        self.flag = None
        self.cur_question_ptr = 0
        self.answers = ('sadness', 'disgust', 'sadness', 'pleasure', 'anger', 'fear', 'disgust', 'anger', 'anger',
                        'fear', 'anger', 'fear', 'surprise', 'contempt')
        self.score = 0

    def change_state(self, new_state):
        self.state = new_state

    def return_cur_text(self):
        return self.texts[self.state]

    def start_timer(self):
        self.timer = Timer(3, self.edit_photo)
        self.timer.start()

    def edit_photo(self):
        self.bot.delete_message(self.buffer.chat.id, self.buffer.message_id)
        text = f'<b>Фото {self.cur_question_ptr + 1} из 14</b>\n\nКакая эмоция больше всего соответствует той, что вы' \
               f' только что увидели на картинке?'
        markup = types.InlineKeyboardMarkup(row_width=2)
        button_labels = ('Гнев', 'Страх', 'Печаль', 'Отвращение', 'Презрение', 'Удивление', 'Удовольствие')
        button_callbacks = ('0_0_anger', '0_1_fear', '1_0_sadness', '1_1_disgust', '2_0_contempt', '2_1_surprise',
                            '3_0_pleasure')
        markup.add(*[types.InlineKeyboardButton(text=i, callback_data=j) for i, j in zip(button_labels,
                                                                                         button_callbacks)])
        self.bot.send_message(self.buffer.chat.id, text=text, reply_markup=markup, parse_mode='html')

    def validate_editing(self, new_args):
        pass

    def handler(self, call):
        if call.data != 'NO_CB':
            row, number, emotion = call.data.split('_')
            print(call.message.json['reply_markup']['inline_keyboard'])
            if emotion == self.answers[self.cur_question_ptr]:
                self.score += 1
            text = f"<b>✅Вы выбрали " \
                   f"{call.message.json['reply_markup']['inline_keyboard'][int(row)][int(number)]['text']}</b>"
            self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       text=text, reply_markup=None, parse_mode='html')
            self.cur_question_ptr += 1
            self.send_question(call.message.chat.id)
        else:
            self.bot.send_message(call.message.chat.id, 'Не надо нажимать на эту кнопку')

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
            with open(os.path.join('content', f'{self.cur_question_ptr + 1}.jpg'), 'rb') as emotion_photo:
                self.buffer = self.bot.send_photo(chat_id, emotion_photo, caption=f'<b>Фото {self.cur_question_ptr + 1}'
                                                                                  f' из 14</b>', parse_mode='html')
                self.start_timer()
        except (IndexError, FileNotFoundError):
            self.finish_test(chat_id)

    def finish_test(self, chat_id):
        text = f'Спасибо за прохождение теста на распознавание эмоций!\n\n<b>Верных ответов: {self.score}</b>'
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Хочу пройти еще раз', callback_data='RESTART_TEST'))
        self.bot.send_message(chat_id, text, reply_markup=markup, parse_mode='html')

    def start_test(self, chat_id):
        self.send_question(chat_id)


class SimpleUserPaulEcmanTest:
    def __init__(self, msg, bot_ref, texts):
        self.on_test = False
        self.bot = bot_ref
        self.id = msg.chat.id
        self.try_times = 0
        self.test = PaulEcmanTest(msg.chat.id, bot_ref, texts)
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
        print(key)
        if msg.text == key:
            with open('logger.txt', 'a') as logger:
                logger.write(f'[Тестобот "Полл Экман"]: Пользователь с id: {msg.chat.id} Авторизация прошла успешно!'
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
                    logger.write(f'[Тестобот "Полл Экман"]: Пользователь с id: {msg.chat.id} Ошибка авторизации!  - '
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
            self.test = PaulEcmanTest(call.message.chat.id, self.bot, self.test.texts)
            self.test.start(call.message.chat.id)
        else:
            self.test.handler(call)


env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
API_TOKEN = os.getenv('API_TOKEN_PAUL_ECMAN')
bot = telebot.TeleBot(API_TOKEN)
users = {}
texts_literal = {
        'DISCLAIMER': 'Отлично!\n\n<b>Пожалуйста, внимательно прочитайте эту информацию:</b>\n\n🔹Вам будет показано 14 '
                      'фотографий яркого проявления разных человеческих эмоций\n\n⏱На одно изображение вам будет дано 3'
                      ' секунды, чтобы вы смогли "считать" эмоцию.\n\n✅Далее выберите в списке из предложенных эмоций '
                      'ту, которая, по вашему мнению, наиболее соответствует выражению лица на фотографии.',
        'START': 'Добрый день 👋🏼\n\n<b>Готовы пройти тест на распознавание эмоций?</b>'
    }


@bot.message_handler(content_types='text')
def handler(message):
    if message.text == '/start':
        try:
            users[message.chat.id].handler(message)
        except KeyError:
            users[message.chat.id] = SimpleUserPaulEcmanTest(message, bot, texts_literal)
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
        users[call.message.chat.id] = SimpleUserPaulEcmanTest(call.message, bot, texts_literal)


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
        'server.socket_port': 7773,
        'engine.autoreload.on': False
    })
    cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
