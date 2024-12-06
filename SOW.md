# Project Title:
Server-Based Tic Tac Toe

### Team:

Brent Jackson

### Project Objective:

The goal of the project is to program a Python-based server-to-client game of Tic Tac Toe. Using sockets and various connection protocols, the game will be played out between multiple computers. The system will handle disconnections gracefully, reset the game board for new players, and synchronize game states in real-time.

## Scope:

### Inclusions:

- Socket-based connections
- Multi-computer gameplay
- Tic Tac Toe with a text-based UI
- Real-time game state synchronization
- Disconnection handling and game reset logic

### Exclusions:

- GUI beyond text-based interaction

## Deliverables:

- Functioning Python scripts for client and server
- Proper documentation updated frequently
- Presentation-worthy programs and a comprehensive Wiki ready for demonstration

## Timeline:

The project progresses sprint by sprint, incorporating features such as:
1. Game state synchronization
2. Disconnection handling
3. Custom messaging between clients and the server
4. Enhancements to the board update mechanism for better user experience

### Key Milestones:

- Wiki Created
- Script Bases Created
- Initial Code Implemented
- Script Testing Added
- Disconnection Handling Finalized
- Scripts Finalized
- Wiki Finalized

## Task Breakdown:

- Wiki Created - 2 Hours
- Script Bases Created - 2 Hours
- Initial Code Added - 3 Hours
- Script Tests Added - 5 Hours
- Disconnection Handling Logic Added - 5 Hours
- Finalizing Scripts - Ongoing
- Wiki Finalized - 3 Hours

### Technical Requirements:

#### Hardware:

- Minimum 2 computers with a network connection and terminal access.

#### Software:

- Python 3 or later
- Terminal or command-line access

## Assumptions:

- The server and clients will maintain constant availability during the game.
- Players will connect and interact using text-based inputs.

## Roles and Responsibilities:

Brent Jackson is solely responsible for all aspects of development, testing, and documentation.

## Communication Plan:

All changes will be thoroughly documented and listed in the appropriate locations, such as the project Wiki and readme files.

## Updates Since Initial Scope:

- **Disconnection Handling:** If one player disconnects, the game resets, and all clients are disconnected to ensure a clean start for new players.
- **Game State Management:** Enhanced protocols ensure that the game board resets automatically after a win, draw, or player disconnection.
- **Client Notifications:** Clients are informed of game resets, board updates, and reassignments in real-time.
- **Taken Spot Handling:** Players attempting to place a move on an already occupied spot receive error prompts, allowing them to try again without disrupting gameplay.
- **Logging Improvements:** The server log resets at every start to provide clean logs for debugging and tracking gameplay.

## Additional Notes:

This document and the project Wiki will be updated iteratively along with the project. Stay tuned for exciting progress and a polished final product!
