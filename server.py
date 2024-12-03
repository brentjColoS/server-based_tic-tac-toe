import socket
import threading
import logging
import json
import sys
import traceback
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

clients = {}
player_turns = []
current_turn_index = 0
game_state = {
    "board": [['#' for _ in range(3)] for _ in range(3)],
    "turn": None,
    "winner": None
}

MESSAGE_TYPES = {
    "JOIN": "join",
    "MOVE": "move",
    "CHAT": "chat",
    "QUIT": "quit",
    "STATE": "state",
    "WIN": "win",
    "DRAW": "draw",
}

def handle_client(client_socket, client_address):
    logging.info(f"Client connected: {client_address}")

    unique_id = str(uuid.uuid4())
    clients[unique_id] = client_socket

    player_id = 'X' if len(player_turns) % 2 == 0 else 'O'
    player_turns.append(unique_id)

    if len(player_turns) == 1:
        game_state["turn"] = unique_id  # Set the first player as the starting turn

    try:
        broadcast({
            "type": "JOIN",
            "message": f"Client {unique_id} joined as {player_id}.",
            "turn": game_state["turn"]
        })

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            try:
                data = json.loads(message)
                logging.info(f"Received message from {unique_id}: {data}")

                response = handle_message(data, unique_id, player_id)
                if response:
                    broadcast(response)
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON from {unique_id}: {message}")
    except Exception:
        logging.error(f"Error with client {unique_id}: {traceback.format_exc()}")
    finally:
        client_socket.close()
        handle_disconnection(unique_id)

def handle_disconnection(unique_id):
    global current_turn_index

    if unique_id in clients:
        del clients[unique_id]
    if unique_id in player_turns:
        player_turns.remove(unique_id)

        if len(player_turns) > 0:
            current_turn_index %= len(player_turns)
            game_state["turn"] = player_turns[current_turn_index]
        else:
            game_state["turn"] = None

    broadcast({"type": "QUIT", "message": f"Client {unique_id} has left the game.", "turn": game_state["turn"]})

def handle_message(data, unique_id, player_id):
    global current_turn_index
    message_type = data.get("type")

    if message_type == MESSAGE_TYPES["JOIN"]:
        return {"type": "JOIN", "message": f"Client {unique_id} has joined the game.", "turn": game_state["turn"]}

    elif message_type == MESSAGE_TYPES["MOVE"]:
        if unique_id == game_state["turn"]:
            position = data.get('position')
            if position and isinstance(position, list) and len(position) == 2:
                try:
                    row, col = map(int, position)
                    row, col = row - 1, col - 1  # Convert 1-based to 0-based indexing
                    if 0 <= row < 3 and 0 <= col < 3 and game_state["board"][row][col] == '#':
                        game_state["board"][row][col] = player_id

                        if check_winner(player_id):
                            game_state["winner"] = player_id
                            return {
                                "type": "WIN",
                                "board": game_state["board"],
                                "message": f"{player_id} wins!",
                                "turn": None
                            }
                        elif check_draw():
                            game_state["winner"] = "Draw"
                            return {
                                "type": "DRAW",
                                "board": game_state["board"],
                                "message": "It's a draw!",
                                "turn": None
                            }

                        # Update turn
                        current_turn_index = (current_turn_index + 1) % len(player_turns)
                        game_state["turn"] = player_turns[current_turn_index]
                        return {
                            "type": "MOVE",
                            "board": game_state["board"],
                            "turn": game_state["turn"],
                            "message": f"{player_id} moved to {position}."
                        }
                    else:
                        return {"type": "ERROR", "message": "Invalid move!", "turn": game_state["turn"]}
                except ValueError:
                    return {"type": "ERROR", "message": "Invalid position format!", "turn": game_state["turn"]}
        else:
            return {"type": "ERROR", "message": "It's not your turn!", "turn": game_state["turn"]}

    elif message_type == MESSAGE_TYPES["CHAT"]:
        return {"type": "CHAT", "message": f"{player_id} says: {data.get('message', '')}"}

    elif message_type == MESSAGE_TYPES["QUIT"]:
        return {"type": "QUIT", "message": f"Client {unique_id} has left the game.", "turn": game_state["turn"]}

    return {"type": "ERROR", "message": "Unknown message type.", "turn": game_state["turn"]}

def check_winner(player_id):
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
    return all(game_state["board"][i][j] != '#' for i in range(3) for j in range(3))

def broadcast(message):
    for unique_id, client_socket in clients.items():
        try:
            client_socket.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            logging.error(f"Failed to send message to {unique_id}: {e}")

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
