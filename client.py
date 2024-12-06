import socket
import threading
import json
import sys

is_my_turn = False  # Track if it's this player's turn
client_id = None  # Unique ID assigned by the server
player_id = None  # The role of this player ('X' or 'O')
game_state = None  # Track the current game state

def receive_messages(sock):
    global is_my_turn, game_state, player_id, client_id
    buffer = ""  # Buffer to store partial data
    while True:
        try:
            # Receive data from the socket
            data = sock.recv(1024).decode('utf-8')
            if not data:
                print("Disconnected from the server.")
                break
            buffer += data  # Append received data to buffer

            # Process complete JSON objects in the buffer
            while True:
                try:
                    # Try to parse a JSON object
                    message, idx = json.JSONDecoder().raw_decode(buffer)
                    buffer = buffer[idx:].lstrip()  # Remove the processed message from the buffer
                    handle_server_message(message, sock)
                except json.JSONDecodeError:
                    # Incomplete JSON object, wait for more data
                    break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break


def handle_server_message(data, sock):
    global is_my_turn, game_state, player_id, client_id
    message_type = data.get("type")

    # Map whoseTurn (1 or 2) to player symbols ('X' or 'O')
    turn_map = {1: 'X', 2: 'O'}

    if message_type == "ASSIGN_ID":
        client_id = data.get("client_id")
        player_id = data.get("player_symbol")
        print(f"\nAssigned ID: {client_id}, playing as {player_id}.")
        game_state = data.get("board", [])
        if turn_map.get(data.get("whoseTurn")) == player_id:
            is_my_turn = True
            prompt_for_move(sock)  # Prompt for move immediately if it's this player's turn
    elif message_type == "JOIN":
        if data.get("client_id") != client_id:  # Ignore self-join messages
            print(f"\n{data.get('message')}")
    elif message_type == "MOVE":
        print(f"\n{data.get('message', 'A move was made.')}")
        # Update the game board for all clients
        game_state = data.get("board", [])
        # Only the client who made the move sees the board print immediately
        if turn_map.get(data.get("whoseTurn")) != player_id:
            print_board(game_state)
        is_my_turn = turn_map.get(data.get("whoseTurn")) == player_id
        if is_my_turn:
            prompt_for_move(sock)
        else:
            print("\nWaiting for the other player's move...")
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
        if is_my_turn:
            prompt_for_move(sock)  # Re-prompt on error
    elif message_type == "CHAT":
        print(f"\n{data.get('message', '')}")
    elif message_type == "STATE":
        print("\nGame state updated.")
        game_state = data.get("board", [])
        print_board(game_state)
        is_my_turn = turn_map.get(data.get("whoseTurn")) == player_id
    else:
        print("\nUnknown message type received:", data)



def prompt_for_move(sock):
    global is_my_turn
    if is_my_turn:
        print_board(game_state)  # Display the board before asking for input
        user_input = input("\nEnter your move as row,col (type 'chat:<message>' to chat | type 'quit' to exit): ")
        if user_input.lower() == 'quit':
            print("Exiting the game.")
            sock.close()
            sys.exit()
        elif user_input.lower().startswith("chat:"):
            chat_message = user_input.split(":", 1)[1].strip()
            send_chat(sock, chat_message)
            print("\nChat sent.")  # Optional message to confirm the chat was sent
            prompt_for_move(sock)  # Re-prompt for input after chat
        else:
            try:
                row, col = map(int, user_input.split(','))
                if 1 <= row <=3 and 1<= col <=3:
                    send_move(sock, [row, col])
                    is_my_turn = False  # Set to False after making the move
                else:
                    print("\nInvalid input. Please enter a row and column within range 1-3.")
                    prompt_for_move(sock)
            except ValueError:
                print("\nInvalid input. Please enter row and column as numbers separated by a comma.")
                prompt_for_move(sock)  # Re-prompt on invalid input

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

        threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

        while True:
            threading.Event().wait(1)  # Allow background thread to process incoming messages

    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    main()
