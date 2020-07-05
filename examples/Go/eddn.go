package main

import (
	"bytes"
	"compress/zlib"
	"encoding/json"
	"fmt"
	"time"

	"gopkg.in/zeromq/goczmq.v4"
)

type EDDN struct {
	SchemaRef string          `json:"$schemaRef"`
	Header    EDDNHeader      `json:"header"`
	Message   json.RawMessage `json:"message"`
}
type EDDNHeader struct {
	UploaderID       string    `json:"uploaderID"`
	SoftwareName     string    `json:"softwareName"`
	SoftwareVersion  string    `json:"softwareVersion"`
	GatewayTimestamp time.Time `json:"gatewayTimestamp"`
}

func main() {
	channel := goczmq.NewSubChanneler("tcp://eddn.edcd.io:9500", "")
	defer channel.Destroy()

	run := true
	for run {
		select {
		case rawMessage, ok := <-channel.RecvChan:
			if !ok {
				run = false
				continue
			}

			message, err := decodeMessage(rawMessage[0])
			if err != nil {
				fmt.Println(err.Error())
				run = false
				continue
			}

			fmt.Println(message.SchemaRef, message.Header.SoftwareName)
		}
	}
}

func decodeMessage(rawMessage []byte) (*EDDN, error) {
	r, err := zlib.NewReader(bytes.NewReader(rawMessage))
	if err != nil {
		return nil, err
	}
	defer r.Close()

	var message EDDN
	err = json.NewDecoder(r).Decode(&message)
	if err != nil {
		return nil, err
	}

	return &message, nil
}
