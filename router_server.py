#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cherrypy
import requests
import telebot
import os
from dotenv import load_dotenv


env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

WEBHOOK_HOST = '45.133.245.170'
WEBHOOK_PORT = 443  # 443, 80, 88 или 8443
WEBHOOK_LISTEN = '0.0.0.0' # Слушаем отовсюду
WEBHOOK_SSL_CERT = 'webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = 'webhook_pkey.pem'  # Путь к закрытому ключу
WEBHOOK_URL_BASE = "https://{!s}:{!s}".format(WEBHOOK_HOST, WEBHOOK_PORT)

BOT_1_TOKEN = os.getenv('API_TOKEN_CSI')
BOT_2_TOKEN = os.getenv('API_TOKEN_CREATIVE_THINKING')
BOT_3_TOKEN = os.getenv('API_TOKEN_PAUL_ECMAN')
BOT_4_TOKEN = os.getenv('API_TOKEN_ILYIN')
BOT_5_TOKEN = os.getenv('API_TOKEN_KELLMAN')
BOT_6_TOKEN = os.getenv('API_TOKEN_TEAMROLES')
BOT_7_TOKEN = os.getenv('API_TOKEN_HERZBERG')
BOT_8_TOKEN = os.getenv('API_TOKEN_LOGIC')
BOT_9_TOKEN = os.getenv('API_TOKEN_DISC')
BOT_10_TOKEN = os.getenv('API_TOKEN_DESIGN_TEST')
BOT_11_TOKEN = os.getenv('API_TOKEN_RITORIKA_TEST')
BOT_12_TOKEN = os.getenv('API_TOKEN_EDSTYLE')
BOT_13_TOKEN = os.getenv('API_TOKEN_HECKHAUSEN')

BOT_1_ADDRESS = "http://127.0.0.1:7771"
BOT_2_ADDRESS = "http://127.0.0.1:7772"
BOT_3_ADDRESS = "http://127.0.0.1:7773"
BOT_4_ADDRESS = "http://127.0.0.1:7774"
BOT_5_ADDRESS = "http://127.0.0.1:7775"
BOT_6_ADDRESS = "http://127.0.0.1:7776"
BOT_7_ADDRESS = "http://127.0.0.1:7777"
BOT_8_ADDRESS = "http://127.0.0.1:7778"
BOT_9_ADDRESS = "http://127.0.0.1:7779"
BOT_10_ADDRESS = "http://127.0.0.1:7781"
BOT_11_ADDRESS = "http://127.0.0.1:7782"
BOT_12_ADDRESS = "http://127.0.0.1:7783"
BOT_13_ADDRESS = "http://127.0.0.1:7784"

bot_1 = telebot.TeleBot(BOT_1_TOKEN)
bot_2 = telebot.TeleBot(BOT_2_TOKEN)
bot_3 = telebot.TeleBot(BOT_3_TOKEN)
bot_4 = telebot.TeleBot(BOT_4_TOKEN)
bot_5 = telebot.TeleBot(BOT_5_TOKEN)
bot_6 = telebot.TeleBot(BOT_6_TOKEN)
bot_7 = telebot.TeleBot(BOT_7_TOKEN)
bot_8 = telebot.TeleBot(BOT_8_TOKEN)
bot_9 = telebot.TeleBot(BOT_9_TOKEN)
bot_10 = telebot.TeleBot(BOT_10_TOKEN)
bot_11 = telebot.TeleBot(BOT_11_TOKEN)
bot_12 = telebot.TeleBot(BOT_12_TOKEN)
bot_13 = telebot.TeleBot(BOT_13_TOKEN)

# Описываем наш сервер
class WebhookServer(object):

    # Первый бот (название функции = последняя часть URL вебхука)
    @cherrypy.expose
    def TeamrolesTest(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            # Вот эта строчка и пересылает все входящие сообщения на нужного бота
            requests.post(BOT_6_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

    # Второй бот (действуем аналогично)
    @cherrypy.expose
    def KellmanTest(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            requests.post(BOT_5_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

    @cherrypy.expose
    def EcmanTest(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            requests.post(BOT_3_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

    @cherrypy.expose
    def CSITest(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            requests.post(BOT_1_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

    @cherrypy.expose
    def IlyinTest(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            requests.post(BOT_4_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

    @cherrypy.expose
    def CTTest(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            requests.post(BOT_2_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

    @cherrypy.expose
    def HerzbergTest(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            requests.post(BOT_7_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

    @cherrypy.expose
    def LogicTest(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            requests.post(BOT_8_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

    @cherrypy.expose
    def DISCTest(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            requests.post(BOT_9_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

    @cherrypy.expose
    def DesignTest(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            requests.post(BOT_10_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

    @cherrypy.expose
    def RitorikaTest(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            requests.post(BOT_11_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

    @cherrypy.expose
    def EDStyle(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            requests.post(BOT_12_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

    @cherrypy.expose
    def Heckhausen(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            requests.post(BOT_13_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)


if __name__ == '__main__':

    bot_1.remove_webhook()
    bot_1.set_webhook(url=f'https://{WEBHOOK_HOST}/CSITest',
                      certificate=open(WEBHOOK_SSL_CERT, 'r'))

    bot_2.remove_webhook()
    bot_2.set_webhook(url=f'https://{WEBHOOK_HOST}/CTTest',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    bot_3.remove_webhook()
    bot_3.set_webhook(url=f'https://{WEBHOOK_HOST}/EcmanTest',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    bot_4.remove_webhook()
    bot_4.set_webhook(url=f'https://{WEBHOOK_HOST}/IlyinTest',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    bot_5.remove_webhook()
    bot_5.set_webhook(url=f'https://{WEBHOOK_HOST}/KellmanTest',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    bot_6.remove_webhook()
    bot_6.set_webhook(url=f'https://{WEBHOOK_HOST}/TeamrolesTest',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    bot_7.remove_webhook()
    bot_7.set_webhook(url=f'https://{WEBHOOK_HOST}/HerzbergTest',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    bot_8.remove_webhook()
    bot_8.set_webhook(url=f'https://{WEBHOOK_HOST}/LogicTest',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    bot_9.remove_webhook()
    bot_9.set_webhook(url=f'https://{WEBHOOK_HOST}/DISCTest',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    bot_10.remove_webhook()
    bot_10.set_webhook(url=f'https://{WEBHOOK_HOST}/DesignTest',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    bot_11.remove_webhook()
    bot_11.set_webhook(url=f'https://{WEBHOOK_HOST}/RitorikaTest',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    bot_12.remove_webhook()
    bot_12.set_webhook(url=f'https://{WEBHOOK_HOST}/EDStyle',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    bot_13.remove_webhook()
    bot_13.set_webhook(url=f'https://{WEBHOOK_HOST}/Heckhausen',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    cherrypy.config.update({
        'server.socket_host': WEBHOOK_LISTEN,
        'server.socket_port': WEBHOOK_PORT,
        'server.ssl_module': 'builtin',
        'server.ssl_certificate': WEBHOOK_SSL_CERT,
        'server.ssl_private_key': WEBHOOK_SSL_PRIV,
        'engine.autoreload.on': False
    })
    cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
