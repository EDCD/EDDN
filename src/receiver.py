import zmq.green as zmq
import sys


def main():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)

    subscriber.setsockopt(zmq.SUBSCRIBE, "")
    subscriber.connect('tcp://eddn-gateway.elite-markets.net:9500')

    while True:
        print subscriber.recv()
        sys.stdout.flush()

if __name__ == '__main__':
    main()
