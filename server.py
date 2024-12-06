import socket
import threading
import logging
import json
import traceback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server_log.log"),  # Log to a file named 'server.log'
        logging.StreamHandler()            # Log to the console
    ]
)

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
    "RESET": "reset",
    "EXIT": "exit"
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
    # Notify the client of their assigned ID and role
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
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            try:
                data = json.loads(message)
                logging.info(f"Received message from {client_id}: {data}")
                message_type = data.get("type")
                if not message_type or message_type not in MESSAGE_TYPES.values():
                    raise ValueError(f"Invalid or missing message type: {data}")
                response = handle_message(data, client_id, player_number, player_symbol)
                if response:
                    broadcast(response)
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Error processing message from {client_id}: {e}")
    except Exception:
        logging.error(f"Error with client {client_id}: {traceback.format_exc()}")
    finally:
        client_socket.close()
        handle_disconnection(client_id)

def handle_disconnection(client_id):
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
                row, col = row - 1, col - 1
                if 0 <= row < 3 and 0 <= col < 3 and game_state["board"][row][col] == '#':
                    game_state["board"][row][col] = player_symbol
                    if check_winner(player_symbol):
                        game_state["winner"] = player_symbol
                        broadcast({
                            "type": "WIN",
                            "message": f"Player {player_number} ({player_symbol}) wins!",
                            "board": game_state["board"],
                            "whoseTurn": None
                        })
                        return
                    elif check_draw():
                        game_state["winner"] = "Draw"
                        broadcast({
                            "type": "DRAW",
                            "message": "It's a draw!",
                            "board": game_state["board"],
                            "whoseTurn": None
                        })
                        return
                    whoseTurn = 2 if whoseTurn == 1 else 1
                    return {
                        "type": "MOVE",
                        "message": f"Player {player_number} ({player_symbol}) moved to {position}.",
                        "board": game_state["board"],
                        "whoseTurn": whoseTurn
                    }
                else:
                    return {"type": "ERROR", "message": "Invalid move!", "board": game_state["board"], "whoseTurn": whoseTurn}
            except ValueError:
                return {"type": "ERROR", "message": "Invalid position format!", "board": game_state["board"], "whoseTurn": whoseTurn}
    elif message_type == MESSAGE_TYPES["RESET"]:
        reset_game()
        return {"type": "RESET", "message": "Game has been reset.", "board": game_state["board"], "whoseTurn": whoseTurn}
    elif message_type == MESSAGE_TYPES["CHAT"]:
        return {"type": "CHAT", "message": f"Player {player_number} ({player_symbol}) says: {data.get('message', '')}"}
    elif message_type == MESSAGE_TYPES["QUIT"]:
        handle_disconnection(client_id)
        return {"type": "QUIT", "message": f"Player {player_number} ({player_symbol}) has quit the game.", "board": game_state["board"], "whoseTurn": whoseTurn}
    return {"type": "ERROR", "message": "Unknown message type.", "board": game_state["board"], "whoseTurn": whoseTurn}


def reset_game():
    global game_state, whoseTurn
    game_state = {"board": [['#' for _ in range(3)] for _ in range(3)], "winner": None}
    whoseTurn = 1
    broadcast({"type": "RESET", "message": "Game has been reset.", "board": game_state["board"], "whoseTurn": whoseTurn})
    logging.info("Game reset successfully.")

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
