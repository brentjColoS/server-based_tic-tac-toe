import socket
import threading
import logging
import json
from collections import defaultdict

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# List to keep track of connected clients and game state
clients = {}
player_turns = []
current_turn_index = 0
game_state = {
    "board": [],  # This will hold the state of the game board
    "turn": None,  # Current player's turn
}

# Message types
MESSAGE_TYPES = {
    "JOIN": "join",
    "MOVE": "move",
    "CHAT": "chat",
    "QUIT": "quit",
    "STATE": "state",
}

# Client handling
def handle_client(client_socket, client_address):
    logging.info(f"Client connected: {client_address}")
    clients[client_address] = client_socket

    # Assign unique player ID
    player_id = len(clients)  # Simple player ID based on order of connection
    player_turns.append(player_address)
    
    try:
        # Notify all clients about the new player
        broadcast({"type": "JOIN", "player_id": player_id, "address": str(client_address)})

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break  # Connection shut

            data = json.loads(message)
            logging.info(f"Received message from {client_address}: {data}")

            response = handle_message(data, client_address, player_id)
            if response:
                broadcast(response)

    except Exception as e:
        logging.error(f"Error with client {client_address}: {e}")
    finally:
        client_socket.close()
        del clients[client_address]
        player_turns.remove(client_address)
        broadcast({"type": "QUIT", "address": str(client_address)})

def handle_message(data, client_address, player_id):
    message_type = data.get("type")
    
    if message_type == MESSAGE_TYPES["JOIN"]:
        return {"type": "JOIN", "message": f"{client_address} has joined the game."}
    
    elif message_type == MESSAGE_TYPES["MOVE"]:
        if client_address == player_turns[current_turn_index]:  # Ensure it's the current player's turn
            # Update game state with the move
            position = data.get('position')
            game_state["board"].append({"player_id": player_id, "position": position})
            # Rotate turn
            current_turn_index = (current_turn_index + 1) % len(player_turns)
            game_state["turn"] = player_turns[current_turn_index]
            return {"type": "MOVE", "message": f"{client_address} moved to {position}."}

    elif message_type == MESSAGE_TYPES["CHAT"]:
        return {"type": "CHAT", "message": f"{client_address}: {data.get('message')}"}

    elif message_type == MESSAGE_TYPES["QUIT"]:
        return {"type": "QUIT", "message": f"{client_address} has left the game."}
    
    return {"type": "ERROR", "message": "Unknown message type."}

def broadcast(message):
    for client_address, client_socket in clients.items():
        client_socket.send(json.dumps(message).encode('utf-8'))

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
