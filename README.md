# server-based_tic-tac-toe
Repository for CS457 Semester-long project: Tic Tac Toe based on server-client connections.

## How to Play:
1. **Start the server:** Run the `server.py` script in the terminal.
   - Example: `python server.py -p 12345`
   - **Note:** The server log (`server_log.log`) will reset every time the server starts.

2. **Connect clients:** Run the `client.py` script on two different machines or terminals, specifying the server's IP address and port.
   - Example: `python client.py -i SERVER_IP -p 12345`

3. **Join the game:** Each client connects to the server and is assigned an ID and role ("X" or "O") based on the order of connection.

4. **Play the game:** Players take turns entering their moves by specifying row and column positions (e.g., "1,2"). The first player to get three in a row (vertically, horizontally, or diagonally) wins!

5. **Chat:** Players can communicate with each other via chat messages. These messages are sent to all connected clients.

6. **Game Over:** Once a player wins or the game ends in a draw, the server announces the outcome. The game board resets, and players can start a new game.

7. **Disconnection Handling:**
   - If a player disconnects, the other player is also disconnected, and the board resets.
   - New players can then connect to a fresh board.

## Technologies Used:
- Python
- Sockets

## Game Message Protocol

### Overview
This document defines the structure and format of messages exchanged between the server and clients in the game.

### Message Structure
Messages are formatted as JSON objects with the following fields:
- **type**: The type of the message (e.g., "join", "move", "chat", "quit", "state", "win", "draw").
- **message** (optional): Additional information depending on the message type (e.g., chat message, move position, or game state).

### Message Types
1. **Join**
   - **Type**: `join`
   - **Example**: `{"type": "join"}`
   - **Response**: A notification message indicating that the client has joined the game. Also includes the player ID ("X" or "O").

2. **Move**
   - **Type**: `move`
   - **Data Field**: `position` (the new position the player has moved to, specified as a pair of coordinates [row, col])
   - **Example**: `{"type": "move", "position": [1, 2]}`
   - **Response**: A notification message indicating the player's new position and updates to the game state. If the move results in a win or a draw, the game status will be updated accordingly.

3. **Chat**
   - **Type**: `chat`
   - **Data Field**: `message` (the message to be sent)
   - **Example**: `{"type": "chat", "message": "Hello!"}`
   - **Response**: A message echoing the chat message with the client's address.

4. **Quit**
   - **Type**: `quit`
   - **Example**: `{"type": "quit"}`
   - **Response**: A notification message indicating that the client has left the game. The server resets the game board and disconnects all players.

5. **Reset**
   - **Type**: `reset`
   - **Response**: The server announces that the game has been reset and provides a fresh game board.

6. **Win**
   - **Type**: `win`
   - **Message Field**: `message` (indicating that a player has won the game)
   - **Example**: `{"type": "win", "message": "Player X wins!"}`
   - **Response**: A notification announcing the winner. The game resets after a win.

7. **Draw**
   - **Type**: `draw`
   - **Message Field**: `message` (indicating that the game has ended in a draw)
   - **Example**: `{"type": "draw", "message": "It's a draw!"}`
   - **Response**: A notification announcing that the game is a draw. The game resets after a draw.

8. **Reassign**
   - **Type**: `reassign`
   - **Fields**: `client_id` (new player ID), `player_symbol` (new symbol, e.g., "X")
   - **Example**: `{"type": "reassign", "client_id": "player_1", "player_symbol": "X"}`
   - **Response**: Updates the client and server with the reassigned player information.

### Connection Management
- The server tracks all connected clients and their roles ("X" or "O").
- If one client disconnects, the other client is also disconnected, and the board resets for new players to join.

### Game State Management
- The server maintains a 3x3 game board and updates it with each move.
- After a win or draw, the game resets to a fresh state.

### Turn Management
- The server manages whose turn it is and ensures only the current player can make a move.
- If a player attempts an invalid move (e.g., placing on a taken spot), the client prompts the player to try again.

### Example of Communication Flow:
1. **Client A** connects to the server and is assigned "Player 1" (X).
2. **Client B** connects and is assigned "Player 2" (O).
3. Players take turns making moves.
4. The server announces a win, draw, or reset based on the game outcome.
5. If a player disconnects, the game resets, and the remaining player is disconnected.

---

## Running the Game
### Server
To run the server, navigate to the project directory and execute the following command:
```bash
python server.py -p PORT
```
This will start the server, listening for connections on the specified port. The log file will reset each time the server starts.

### Client
To run the client, execute the following command:
```bash
python client.py -i SERVER_IP -p PORT
```
This will connect the client to the server at the specified IP address and port.
