# server-based_tic-tac-toe
Repository for CS457 Semester-long project: Tic Tac Toe based on server-client connections.

## How to Play:
1. **Start the server:** Run the `server.py` script in the terminal.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals.
3. **Play the game:** Players take turns entering their moves. The first player to get three in a row wins!

## Technologies Used:
* Python
* Sockets

## Game Message Protocol

### Overview
This document defines the structure and format of messages exchanged between the server and clients in the game.

### Message Structure
Messages are formatted as JSON objects with the following fields:
- **type**: The type of the message (e.g., "join", "move", "chat", "quit").
- **message** (optional): Additional information depending on the message type (e.g., chat message or move position).

### Message Types
1. **Join**
   - **Type**: `join`
   - **Example**: `{"type": "join"}`
   - **Response**: A notification message indicating that the client has joined.

2. **Move**
   - **Type**: `move`
   - **Data Field**: `position` (the new position the player has moved to)
   - **Example**: `{"type": "move", "position": {"x": 1, "y": 2}}`
   - **Response**: A notification message indicating the player's new position.

3. **Chat**
   - **Type**: `chat`
   - **Data Field**: `message` (the message to be sent)
   - **Example**: `{"type": "chat", "message": "Hello!"}`
   - **Response**: A message echoing the chat message with the client's address.

4. **Quit**
   - **Type**: `quit`
   - **Example**: `{"type": "quit"}`
   - **Response**: A notification message indicating that the client has left the game.

### Connection Management
- The server maintains a list of connected clients and their associated game states.
- Other clients are notified when a player joins or leaves the game.

## Additional Resources:
* [Python Official Website](https://www.python.org)
* [GeeksforGeeks: Socket Programming in Python](https://www.geeksforgeeks.org/socket-programming-python/)
