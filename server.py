import socket
import threading
import os
import json
from game import TicTacToeGame

HOST = 'localhost'
PORT = 8773
SCOREBOARD_FILE = "scoreboard.json"

waiting_clients = []
scoreboard_lock = threading.Lock()

def load_scoreboard():
    if os.path.exists(SCOREBOARD_FILE):
        with open(SCOREBOARD_FILE, "r") as f:
            return json.load(f)
    return {}

def save_scoreboard():
    with open(SCOREBOARD_FILE, "w") as f:
        json.dump(scoreboard, f, indent=2)

scoreboard = load_scoreboard()

def handle_client_pair(client1, client2):
    try:
        # Get player names
        name1 = client1.recv(1024).decode().strip()
        name2 = client2.recv(1024).decode().strip()

        # Assign symbols
        client1.send(b"You are X\n")
        client2.send(b"You are O\n")

        names = [name1, name2]
        symbols = ['X', 'O']
        clients = [client1, client2]
        game = TicTacToeGame()
        current = 0

        while not game.is_over():
            try:
                board = game.render()
                for c in clients:

                    c.send(f"\n{board}\n".encode())

                current_client = clients[current]
                opposing_client = clients[1 - current]

                # Indicate turn
                for i, c in enumerate(clients):
                    c.send(f"TURN {symbols[current]}\n".encode())
                    if i == current:
                        c.send(f"{names[current]}, your move (row col):\n".encode())

                move_data = current_client.recv(1024)
                move = move_data.decode().strip().split()
                if len(move) != 2 or not all(x.isdigit() for x in move):
                    current_client.send(b"Invalid input\n")
                    continue

                row, col = map(int, move)
                if not game.make_move(current, row, col):
                    current_client.send(b"Invalid move. Try again.\n")
                    continue

                current = 1 - current
            except(ConnectionResetError, ConnectionAbortedError, socket.error) as e:
                print(f"Player {names[current]} left the game: {e}\n")
                opposing_client.send(f"Player {names[current]} left the game. Easy win this time.\n".encode())
                with scoreboard_lock:
                    scoreboard[names[1-current]] = scoreboard.get(names[1-current], 0) + 2
                    save_scoreboard()
                opposing_client.close()
                current_client.close()
                return


        # Send final board
        board = game.render()
        for c in clients:
            c.send(f"\n{board}\n".encode())

        # Announce winner
        winner = game.get_winner()
        if winner is not None:
            message = f"{names[winner]} wins!\n"
        else:
            message = "It's a draw!\n"

        # Update scoreboard
        with scoreboard_lock:
            if winner is not None:
                scoreboard[names[winner]] = scoreboard.get(names[winner], 0) + 2
            else:
                for name in names:
                    scoreboard[name] = scoreboard.get(name, 0) + 1
            save_scoreboard()

        for c in clients:
            c.send(message.encode())
            c.send(b"RESET\n")
            c.close()

        print("Updated scoreboard:", scoreboard)

    except Exception as e:
        print("Game error:", e)
        client1.close()
        client2.close()

def wait_for_clients():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server running on {HOST}:{PORT}")

    while True:
        client, addr = server.accept()
        print(f"Connected: {addr}")
        waiting_clients.append(client)

        if len(waiting_clients) >= 2:
            c1 = waiting_clients.pop(0)
            c2 = waiting_clients.pop(0)
            threading.Thread(target=handle_client_pair, args=(c1, c2), daemon=True).start()

if __name__ == "__main__":
    wait_for_clients()
