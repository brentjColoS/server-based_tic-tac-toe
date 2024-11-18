# server-based_tic-tac-toe
Repository for CS457 Semester-long project: Tic Tac Toe based on server-client connections.

## How to Play:
1. **Start the server:** Run the `server.py` script in the terminal.
   - Example: `python server.py -p 12345`
   
2. **Connect clients:** Run the `client.py` script on two different machines or terminals, specifying the server's IP address and port.
   - Example: `python client.py -i SERVER_IP -p 12345`

3. **Join the game:** Each client sends a join message to the server upon connection. The server assigns each player an ID ("X" or "O").

4. **Play the game:** Players take turns entering their moves by specifying row and column positions (e.g., "1 2"). The first player to get three in a row (vertically, horizontally, or diagonally) wins!

5. **Chat:** Players can communicate with each other via chat messages. These messages are sent to all connected clients.

6. **Game Over:** Once a player wins or the game ends in a draw, the server announces the outcome. Players are then offered the option to start a new game or quit.

## Technologies Used:
* Python
* Sockets

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
   - **Response**: A notification message indicating that the client has left the game.

5. **State**
   - **Type**: `state`
   - **Response**: Sends the current game state to all clients, including the board and which player's turn it is.

6. **Win**
   - **Type**: `win`
   - **Message Field**: `message` (indicating that a player has won the game)
   - **Example**: `{"type": "win", "message": "Player X wins!"}`
   - **Response**: A notification announcing the winner.

7. **Draw**
   - **Type**: `draw`
   - **Message Field**: `message` (indicating that the game has ended in a draw)
   - **Example**: `{"type": "draw", "message": "It's a draw!"}`
   - **Response**: A notification announcing that the game is a draw.

### Connection Management
- The server maintains a list of connected clients and their associated game states.
- Each player is assigned a unique identifier ("X" or "O") to manage turns and moves.
- The game ensures that only the current player can make a move. Players take turns, and the server tracks whose turn it is.

### Game State Management
- The server tracks the game board (3x3 grid) and updates it with each move.
- If a player wins (by getting three in a row horizontally, vertically, or diagonally), the server announces the winner.
- If the game ends in a draw (no empty spaces left and no winner), the server announces a draw.

### Turn Management
- Players take turns making moves, which are synchronized across all clients. Each player must wait for their turn to make a move.
- The server manages whose turn it is and updates the game state accordingly.

### User Interface
- The server sends regular updates to the clients, including the current game board, whose turn it is, and any game outcomes (win or draw).
- The client displays the game board and prompts the player for their next move (in the form of row and column coordinates).
- Players are notified when the game ends, either with a win or a draw, and are given the option to start a new game or quit.

### Example of Communication Flow:
1. **Client A** connects to the server and sends a `join` message.
2. The server assigns Player "X" to Client A and sends a `state` message with an empty board and "X's" turn.
3. **Client A** sends a `move` message with the coordinates `[0, 0]`, placing "X" on the board.
4. The server updates the board and sends the new game state to both clients.
5. **Client B** (Player "O") moves next, and the game continues.
6. If a player wins or the game ends in a draw, the server sends a `win` or `draw` message to all clients.

---

## Running the Game
### Server
To run the server, navigate to the project directory and execute the following command:
```bash
python server.py -p PORT
```
This will start the server, listening for connections on the specified port.

### Client
To run the client, execute the following command:
```bash
python client.py -i SERVER_IP -p PORT
```
This will connect the client to the server at the specified IP address and port.
