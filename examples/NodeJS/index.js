import zlib from 'zlib';
import zmq from 'zeromq';

const SOURCE_URL = 'tcp://eddn.edcd.io:9500';

async function run() {
  const sock = new zmq.Subscriber;

  sock.connect(SOURCE_URL);
  sock.subscribe('');
  console.log('EDDN listener connected to:', SOURCE_URL);

  for await (const [src] of sock) {
    const msg = JSON.parse(zlib.inflateSync(src));
    console.log(msg);
  }
}

run();
