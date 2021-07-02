package com.eddn.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties
public class EdcmApiJavaApplication {

    public static void main(String[] args) {
        SpringApplication.run(EdcmApiJavaApplication.class, args);
    }

}
