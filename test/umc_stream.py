import socket
import json

def start_udp_server():
    server_address = ('', 5432)

    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind to the server address
    sock.bind(server_address)

    while True:
        # Receive data from the client
        data, client_address = sock.recvfrom(3000)

        print("----")
        print(data)
        print("----")

        # Get data as a json object
        json_data = json.loads(data.decode('utf-8'), strict=False)
        # iris = json_data['camera']['optic']['lens']['lensState']["lensIris"]
        # print(f"Iris: {iris}")

        focal_length = json_data['camera']['optic']['lens']['lensState']["lensFocalLength"]
        print(f"Focal Length: {focal_length}")


if __name__ == "__main__":
    # Start the UDP server
    start_udp_server()
