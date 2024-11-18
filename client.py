import socket
import logging
import sys
import json
import threading

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable for player ID
player_id = None

def handle_server_messages(client_socket):
    """Handle incoming messages from the server."""
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break
        data = json.loads(message)
        logging.info(f"Received from server: {data}")
        if data['type'] == 'MOVE':
            # Render the move on the game board
            render_game_state(data)
        elif data['type'] == 'JOIN':
            logging.info(data['message'])  # This will now log correctly
        elif data['type'] == 'CHAT':
            logging.info(data['message'])
        elif data['type'] == 'QUIT':
            logging.info(data['message'])
        elif data['type'] == 'STATE':
            # Update local game state based on server state
            update_game_state(data)

def render_game_state(data):
    """Placeholder for rendering game state on the client."""
    # Here you can implement your rendering logic
    logging.info(f"Rendering move: {data}")

def update_game_state(data):
    """Update the local game state."""
    # Here you can implement your game state update logic
    logging.info(f"Updating game state with: {data}")

# Client starter
def start_client(server_host, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_host, server_port))
        logging.info(f"Connected to server at {server_host}:{server_port}")

        # Start a thread to handle incoming messages
        threading.Thread(target=handle_server_messages, args=(client_socket,), daemon=True).start()

        # Send join message
        send_message(client_socket, {"type": "JOIN"})  # Change this to match the server expectation

        while True:
            message = input("Enter a message to send (or 'exit' to quit): ")
            if message.lower() == 'exit':
                send_message(client_socket, {"type": "QUIT"})
                break
            
            send_message(client_socket, {"type": "CHAT", "message": message})

    except (ConnectionRefusedError, TimeoutError) as e:
        logging.error(f"Connection error: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        client_socket.close()
        logging.info("Disconnected from server.")

def send_message(client_socket, message):
    client_socket.send(json.dumps(message).encode('utf-8'))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_host> <server_port>")
        sys.exit(1)

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    start_client(server_host, server_port)
