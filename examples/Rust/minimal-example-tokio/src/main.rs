use flate2::bufread::ZlibDecoder;
use serde::Deserialize;
use std::io::Read;
use zeromq::Socket;
use zeromq::SocketRecv;

#[derive(Deserialize, Debug)]
struct EDDN {
    header: EDDNHeader,
    message: Event,
}

#[derive(Deserialize, Debug)]
struct EDDNHeader {
    #[serde(rename = "softwareName")]
    software_name: String,
    #[serde(rename = "softwareVersion")]
    software_version: String,
}

#[derive(Deserialize, Debug)]
struct Event {
    event: Option<String>,
}

#[tokio::main]
async fn main() {
    let mut socket = zeromq::SubSocket::new();
    socket
        .connect("tcp://eddn.edcd.io:9500")
        .await
        .expect("Failed to connect to EDDN");
    println!("Connected to eddn");
    socket
        .subscribe("")
        .await
        .expect("Failed to subscribe to EDDN");
    println!("Subscribed to eddn");

    loop {
        match socket.recv().await {
            Err(err) => {
                println!("Receive Error: {}", err.to_string())
            }
            Ok(recv) => {
                let data_compressed = recv.get(0).unwrap().to_vec();
                let mut decoder = ZlibDecoder::new(&data_compressed[..]);
                let mut data = String::new();
                if let Err(err) = decoder.read_to_string(&mut data) {
                    println!("Failed decompression of zlib payload: {}", err);
                    continue;
                }

                let message: EDDN = match serde_json::from_str(&data) {
                    Ok(x) => x,
                    Err(err) => {
                        println!("Failed parsing payload: {}", err);
                        continue;
                    }
                };

                match message.message.event {
                    Some(event_type) => println!(
                        "RX an Event of type {} from Software {} Version {}",
                        event_type, message.header.software_name, message.header.software_version
                    ),
                    None => println!(
                        "RX an Event without event type from Software {} Version {}",
                        message.header.software_name, message.header.software_version
                    ),
                }
            }
        }
    }
}
