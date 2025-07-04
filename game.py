class TicTacToeGame:
    def __init__(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.moves = 0
        self.winner = None

    def make_move(self, player_index, row, col):
        if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == ' ':
            self.board[row][col] = 'X' if player_index == 0 else 'O'
            self.moves += 1
            if self.check_winner(row, col):
                self.winner = player_index
            return True
        return False

    def check_winner(self, row, col):
        symbol = self.board[row][col]

        # Check row
        if all(self.board[row][c] == symbol for c in range(3)):
            return True
        # Check column
        if all(self.board[r][col] == symbol for r in range(3)):
            return True
        # Check diagonals
        if row == col and all(self.board[i][i] == symbol for i in range(3)):
            return True
        if row + col == 2 and all(self.board[i][2 - i] == symbol for i in range(3)):
            return True
        return False

    def is_over(self):
        return self.winner is not None or self.moves == 9

    def get_winner(self):
        return self.winner  # Returns 0 (player1), 1 (player2), or None for draw

    def render(self):
        return '\n'.join([
            ' | '.join(self.board[i]) + ('\n' + '-' * 9 if i < 2 else '')
            for i in range(3)
        ])
