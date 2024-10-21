import socket
import threading
import logging
import json

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# List to keep track of connected clients
clients = {}

# Message types
MESSAGE_TYPES = {
    "JOIN": "join",
    "MOVE": "move",
    "CHAT": "chat",
    "QUIT": "quit"
}

# Client handling
def handle_client(client_socket, client_address):
    logging.info(f"Client connected: {client_address}")
    clients[client_address] = client_socket
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break  # Connection shut

            data = json.loads(message)
            logging.info(f"Received message from {client_address}: {data}")

            response = handle_message(data, client_address)
            if response:
                client_socket.send(json.dumps(response).encode('utf-8'))

    except Exception as e:
        logging.error(f"Error with client {client_address}: {e}")
    finally:
        client_socket.close()
        del clients[client_address]
        logging.info(f"Client disconnected: {client_address}")

def handle_message(data, client_address):
    message_type = data.get("type")
    if message_type == MESSAGE_TYPES["JOIN"]:
        return {"type": "JOIN", "message": f"{client_address} has joined the game."}
    elif message_type == MESSAGE_TYPES["MOVE"]:
        return {"type": "MOVE", "message": f"{client_address} moved to {data.get('position')}."}
    elif message_type == MESSAGE_TYPES["CHAT"]:
        return {"type": "CHAT", "message": f"{client_address}: {data.get('message')}"}
    elif message_type == MESSAGE_TYPES["QUIT"]:
        return {"type": "QUIT", "message": f"{client_address} has left the game."}
    else:
        return {"type": "ERROR", "message": "Unknown message type."}

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
