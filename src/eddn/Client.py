import zlib
import zmq.green as zmq
import simplejson
import sys


def main():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)

    subscriber.connect('tcp://localhost:9500')
    subscriber.setsockopt(zmq.SUBSCRIBE, "")

    while True:
        market_json = zlib.decompress(subscriber.recv())
        market_data = simplejson.loads(market_json)
        print market_data
        sys.stdout.flush()

if __name__ == '__main__':
    main()
