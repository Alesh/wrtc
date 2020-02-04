import asyncio
from aiohttp import web


async def main(port, debug):
    print(port, debug)


if __name__ == '__main__':
    import sys
    import getopt
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

    asyncio.run(main(port, debug))
