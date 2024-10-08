import socket
import logging
import sys

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Client starter
def start_client(server_host, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_host, server_port))
        logging.info(f"Connected to server at {server_host}:{server_port}")

        while True:
            message = input("Enter a message to send (or 'exit' to quit): ")
            if message.lower() == 'exit':
                break
            client_socket.send(message.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            logging.info(f"Received from server: {response}")

    except (ConnectionRefusedError, TimeoutError) as e:
        logging.error(f"Connection error: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        client_socket.close()
        logging.info("Disconnected from server.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_host> <server_port>")
        sys.exit(1)

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    start_client(server_host, server_port)
