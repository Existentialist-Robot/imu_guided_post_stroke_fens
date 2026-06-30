import socket
from threading import Thread
from time import sleep
import sys

exit = False

def rx_thread(server_address, server_port):
    global exit

    rx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rx_socket.bind((server_address, server_port))
    rx_socket.setblocking(0)

    print(f"RX: listening on UDP port {server_port}")

    while not exit:
        try:
            data, addr = rx_socket.recvfrom(1024)
            rx_socket.sendto(str(data).encode(), addr)
        except socket.error:
            pass
        sleep(0.1)


def main(args):
    global exit

    server_address = '0.0.0.0'
    server_port = 3333

    rx_handle = Thread(target=rx_thread, args=(server_address, server_port,))
    rx_handle.start()
    sleep(0.1)

    tx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tx_socket.setblocking(0)

    print(f"TX: sending to {server_address}:{server_port}")
    print("Type anything and press Enter to transmit. Ctrl+C to exit.")

    while True:
        try:
            tx_char = input("TX: ")
            tx_socket.sendto(tx_char.encode(), (server_address, server_port))
            sleep(0.2)
            data, addr = tx_socket.recvfrom(1024)
            print(f"RX: {data}")
        except socket.error:
            pass
        except KeyboardInterrupt:
            exit = True
            print("Exiting...")
            break
        sleep(0.1)

    rx_handle.join()


if __name__ == "__main__":
    main(sys.argv[1:])
