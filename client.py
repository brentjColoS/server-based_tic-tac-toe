import socket
import threading
import json
import sys
import uuid

is_my_turn = False  # Track if it's this player's turn
client_id = None  # Unique ID for this client
player_id = None  # The role of this player ('X' or 'O')
game_state = None  # Track the current game state

def receive_messages(sock):
    global is_my_turn, game_state, player_id
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
    global is_my_turn, game_state, player_id
    message_type = data.get("type")

    if message_type == "JOIN":
        if data.get("player_id") == player_id:
            print(f"\n(You) Client {client_id} joined as {player_id}.")
        else:
            print(f"\nAnother player joined as {data.get('player_id')}.")
        game_state = data.get("board", [])
        print_board(game_state)
        if data.get("turn") == client_id:
            is_my_turn = True
    elif message_type == "MOVE":
        print(f"\n{data.get('message', 'A move was made.')}")
        game_state = data.get("board", [])
        print_board(game_state)
        is_my_turn = data.get("turn") == client_id
    elif message_type == "WIN":
        print(f"\n{data.get('message', 'Game over.')}")
        game_state = data.get("board", [])
        print_board(game_state)
        is_my_turn = False  # Game is over
    elif message_type == "DRAW":
        print(f"\n{data.get('message', 'It is a draw.')}")
        game_state = data.get("board", [])
        print_board(game_state)
        is_my_turn = False  # Game is over
    elif message_type == "ERROR":
        print(f"\n{data.get('message', 'An error occurred.')}")
    elif message_type == "CHAT":
        print(f"\n{data.get('message', '')}")
    elif message_type == "STATE":
        print("\nGame state updated.")
        game_state = data.get("board", [])
        print_board(game_state)
        is_my_turn = data.get("turn") == client_id
    else:
        print("\nUnknown message type received:", data)

def send_move(sock, position):
    try:
        message = json.dumps({"type": "move", "position": position})
        sock.send(message.encode('utf-8'))
    except Exception as e:
        print(f"Error sending move: {e}")

def send_chat(sock, message):
    try:
        chat_message = json.dumps({"type": "chat", "message": message})
        sock.send(chat_message.encode('utf-8'))
    except Exception as e:
        print(f"Error sending chat message: {e}")

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
    global is_my_turn, client_id, player_id, game_state
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
        join_message = json.dumps({"type": "JOIN", "client_id": client_id})
        sock.send(join_message.encode('utf-8'))

        threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

        while True:
            if is_my_turn is True:
                print_board(game_state)  # Display the board before asking for input
                user_input = input("\nEnter your move as row,col (or type 'chat:<message>' to chat): ")
                if user_input.lower() == 'quit':
                    print("Exiting the game.")
                    sock.close()
                    break
                elif user_input.lower().startswith("chat:"):
                    chat_message = user_input.split(":", 1)[1].strip()
                    send_chat(sock, chat_message)
                else:
                    try:
                        row, col = map(int, user_input.split(','))
                        send_move(sock, [row, col])
                        is_my_turn = False  # Set to False after making the move
                    except ValueError:
                        print("\nInvalid input. Please enter row and column as numbers separated by a comma.")
            else:
                print("\nWaiting for the other player's move...")  # Display once
                threading.Event().wait()

    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    main()
