# server-based_tic-tac-toe
Repository for CS457 Semester-long project: Tic Tac Toe based on server-client connections.

## How to Play:
1. **Start the server:** Run the `server.py` script in the terminal.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals.
3. **Join the game:** Each client sends a join message to the server upon connection.
4. **Play the game:** Players take turns entering their moves. The first player to get three in a row wins!
5. **Chat:** Players can communicate with each other via chat messages.

## Technologies Used:
* Python
* Sockets

## Game Message Protocol

### Overview
This document defines the structure and format of messages exchanged between the server and clients in the game.

### Message Structure
Messages are formatted as JSON objects with the following fields:
- **type**: The type of the message (e.g., "join", "move", "chat", "quit", "state").
- **message** (optional): Additional information depending on the message type (e.g., chat message, move position, or game state).

### Message Types
1. **Join**
   - **Type**: `join`
   - **Example**: `{"type": "join"}`
   - **Response**: A notification message indicating that the client has joined.

2. **Move**
   - **Type**: `move`
   - **Data Field**: `position` (the new position the player has moved to)
   - **Example**: `{"type": "move", "position": {"x": 1, "y": 2}}`
   - **Response**: A notification message indicating the player's new position and updates to the game state.

3. **Chat**
   - **Type**: `chat`
   - **Data Field**: `message` (the message to be sent)
   - **Example**: `{"type": "chat", "message": "Hello!"}`
   - **Response**: A message echoing the chat message with the client's address.

4. **Quit**
   - **Type**: `quit`
   - **Example**: `{"type": "quit"}`
   - **Response**: A notification message indicating that the client has left the game.

5. **State**
   - **Type**: `state`
   - **Response**: Sends the current game state to all clients, including the board and which player's turn it is.

### Connection Management
- The server maintains a list of connected clients and their associated game states.
- Each player is assigned a unique identifier to manage turns and moves.
- The game ensures that only the current player can make a move.

### Turn Management
- Players take turns making moves, which are synchronized across all clients.
- The server manages whose turn it is and updates the game state accordingly.
