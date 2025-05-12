import tkinter as tk
import random
import pickle
import os

# Q-learning parameters
Q_table = {}
alpha = 0.1
gamma = 0.9
epsilon = 0.2

BOARD_SIZE = 8
SQUARE_SIZE = 60
WIN_REWARD = 2
LOSS_REWARD = -2
CAPTURE_REWARD = 1
LOSS_PIECE_PENALTY = -1
KING_REWARD = 0.5
OPPONENT_KING_PENALTY = -0.5

q_table_file = "q_table.pkl"

# Statistics
stats = {
    "games_played": 0,
    "red_wins": 0,
    "black_wins": 0,
    "moves": 0,
}

def load_q_table(filename=q_table_file):
    global Q_table
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            Q_table = pickle.load(f)

def save_q_table(filename=q_table_file):
    with open(filename, 'wb') as f:
        pickle.dump(Q_table, f)

def initialize_board():
    board = {}
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if (x + y) % 2 != 0:
                if y < 3:
                    board[(x, y)] = 'black'
                elif y > 4:
                    board[(x, y)] = 'red'
                else:
                    board[(x, y)] = None
    return board

def board_to_state(board):
    return str(board)

def get_valid_moves(board, color):
    moves = []
    direction = -1 if color == 'red' else 1
    opponent = 'black' if color == 'red' else 'red'
    for (x, y), piece in board.items():
        if piece and color in piece:
            directions = [(-1, direction), (1, direction)]
            if 'king' in piece:
                directions += [(-1, -direction), (1, -direction)]
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE:
                    if board.get((new_x, new_y)) is None:
                        moves.append(((x, y), (new_x, new_y)))
                    elif board.get((new_x, new_y), '').startswith(opponent):
                        jump_x, jump_y = new_x + dx, new_y + dy
                        if 0 <= jump_x < BOARD_SIZE and 0 <= jump_y < BOARD_SIZE and board.get((jump_x, jump_y)) is None:
                            moves.append(((x, y), (jump_x, jump_y)))
    return moves

def make_move(board, action):
    new_board = board.copy()
    from_pos, to_pos = action
    piece = new_board[from_pos]
    new_board[to_pos] = piece
    new_board[from_pos] = None
    if abs(from_pos[0] - to_pos[0]) == 2:
        mid_x = (from_pos[0] + to_pos[0]) // 2
        mid_y = (from_pos[1] + to_pos[1]) // 2
        new_board[(mid_x, mid_y)] = None
    if to_pos[1] == 0 and piece == 'red':
        new_board[to_pos] = 'red_king'
    elif to_pos[1] == BOARD_SIZE - 1 and piece == 'black':
        new_board[to_pos] = 'black_king'
    return new_board

def check_winner(board):
    red_pieces = sum(1 for p in board.values() if p and 'red' in p)
    black_pieces = sum(1 for p in board.values() if p and 'black' in p)
    if red_pieces == 0:
        return 'black'
    elif black_pieces == 0:
        return 'red'
    return None

def select_action(state, valid_moves):
    if not valid_moves:
        return None
    if random.random() < epsilon:
        return random.choice(valid_moves)
    q_values = [Q_table.get((state, move), 0) for move in valid_moves]
    max_q = max(q_values)
    best_moves = [move for move, q in zip(valid_moves, q_values) if q == max_q]
    return random.choice(best_moves)

def update_q_table(prev_state, action, reward, next_state, next_valid_moves):
    if action is None:
        return
    old_q = Q_table.get((prev_state, action), 0)
    future_q = max([Q_table.get((next_state, m), 0) for m in next_valid_moves], default=0)
    new_q = old_q + alpha * (reward + gamma * future_q - old_q)
    Q_table[(prev_state, action)] = new_q

class CheckersGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Checkers Self-Play")
        self.canvas = tk.Canvas(root, width=BOARD_SIZE * SQUARE_SIZE, height=BOARD_SIZE * SQUARE_SIZE)
        self.canvas.pack()
        self.stats_label = tk.Label(root, text="", font=("Arial", 12))
        self.stats_label.pack()
        self.board = initialize_board()
        self.current_color = 'red'
        self.running = False
        self.move_counter = 0

        load_q_table()
        self.draw_board()

        start_button = tk.Button(root, text="Start Training", command=self.start_training)
        start_button.pack(pady=5)

    def draw_board(self):
        self.canvas.delete("all")
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                color = "#D18B47" if (x + y) % 2 else "#FFCE9E"
                self.canvas.create_rectangle(x*SQUARE_SIZE, y*SQUARE_SIZE,
                                             (x+1)*SQUARE_SIZE, (y+1)*SQUARE_SIZE,
                                             fill=color)
        for (x, y), piece in self.board.items():
            if piece:
                fill_color = "red" if "red" in piece else "black"
                self.canvas.create_oval(x*SQUARE_SIZE+10, y*SQUARE_SIZE+10,
                                        (x+1)*SQUARE_SIZE-10, (y+1)*SQUARE_SIZE-10,
                                        fill=fill_color)
                if 'king' in piece:
                    self.canvas.create_text(x*SQUARE_SIZE+30, y*SQUARE_SIZE+30, text="K", fill="white", font=("Arial", 12, "bold"))
        self.update_stats_display()

    def update_stats_display(self):
        red_win_rate = (stats["red_wins"] / stats["games_played"] * 100) if stats["games_played"] else 0
        black_win_rate = (stats["black_wins"] / stats["games_played"] * 100) if stats["games_played"] else 0
        text = (f"Games Played: {stats['games_played']} | "
                f"Red Wins: {stats['red_wins']} ({red_win_rate:.1f}%) | "
                f"Black Wins: {stats['black_wins']} ({black_win_rate:.1f}%) | "
                f"Moves This Game: {self.move_counter}")
        self.stats_label.config(text=text)

    def start_training(self):
        self.running = True
        self.train_self_play()

    def train_self_play(self):
        if not self.running:
            return

        state = board_to_state(self.board)
        valid_moves = get_valid_moves(self.board, self.current_color)

        if not valid_moves:
            winner = 'black' if self.current_color == 'red' else 'red'
            self.register_game_end(winner)
            return

        action = select_action(state, valid_moves)
        new_board = make_move(self.board, action)
        next_state = board_to_state(new_board)
        next_color = 'black' if self.current_color == 'red' else 'red'
        next_valid_moves = get_valid_moves(new_board, next_color)

        reward = 0
        if self.check_capture(self.board, new_board):
            reward += CAPTURE_REWARD
        if self.check_lost_piece(self.board, new_board):
            reward += LOSS_PIECE_PENALTY
        if self.check_gained_king(self.board, new_board, self.current_color):
            reward += KING_REWARD
        if self.check_opponent_gained_king(self.board, new_board, self.current_color):
            reward += OPPONENT_KING_PENALTY

        update_q_table(state, action, reward, next_state, next_valid_moves)

        winner = check_winner(new_board)
        if winner:
            update_q_table(next_state, None, WIN_REWARD if winner == self.current_color else LOSS_REWARD, None, [])
            self.register_game_end(winner)
        else:
            self.board = new_board
            self.current_color = next_color
            self.move_counter += 1
            self.draw_board()
            self.root.after(100, self.train_self_play)

    def register_game_end(self, winner):
        stats["games_played"] += 1
        stats["red_wins"] += int(winner == 'red')
        stats["black_wins"] += int(winner == 'black')
        save_q_table()
        self.board = initialize_board()
        self.current_color = 'red'
        self.move_counter = 0
        self.draw_board()
        self.root.after(500, self.train_self_play)

    def check_capture(self, old_board, new_board):
        old_positions = {pos for pos, p in old_board.items() if p}
        new_positions = {pos for pos, p in new_board.items() if p}
        return len(new_positions) < len(old_positions)

    def check_lost_piece(self, old_board, new_board):
        for (x, y), piece in old_board.items():
            if piece and not new_board.get((x, y)):
                if self.current_color not in piece:
                    return True
        return False

    def check_gained_king(self, old_board, new_board, color):
        old_kings = {pos for pos, p in old_board.items() if p == f'{color}_king'}
        new_kings = {pos for pos, p in new_board.items() if p == f'{color}_king'}
        return len(new_kings) > len(old_kings)

    def check_opponent_gained_king(self, old_board, new_board, color):
        opponent = 'black' if color == 'red' else 'red'
        old_kings = {pos for pos, p in old_board.items() if p == f'{opponent}_king'}
        new_kings = {pos for pos, p in new_board.items() if p == f'{opponent}_king'}
        return len(new_kings) > len(old_kings)

if __name__ == "__main__":
    root = tk.Tk()
    app = CheckersGUI(root)
    root.mainloop()
