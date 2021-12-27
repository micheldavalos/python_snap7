import snap7
from snap7.util import get_int

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

try:
    import asyncio
except ImportError:
    import trollius as asyncio

client = snap7.client.Client()
client.connect("192.168.0.254", 0, 0)

def read_plc():
    data = client.db_read(2, 14, 2)
    contador = get_int(data, 0)
    # print(contador)
    logging.info(contador)


if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(read_plc, 'interval', seconds=0.5)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass



