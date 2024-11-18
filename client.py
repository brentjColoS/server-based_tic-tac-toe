import socket
import logging
import sys
import json
import threading
import argparse

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable for player ID
player_id = None
game_state = {
    "board": [[' ' for _ in range(3)] for _ in range(3)],
    "turn": None,
    "winner": None
}

# Handle incoming server messages
def handle_server_messages(client_socket):
    """Handle incoming messages from the server."""
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break
        data = json.loads(message)
        logging.info(f"Received from server: {data}")
        if data['type'] == 'MOVE':
            render_game_state(data)
        elif data['type'] == 'WIN':
            logging.info(data['message'])
            break
        elif data['type'] == 'DRAW':
            logging.info(data['message'])
            break
        elif data['type'] == 'JOIN':
            logging.info(f"Welcome {data['address']}! You are playing as {data['player_id']}.")

# Display the game board
def render_game_state(data):
    """Placeholder for rendering game state on the client."""
    game_state["board"] = data.get('board', game_state["board"])
    logging.info("\n".join(["|".join(row) for row in game_state["board"]]))
    logging.info(f"Current turn: {data.get('turn')}")
    if game_state["winner"]:
        logging.info(f"Game over. Winner: {game_state['winner']}")

# Send a move to the server
def send_move(client_socket):
    """Get user input for the move and send it to the server."""
    while True:
        try:
            move = input("Enter your move (row col): ").split()
            row, col = int(move[0]), int(move[1])
            if game_state["board"][row][col] != ' ':
                logging.warning("That space is already taken. Try again.")
                continue
            send_message(client_socket, {"type": "MOVE", "position": [row, col]})
            break
        except ValueError:
            logging.warning("Invalid input. Enter row and column as numbers (e.g., 1 2).")

# Send messages to the server
def send_message(client_socket, message):
    client_socket.send(json.dumps(message).encode('utf-8'))

# Client starter
def start_client(server_host, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_host, server_port))
        logging.info(f"Connected to server at {server_host}:{server_port}")

        # Start a thread to handle incoming messages
        threading.Thread(target=handle_server_messages, args=(client_socket,), daemon=True).start()

        # Send join message
        send_message(client_socket, {"type": "join"})

        # Wait for the game to start and make moves
        while True:
            send_move(client_socket)

    except (ConnectionRefusedError, TimeoutError) as e:
        logging.error(f"Connection error: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        client_socket.close()
        logging.info("Disconnected from server.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a Tic-Tac-Toe client')
    parser.add_argument('-i', '--host', required=True, help='Server IP/DNS')
    parser.add_argument('-p', '--port', type=int, required=True, help='Server port')
    args = parser.parse_args()

    start_client(args.host, args.port)
