import socket
import threading
import logging
import json
import sys

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Game state and player tracking
clients = {}
player_turns = []
current_turn_index = 0
game_state = {
    "board": [[' ' for _ in range(3)] for _ in range(3)],  # 3x3 board
    "turn": None,  # Current player's turn
    "winner": None  # None if no winner, 'X' or 'O' if there's a winner
}

# Message types
MESSAGE_TYPES = {
    "JOIN": "join",
    "MOVE": "move",
    "CHAT": "chat",
    "QUIT": "quit",
    "STATE": "state",
    "WIN": "win",
    "DRAW": "draw",
}

# Client handling
def handle_client(client_socket, client_address):
    logging.info(f"Client connected: {client_address}")
    clients[client_address] = client_socket

    # Assign unique player ID (X or O)
    player_id = 'X' if len(clients) % 2 == 0 else 'O'
    player_turns.append(client_address)

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
            position = data.get('position')
            row, col = position
            # Validate move
            if game_state["board"][row][col] == ' ':
                game_state["board"][row][col] = player_id
                game_state["turn"] = player_turns[(current_turn_index + 1) % len(player_turns)]
                # Check for win or draw
                if check_winner(player_id):
                    game_state["winner"] = player_id
                    return {"type": "WIN", "message": f"{client_address} ({player_id}) wins!"}
                if check_draw():
                    game_state["winner"] = "Draw"
                    return {"type": "DRAW", "message": "It's a draw!"}
                # Rotate turn
                global current_turn_index
                current_turn_index = (current_turn_index + 1) % len(player_turns)
                return {"type": "MOVE", "message": f"{client_address} moved to {position}."}
            else:
                return {"type": "ERROR", "message": "Invalid move!"}
        else:
            return {"type": "ERROR", "message": "It's not your turn!"}

    elif message_type == MESSAGE_TYPES["CHAT"]:
        return {"type": "CHAT", "message": f"{client_address}: {data.get('message')}"}

    elif message_type == MESSAGE_TYPES["QUIT"]:
        return {"type": "QUIT", "message": f"{client_address} has left the game."}

    return {"type": "ERROR", "message": "Unknown message type."}

def check_winner(player_id):
    # Check rows, columns, and diagonals for a winner
    for i in range(3):
        if all(game_state["board"][i][j] == player_id for j in range(3)) or \
           all(game_state["board"][j][i] == player_id for j in range(3)):
            return True
    if game_state["board"][0][0] == player_id and game_state["board"][1][1] == player_id and game_state["board"][2][2] == player_id:
        return True
    if game_state["board"][0][2] == player_id and game_state["board"][1][1] == player_id and game_state["board"][2][0] == player_id:
        return True
    return False

def check_draw():
    # Check if the board is full and there’s no winner
    return all(game_state["board"][i][j] != ' ' for i in range(3) for j in range(3))

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
    import argparse
    parser = argparse.ArgumentParser(description='Start a Tic-Tac-Toe server')
    parser.add_argument('-p', '--port', type=int, required=True, help='Port to listen on')
    args = parser.parse_args()
    start_server(port=args.port)
