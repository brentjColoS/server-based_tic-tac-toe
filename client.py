import socket
import threading
import json
import sys
import uuid

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if not message:
                print("Disconnected from the server.")
                break
            data = json.loads(message)
            handle_server_message(data)
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def handle_server_message(data):
    message_type = data.get("type")

    if message_type == "JOIN":
        print(data.get("message", "A player joined."))
    elif message_type == "MOVE":
        print(data.get("message", "A move was made."))
        print_board(data.get("board"))
    elif message_type == "WIN":
        print(data.get("message", "Game over."))
        print_board(data.get("board"))
    elif message_type == "DRAW":
        print(data.get("message", "It's a draw."))
        print_board(data.get("board"))
    elif message_type == "ERROR":
        print(data.get("message", "An error occurred."))
    elif message_type == "QUIT":
        print(data.get("message", "A player quit the game."))
    elif message_type == "STATE":
        print("Game state updated.")
        print_board(data.get("board"))
    else:
        print("Unknown message type received.")

def send_move(sock, position):
    try:
        message = json.dumps({"type": "move", "position": position})
        sock.send(message.encode('utf-8'))
    except Exception as e:
        print(f"Error sending move: {e}")

def print_board(board):
    if board:
        print("\nCurrent Board:")
        for row in board:
            print(" | ".join(cell if cell != '#' else ' ' for cell in row))
            print("-" * 11)
    else:
        print("No board to display.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Tic-Tac-Toe client')
    parser.add_argument('-H', '--host', type=str, required=True, help='Server host')
    parser.add_argument('-p', '--port', type=int, required=True, help='Server port')
    args = parser.parse_args()

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((args.host, args.port))
        print("Connected to the server.")

        # Generate a unique ID for this client
        client_id = str(uuid.uuid4())
        message = json.dumps({"type": "JOIN", "client_id": client_id})
        sock.send(message.encode('utf-8'))

        threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

        while True:
            user_input = input("Enter your move as row,col (or type 'quit' to exit): ")
            if user_input.lower() == 'quit':
                print("Exiting the game.")
                sock.close()
                break

            try:
                row, col = map(int, user_input.split(','))
                send_move(sock, [row, col])
            except ValueError:
                print("Invalid input. Please enter row and column as numbers separated by a comma.")

    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    main()
