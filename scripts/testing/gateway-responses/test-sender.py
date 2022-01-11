#!/usr/bin/env python3
# vim: tabstop=4 shiftwidth=4 expandtab smarttab textwidth=0 wrapmargin=0

import argparse
import requests

upload_url = 'https://dev.eddn.edcd.io:4432/upload/'

def send_message(url, message_filename):
    print(f'''
send_message:
    URL: {url}
    input file: "{message_filename}"
''')

    with open(message_filename, 'r') as f:
        msg = f.read()

        s = requests.Session()

        r = s.post(upload_url, data=msg)

        print(f'Response: {r!r}')
        print(f'Body: {r.content.decode()}')

if __name__ == "__main__":
    __parser = argparse.ArgumentParser(
        description='Send test messages to an EDDN /upload/ endpoint',
    )

    __parser.add_argument(
        '--url',
        metavar='<full URL of /upload/ endpoint>',
        help='The full URL of an EDDN /upload/ endpoint',
    )

    __parser.add_argument(
        'messagefile',
        metavar='<input file name>',
        help='Name of a file containing the body of the EDDN message to be sent',
    )

    args = __parser.parse_args()

    if args.url:
        # Allow for some short aliases, but NOT!!! for live !!!
        if args.url == 'beta':
            upload_url = 'https://beta.eddn.edcd.io:4431/upload/'

        elif args.url == 'dev':
            upload_url = 'https://dev.eddn.edcd.io:4432/upload/'

        else:
            upload_url = args.url

    send_message(upload_url, args.messagefile)
