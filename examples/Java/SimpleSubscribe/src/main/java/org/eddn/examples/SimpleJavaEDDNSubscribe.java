package org.eddn.examples;

import java.util.zip.Inflater;

import org.zeromq.SocketType;
import org.zeromq.ZMQ;
import org.zeromq.ZContext;

public class SimpleJavaEDDNSubscribe {
    private static final int MAX_MESSAGE_SIZE_KB = 200;
    private static final String EDDN_SERVER = "tcp://eddn.edcd.io:9500";
    private static ZContext context;

    public static void main(String[] args) throws Exception {
        context = new ZContext();    
        String jsonMessage = getOneMessage();
        System.out.println(jsonMessage);
        context.close();
    }

    private static String getOneMessage() throws Exception {
        byte[] deflatedMessage = receiveOneDeflatedMessage();
        return inflateMessage(deflatedMessage);
    }

    private static byte[] receiveOneDeflatedMessage() {
        ZMQ.Socket socket = getEDDNSubscriptionSocket();    
        byte[] deflatedMessage = socket.recv();
        return deflatedMessage;
    }

    private static ZMQ.Socket getEDDNSubscriptionSocket() {
        ZMQ.Socket socket = context.createSocket(SocketType.SUB);
        socket.connect(EDDN_SERVER);
        
        // need to subscribe to the empty topic to receive anything
        socket.subscribe("");
        return socket;
    }

    public static String inflateMessage(byte[] bytes) throws Exception {

        Inflater decompresser = new Inflater();
        decompresser.setInput(bytes);
        byte[] result = new byte[MAX_MESSAGE_SIZE_KB * 1024];
        int resultLength = decompresser.inflate(result);
        decompresser.end();

        // Decode the bytes into a String
        String outputString = new String(result, 0, resultLength, "UTF-8");
        return outputString;
    }
}