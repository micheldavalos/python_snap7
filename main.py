import snap7
from snap7.util import get_int


if __name__ == '__main__':
    client = snap7.client.Client()
    client.connect("192.168.0.254", 0, 0)
    data = client.db_read(2, 14, 2)
    contador = get_int(data, 0)
    print(contador)


