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
        print(f"\n{data.get('message', 'A player joined.')}")
    elif message_type == "MOVE":
        print(f"\n{data.get('message', 'A move was made.')}")
        print_board(data.get("board"))
    elif message_type == "WIN":
        print(f"\n{data.get('message', 'Game over.')}")
        print_board(data.get("board"))
    elif message_type == "DRAW":
        print(f"\n{data.get('message', 'It is a draw.')}")
        print_board(data.get("board"))
    elif message_type == "ERROR":
        print(f"\n{data.get('message', 'An error occurred.')}")
    elif message_type == "QUIT":
        print(f"\n{data.get('message', 'A player quit the game.')}")
    elif message_type == "STATE":
        print("\nGame state updated.")
        print_board(data.get("board"))
    else:
        # Suppress unknown message errors for known message types
        print(f"Unhandled message type: {message_type}")
        return

def send_move(sock, position):
    try:
        message = json.dumps({"type": "move", "position": position})
        sock.send(message.encode('utf-8'))
    except Exception as e:
        print(f"Error sending move: {e}")

def print_board(board):
    if board:
        print("\nCurrent Board:")
        for i, row in enumerate(board):
            print(" | ".join(cell if cell != '#' else ' ' for cell in row))
            if i < len(board) - 1:  # Skip adding dashes after the last row
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
            user_input = input("\nEnter your move as row,col (or type 'quit' to exit): ")
            if user_input.lower() == 'quit':
                print("Exiting the game.")
                sock.close()
                break

            try:
                row, col = map(int, user_input.split(','))
                send_move(sock, [row, col])
            except ValueError:
                print("\nInvalid input. Please enter row and column as numbers separated by a comma.")

    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    main()
