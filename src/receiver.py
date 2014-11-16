import zmq.green as zmq
import sys


def main():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)

    subscriber.setsockopt(zmq.SUBSCRIBE, "")
    subscriber.connect('tcp://199.115.222.234:9500')

    while True:
        print subscriber.recv()
        sys.stdout.flush()

if __name__ == '__main__':
    main()
