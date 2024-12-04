import socket
import threading
import logging
import json
import sys
import traceback

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

clients = {}  # Maps client_id to socket
player_roles = {}  # Maps client_id to player number (1 or 2)
game_state = {
    "board": [['#' for _ in range(3)] for _ in range(3)],
    "winner": None
}
whoseTurn = 1  # Global variable to track whose turn it is (1 or 2)

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
    global whoseTurn

    logging.info(f"Client connected: {client_address}")

    if len(player_roles) >= 2:
        client_socket.send(json.dumps({
            "type": "ERROR",
            "message": "Game is full. Only two players allowed."
        }).encode('utf-8'))
        client_socket.close()
        return

    player_number = 1 if len(player_roles) == 0 else 2
    client_id = f"player_{player_number}"
    clients[client_id] = client_socket
    player_roles[client_id] = player_number
    player_symbol = 'X' if player_number == 1 else 'O'

    # Notify the client of their assigned ID and player role
    client_socket.send(json.dumps({
        "type": "ASSIGN_ID",
        "client_id": client_id,
        "player_symbol": player_symbol,
        "board": game_state["board"],
        "whoseTurn": whoseTurn
    }).encode('utf-8'))

    broadcast({
        "type": "JOIN",
        "message": f"Player {player_number} joined as {player_symbol}.",
        "board": game_state["board"],
        "whoseTurn": whoseTurn
    })

    # Allow Player 1 to make the first move immediately
    if player_number == 1:
        client_socket.send(json.dumps({
            "type": "MOVE",
            "message": "You are Player 1 (X). Make your move.",
            "board": game_state["board"],
            "whoseTurn": whoseTurn
        }).encode('utf-8'))

    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            try:
                data = json.loads(message)
                logging.info(f"Received message from {client_id}: {data}")

                response = handle_message(data, client_id, player_number, player_symbol)
                if response:
                    broadcast(response)
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON from {client_id}: {message}")
    except Exception:
        logging.error(f"Error with client {client_id}: {traceback.format_exc()}")
    finally:
        client_socket.close()
        handle_disconnection(client_id)

def handle_disconnection(client_id):
    global whoseTurn

    if client_id in clients:
        del clients[client_id]
    if client_id in player_roles:
        del player_roles[client_id]

    broadcast({
        "type": "QUIT",
        "message": f"{client_id} has left the game.",
        "board": game_state["board"],
        "whoseTurn": whoseTurn
    })

def handle_message(data, client_id, player_number, player_symbol):
    global whoseTurn
    message_type = data.get("type")

    if message_type == MESSAGE_TYPES["MOVE"]:
        if whoseTurn != player_number:
            return {
                "type": "ERROR",
                "message": "It's not your turn!",
                "board": game_state["board"],
                "whoseTurn": whoseTurn
            }

        position = data.get('position')
        if position and isinstance(position, list) and len(position) == 2:
            try:
                row, col = map(int, position)
                row, col = row - 1, col - 1  # Convert 1-based to 0-based indexing
                if 0 <= row < 3 and 0 <= col < 3 and game_state["board"][row][col] == '#':
                    # Update the board
                    game_state["board"][row][col] = player_symbol

                    # Check for a winner or a draw
                    if check_winner(player_symbol):
                        game_state["winner"] = player_symbol
                        return {
                            "type": "WIN",
                            "message": f"Player {player_number} ({player_symbol}) wins!",
                            "board": game_state["board"],
                            "whoseTurn": None
                        }
                    elif check_draw():
                        game_state["winner"] = "Draw"
                        return {
                            "type": "DRAW",
                            "message": "It's a draw!",
                            "board": game_state["board"],
                            "whoseTurn": None
                        }

                    # Switch turn
                    whoseTurn = 2 if whoseTurn == 1 else 1
                    return {
                        "type": "MOVE",
                        "message": f"Player {player_number} ({player_symbol}) moved to {position}.",
                        "board": game_state["board"],
                        "whoseTurn": whoseTurn
                    }
                else:
                    return {
                        "type": "ERROR",
                        "message": "Invalid move!",
                        "board": game_state["board"],
                        "whoseTurn": whoseTurn
                    }
            except ValueError:
                return {
                    "type": "ERROR",
                    "message": "Invalid position format!",
                    "board": game_state["board"],
                    "whoseTurn": whoseTurn
                }
    elif message_type == MESSAGE_TYPES["CHAT"]:
        return {
            "type": "CHAT",
            "message": f"Player {player_number} ({player_symbol}) says: {data.get('message', '')}"
        }

    return {
        "type": "ERROR",
        "message": "Unknown message type.",
        "board": game_state["board"],
        "whoseTurn": whoseTurn
    }

def check_winner(symbol):
    for i in range(3):
        if all(game_state["board"][i][j] == symbol for j in range(3)) or \
           all(game_state["board"][j][i] == symbol for j in range(3)):
            return True
    if game_state["board"][0][0] == symbol and game_state["board"][1][1] == symbol and game_state["board"][2][2] == symbol:
        return True
    if game_state["board"][0][2] == symbol and game_state["board"][1][1] == symbol and game_state["board"][2][0] == symbol:
        return True
    return False

def check_draw():
    return all(game_state["board"][i][j] != '#' for i in range(3) for j in range(3))

def broadcast(message):
    for client_id, client_socket in clients.items():
        try:
            client_socket.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            logging.error(f"Failed to send message to {client_id}: {e}")

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
