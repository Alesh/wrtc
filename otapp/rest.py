import os.path
from aiohttp import web

routes = web.RouteTableDef()


@routes.post('/rest/v1/otapp/user/enter')
async def user_enter(request):
    """ JSON в запросе {'user_id': <user_id>}
    JSON в ответе {'state': [<sission_id or null>, <connected:bool>]} для пациента
    для доктора {`patients`: {<patient user_id>: [<sission_id or null>, <connected:bool>], ...}}
    """
    data = await request.json()
    data = request.app.user_enter(**data)
    return web.json_response(data)


@routes.post('/rest/v1/otapp/user/exit')
async def user_exit(request):
    """ JSON в запросе {'user_id': <user_id>} """
    data = await request.json()
    request.app.user_exit(**data)
    return web.Response(status=200)


@routes.post('/rest/v1/otapp/session/create')
async def create_session(request):
    """ JSON в запросе {'user_id': <user_id>}
    JSON в ответе {'api_key': <api_key>, 'session_id': <session_id>, 'token': <token>}"""
    data = await request.json()
    data = request.app.create_session(**data)
    return web.json_response(data)


@routes.post('/rest/v1/otapp/session/join')
async def join_to_session(request):
    """ JSON в запросе {'user_id': <user_id>, 'session_id':<session_id>}
    JSON в ответе {'api_key': <api_key>, 'session_id': <session_id>, 'token': <token>}"""
    data = await request.json()
    data = request.app.join_to_session(**data)
    return web.json_response(data)


@routes.post('/rest/v1/otapp/session/call')
async def call_from_session(request):
    """ JSON в запросе {'user_id': <user_id>, 'session_id':<session_id>, 'addressee':<addressee user_id>}
    """
    data = await request.json()
    request.app.call_from_session(**data)
    return web.Response(status=200)



routes.static('/', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wwwroot'), show_index=True)


if __name__ == '__main__':
    import sys
    import logging
    import getopt
    import otapp

    try:
        port = 5000
        debug = False
        opts, args = getopt.getopt(sys.argv[1:], "dp:", ['debug', 'port='])
    except getopt.GetoptError as exc:
        print(exc)
        print("Usage:"
              "\npython -m otapp.rest {options}"
              "\n\t-d,--debug          Debug mode"
              "\n\t-p,--port=<number>  Bind to port")
        sys.exit(2)

    for name, value in opts:
        if name in ('-d', '--debug'):
            debug = True
        elif name in ('-p', '--port'):
            port = int(value)

    logging.basicConfig(level=(logging.DEBUG if debug else logging.INFO))
    app = otapp.Application(logger=logging.root)
    app.add_routes(routes)
    web.run_app(app, port=port)
