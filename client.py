import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

HOST = 'localhost'
PORT = 8773

class TClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Tic Tac Toe")
        self.my_symbol = None
        self.my_turn = False
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        self.buttons = []
        self.create_board()
        threading.Thread(target=self.listen, daemon=True).start()
        self.master.after(100, self.get_name)

    #get name for scoreboard
    def get_name(self):
        self.name = simpledialog.askstring("Name", "Enter your player name:")
        if not self.name:
            messagebox.showinfo("Exiting", "You need a name to compete.")
            self.master.destroy()
            return
        self.s.send(self.name.encode())

    #creates gui board
    def create_board(self):
        for row in range(3):
            row_buttons = []
            for col in range(3):
                btn = tk.Button(self.master, text=" ", font=("Arial", 26), width=8, height=4,
                                command=lambda r=row, c=col: self.move(r, c), bg="#f0f0f0")
                btn.grid(row=row, column=col)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    #registers moves on the board
    def move(self, row, col):
        if not self.my_turn:
            return
        if self.buttons[row][col]['text'].strip():
            return  # Prevent clicking filled cells
        self.my_turn = False
        self.s.send(f"{row} {col}".encode())

    #listens for messages
    def listen(self):
        while True:
            try:
                data = self.s.recv(2048)
                if not data:
                    break
                message = data.decode()
                self.handle_message(message)
            except Exception as e:
                print("Connection error:", e)
                break

    #handles messages
    def handle_message(self, message):
        lines = message.strip().splitlines()
        for line in lines:
            if line.startswith("You are"):
                self.my_symbol = line.split()[-1]
            elif line.startswith("TURN"):
                parts = line.split()
                if len(parts) == 2:
                    self.my_turn = (parts[1] == self.my_symbol)
                    self.master.title("Tic Tac Toe - {}".format("Your turn" if self.my_turn else "Opponent's turn"))
                else:
                    print("Malformed TURN message:", line)
            elif "wins" in line or "draw" in line:
                self.update_board('\n'.join(lines))
                messagebox.showinfo("Game Over", line)
                self.master.quit()
                return
        self.update_board('\n'.join(lines))

    #updates board with user moves
    def update_board(self, message):
        board_lines = [line for line in message.strip().splitlines() if '|' in line]
        for i, line in enumerate(board_lines):
            cells = [cell.strip() for cell in line.split('|')]
            for j, val in enumerate(cells):
                self.buttons[i][j].config(text=val, disabledforeground='black')

if __name__ == "__main__":
    root = tk.Tk()
    client = TClient(root)
    root.mainloop()
