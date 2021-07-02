package com.eddn.example.core.zeromq;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.annotation.ServiceActivator;
import org.springframework.integration.config.EnableIntegration;
import org.springframework.integration.zeromq.channel.ZeroMqChannel;
import org.springframework.messaging.MessageHandler;
import org.zeromq.ZContext;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.zip.DataFormatException;
import java.util.zip.Inflater;

@Configuration
@EnableIntegration
public class ZeromqConfig {

    @Bean
    public ZContext zContext() {
        return new ZContext();
    }

    @Bean(name = "zeroMqChannel")
    ZeroMqChannel zeroMqPubSubChannel(ZContext context) {
        ZeroMqChannel channel = new ZeroMqChannel(context, true);
        channel.setConnectUrl("tcp://eddn.edcd.io:9500:9500");
        return channel;
    }


    @Bean
    @ServiceActivator(inputChannel = "zeroMqChannel")
    public MessageHandler subscribe() {

        return message -> {
            byte[] output = new byte[256 * 1024];
            byte[] payload = (byte[]) message.getPayload();
            Inflater inflater = new Inflater();
            inflater.setInput(payload);
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream(payload.length);
            try {
                int outputLength = inflater.inflate(output);
                String outputString = new String(output, 0, outputLength, StandardCharsets.UTF_8);
                System.out.println(outputString);
            } catch (DataFormatException e) {
                e.printStackTrace();
            }
        };
    }


}
