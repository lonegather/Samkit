import json
import asyncio
from importlib import reload
import unreal_engine as ue


def ticker_loop(delta_time):
    try:
        loop.stop()
        loop.run_forever()
    except Exception as e:
        ue.log_error(e)
    return True


# this is called whenever a new client connects
async def new_client_connected(reader, writer):
    import asset_import
    reload(asset_import)

    name = writer.get_extra_info('peername')
    ue.log('new client connection from {0}'.format(name))
    while True:
        # wait for a line
        data = await reader.readline()
        if not data:
            break
        asset_import.import_asset(**json.loads(data.decode()))

    ue.log('client {0} disconnected'.format(name))


# this spawns the server
# the try/finally trick allows for gentle shutdown of the server
async def spawn_server(host, port):
    try:
        coro = await asyncio.start_server(new_client_connected, host, port, reuse_address=True)
        ue.log('tcp server spawned on {0}:{1}'.format(host, port))
        await coro.wait_closed()
    finally:
        coro.close()
        ue.log('tcp server ended')


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
ticker = ue.add_ticker(ticker_loop)

# cleanup previous tasks
for task in asyncio.Task.all_tasks():
    task.cancel()

asyncio.ensure_future(spawn_server('127.0.0.1', 8888))
