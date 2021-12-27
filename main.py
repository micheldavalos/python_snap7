import snap7
from snap7.util import get_int, get_string, get_bool, get_real

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


def read_plc_int():
    data = client.db_read(2, 14, 2)
    contador = get_int(data, 0)
    # print(contador)
    logging.info(contador)


def read_plc_string():
    data = client.db_read(2, 2, 12)
    s = get_string(data, 0, 12)
    logging.info(s)


def call_read_plc():
    read_plc_int()
    read_plc_string()


class DBObject(object):
    pass


offsets = {"Bool": 2, "Int": 2, "Real": 4, "DInt": 6, "String": 12}

db = \
    """
jiiu Bool 0.0
b2 Bool 0.1
nombre String 2.0
contador Int 14.0
slider Int 16.0
"""


def DBRead(plc, db_num, length, dbitems):
    data = plc.read_area(snap7.types.Areas['DB'], db_num, 0, length)
    obj = DBObject()
    for item in dbitems:
        value = None
        offset = int(item['bytebit'].split('.')[0])

        if item['datatype'] == 'Real':
            value = get_real(data, offset)

        if item['datatype'] == 'Bool':
            bit = int(item['bytebit'].split('.')[1])
            value = get_bool(data, offset, bit)

        if item['datatype'] == 'Int':
            value = get_int(data, offset)

        if item['datatype'] == 'String':
            value = get_string(data, offset, 12)

        obj.__setattr__(item['name'], value)

    return obj


def get_db_size(array, bytekey, datatypekey):
    seq, length = [float(x[bytekey]) for x in array], [x[datatypekey] for x in array]
    idx = seq.index(seq[-1])
    lastByte = int(seq[-1]) + (offsets[length[idx]])
    return lastByte


itemlist = filter(lambda a: a != '', db.split('\n'))
deliminator = ' '
items = [
    {
        "name": x.split(deliminator)[0],
        "datatype": x.split(deliminator)[1],
        "bytebit": x.split(deliminator)[2]
    } for x in itemlist
]


def get_db():
    # get length of datablock
    length = get_db_size(items, 'bytebit', 'datatype')
    db = DBRead(client, 2, length, items)
    logging.info(f"jiiu: {db.jiiu}, b2: {db.b2}, nombre: {db.nombre}, contador: {db.contador}, slider: {db.slider}")


if __name__ == '__main__':
    # client.disconnect()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(get_db, 'interval', seconds=0.5)
    # scheduler.add_job(call_read_plc, 'interval', seconds=0.5)
    # scheduler.add_job(read_plc_string, 'interval', seconds=0.8)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
