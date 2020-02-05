import asyncio
from aiohttp import web

routes = web.RouteTableDef()


@routes.post('/rest/v1/otapp/user/enter')
async def user_enter(request):
    data = await request.json()
    request.app.user_enter(**data)


@routes.post('/rest/v1/otapp/user/exit')
async def user_exit(request):
    data = await request.json()
    request.app.user_exit(**data)


@routes.post('/rest/v1/otapp/session/create')
async def create_session(request):
    data = await request.json()
    request.app.create_session(**data)


@routes.post('/rest/v1/otapp/session/join')
async def join_to_session(request):
    data = await request.json()
    request.app.join_to_session(**data)


@routes.post('/rest/v1/otapp/session/call')
async def call_from_session(request):
    data = await request.json()
    request.app.call_from_session(**data)


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
