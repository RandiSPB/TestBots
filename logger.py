import cherrypy


def logger_request(route_func):

    def wrapper_func():
        print(route_func.__name__)
        print(cherrypy.request)
        route_func()

    return wrapper_func
