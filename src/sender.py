import zmq.green as zmq
import time


def main():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:9500")

    while True:
        socket.send('{"PING" : ' + str(time.time()) + '}')
        time.sleep(1)

if __name__ == '__main__':
    main()
