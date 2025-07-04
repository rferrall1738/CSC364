import socket
import threading
import json
import os
from game import TicTacToeGame
import time
import signal
import sys

time.sleep(0.1)
HOST = 'localhost'
PORT = 877
SCOREBOARD_FILE = "scoreboard.json"

waiting_clients = []
scoreboard_lock = threading.Lock()  # To protect concurrent access to scoreboard

# Scoreboard persistence
# ---------------------------
def load_scoreboard():
    if os.path.exists(SCOREBOARD_FILE):
        with open(SCOREBOARD_FILE, "r") as f:
            return json.load(f)
    return {}

def save_scoreboard():
    with open(SCOREBOARD_FILE, "w") as f:
        json.dump(scoreboard, f, indent=2)

scoreboard = load_scoreboard()

# Game logic between two clients
# ---------------------------
def handle_client_pair(client1, client2):
    try:
        # Step 1: Ask both players for names
        names = []
        for client in (client1, client2):
            client.send(b"Enter your player name: ")
            name = client.recv(1024).decode().strip()
            names.append(name)
            with scoreboard_lock:
                if name not in scoreboard:
                    scoreboard[name] = 0

        # Step 2: Initialize game
        game = TicTacToeGame()
        current = 0  # 0 = client1, 1 = client2

        # Step 3: Game loop
        while not game.is_over():
            board = game.render()
            for client in (client1, client2):
                client.send(f"\n{board}\n".encode())

            current_client = [client1, client2][current]
            current_name = names[current]

            # Prompt for move
            current_client.send(f"{current_name}, your move (row col): \n".encode())

            try:
                move_data = current_client.recv(1024)
                if not move_data:
                    break
                move = move_data.decode().strip().split()
                if len(move) != 2 or not all(m.isdigit() for m in move):
                    current_client.send(b"Invalid move format. Use: row col\n")
                    continue

                row, col = map(int, move)
                if not game.make_move(current, row, col):
                    current_client.send(b"Invalid move. Try again.\n")
                    continue

                current = 1 - current  # Swap turn
            except:
                break

        # Step 4: Game finished — render final board
        board = game.render()
        for client in (client1, client2):
            client.send(f"\n{board}\n".encode())

        # Step 5: Announce result
        result = game.get_winner()
        if result is None:
            message = "Game ended in a draw!\n"
            with scoreboard_lock:
                scoreboard[names[0]] += 1
                scoreboard[names[1]] += 1
        else:
            winner = names[result]
            message = f"{winner} wins!\n"
            with scoreboard_lock:
                scoreboard[winner] += 2

        save_scoreboard()

        # Step 6: Send final result and close sockets
        for client in (client1, client2):
            client.send(message.encode())
            client.close()

    except Exception as e:
        print("Game error:", e)
        client1.close()
        client2.close()

def signal_handler(sig, frame):
    print("\nShutting down server...")
    save_scoreboard()
    sys.exit(0)

# Accept clients and pair them
# ---------------------------
def wait_for_clients():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"Connected: {addr}")
        waiting_clients.append(client_socket)

        if len(waiting_clients) >= 2:
            c1 = waiting_clients.pop(0)
            c2 = waiting_clients.pop(0)
            thread = threading.Thread(target=handle_client_pair, args=(c1, c2))
            thread.start()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Handles Ctrl+C
    wait_for_clients()
