require 'zlib'
require 'ffi-rzmq'
require 'json'
require 'pry-byebug'

trap "SIGINT" do
  puts "Quitting"
  exit 130
end

EDDN_RELAY   = 'tcp://eddn.edcd.io:9500'
EDDN_TIMEOUT = 60000

context    = ZMQ::Context.new
subscriber = context.socket(ZMQ::SUB)

subscriber.setsockopt(ZMQ::SUBSCRIBE, "")

while true do
  begin
    subscriber.connect(EDDN_RELAY)
    puts "Connected to EDDN"

    poller = ZMQ::Poller.new()
    poller.register(subscriber, ZMQ::POLLIN)

    while true do
      socks = poller.poll(EDDN_TIMEOUT)

      if socks
        msg     = ZMQ::Message.new()
        message = subscriber.recvmsg(msg, ZMQ::DONTWAIT)
        message = Zlib::Inflate.inflate(msg.copy_out_string)
        json    = JSON.parse(message)
        puts json
      else
        puts "Disconnected from EDDN (After timeout)"
        subscriber.disconnect(EDDN_RELAY)
        break
      end
    end

  rescue StandardError => e
    puts "Disconnect from EDDN (After receiving ZMQError)"
    puts "ZMQSocketException: #{e}"
    subscriber.disconnect(EDDN_RELAY)
    sleep(10)
  end
end
