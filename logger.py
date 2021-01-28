import cherrypy
import json


def logger_request(route_func):

    def wrapper_func(args):
        route_func(args)
        print(route_func.__name__)
        print(cherrypy.request.headers)
        length = int(cherrypy.request.headers['content-length'])
        print(f'lenght = {length}')
        print('----------------')
        json_string = cherrypy.request.body.read(length)
        print(json_string)
        print('-----------')
        #print(f'json : \n{json.dumps(json_string)}')
        print('---------')

    return wrapper_func
