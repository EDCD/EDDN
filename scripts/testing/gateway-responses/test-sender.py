#!/usr/bin/env python3
# vim: tabstop=4 shiftwidth=4 expandtab smarttab textwidth=0 wrapmargin=0

import argparse
import requests
import zlib

upload_url = 'https://dev.eddn.edcd.io:4432/upload/'

def send_message(url, args):
    print(f'''
send_message:
    URL: {url}
    input file: "{args.messagefile}"
''')

    with open(args.messagefile, 'r') as f:
        msg = f.read()

        if args.formdata:
            if args.formdata == 'good':
                msg = 'data=' + msg

            elif args.formdata == 'bad':
                msg = 'BADLYENCODED=' + msg

        s = requests.Session()

        if args.gzip:
            # We assume that the argparse setup is enforcing the value being
            # valid, i.e. `'good'` if it's not `'bad'`.
            msg = zlib.compress(msg.encode('utf-8'))
            s.headers['Content-Encoding'] = 'gzip'

            if args.gzip == 'bad':
                # Prepend a character so it's not a valid gzip header
                msg = b'w' + msg

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
        '--formdata',
        choices=('good', 'bad'),
        help='Specify to form-encode the request body',
    )

    __parser.add_argument(
        '--gzip',
        choices=('good', 'bad'),
        help='Specify to gzip-compress the request body',
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

    send_message(upload_url, args)
