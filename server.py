import socket
import threading
import logging

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Client handling
def handle_client(client_socket, client_address):
    logging.info(f"Client connected: {client_address}")
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break  # Connection shut
            logging.info(f"Received message from {client_address}: {message}")
            response = f"Echo: {message}"
            client_socket.send(response.encode('utf-8'))
    except Exception as e:
        logging.error(f"Error with client {client_address}: {e}")
    finally:
        client_socket.close()
        logging.info(f"Client disconnected: {client_address}")

# Starter process
def start_server(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    logging.info(f"Server listening on {host}:{port}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
