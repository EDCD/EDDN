using NetMQ.Sockets;
using NetMQ;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Ionic.Zlib;

namespace ConsoleApp
{
    class Program
    {
        static void Main(string[] args)
        {
            var utf8 = new UTF8Encoding();

            using (var client = new SubscriberSocket())
            {
                client.Options.ReceiveHighWatermark = 1000;
                client.Connect("tcp://eddn.edcd.io:9500");
                client.SubscribeToAnyTopic();
                while (true)
                {
                    var bytes = client.ReceiveFrameBytes();
                    var uncompressed = ZlibStream.UncompressBuffer(bytes);

                    var result = utf8.GetString(uncompressed);

                    Console.WriteLine(result);
                }
            }
        }
    }
}
