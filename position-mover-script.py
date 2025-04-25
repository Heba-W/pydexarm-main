import serial
import time
import random

# === Config ===
columns = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
rows = ['8', '7', '6', '5', '4', '3', '2', '1']

coords = {
    '8': {'a': 80, 'b': 55, 'c': 25, 'd': -5,  'e': -35, 'f': -60, 'g': -90,  'h': -120},
    '7': {'a': 80, 'b': 47, 'c': 26, 'd': -5,  'e': -35, 'f': -60, 'g': -90,  'h': -120},
    '6': {'a': 80, 'b': 47, 'c': 26, 'd': -5,  'e': -35, 'f': -60, 'g': -90,  'h': -120},
    '5': {'a': 80, 'b': 47, 'c': 26, 'd': -5,  'e': -35, 'f': -60, 'g': -90,  'h': -120},
    '4': {'a': 80, 'b': 47, 'c': 26, 'd': -5,  'e': -35, 'f': -60, 'g': -90,  'h': -120},
    '3': {'a': 80, 'b': 47, 'c': 26, 'd': -5,  'e': -35, 'f': -60, 'g': -90,  'h': -120},
    '2': {'a': 80, 'b': 47, 'c': 26, 'd': -5,  'e': -35, 'f': -60, 'g': -90,  'h': -120},
    '1': {'a': 80, 'b': 47, 'c': 26, 'd': -5,  'e': -35, 'f': -60, 'g': -90,  'h': -120},
}

y_offsets = {
    '8': 200, '7': 220, '6': 250, '5': 280,
    '4': 310, '3': 340, '2': 370, '1': 390,
}

captured_counts = {'r': 0, 'b': 0}

def get_coords(square):
    col = square[0].lower()
    row = square[1]
    if col not in columns or row not in rows:
        raise ValueError("Invalid square. Use format like 'e2'")
    x = coords[row][col]
    y = y_offsets[row]
    return x, y

ser = serial.Serial("COM4", 115200, timeout=1)
time.sleep(2)
ser.write("G0 X-20 Y290 Z-40 F2000\n".encode())
time.sleep(4)
input("Adjust board if needed, then Enter to start...")

def activate_gripper(action):
    if action == "pick":
        ser.write("M1000\n".encode())
    elif action == "release":
        ser.write("M1002\n".encode())

def move_piece_physical(start, end, capture=False, color=None):
    x_start, y_start = get_coords(start)
    ser.write(f"G0 X{x_start:.1f} Y{y_start:.1f} Z-20 F2000\n".encode())
    time.sleep(3)
    ser.write("G0 Z-50 F1000\n".encode())
    time.sleep(2)
    activate_gripper("pick")
    time.sleep(1)
    ser.write("G0 Z-20 F1000\n".encode())
    time.sleep(1)

    if capture:
        z_drop = -70 + (captured_counts[color] * 10)
        y_dest = 343 if color == 'r' else 303
        ser.write(f"G0 X-170 Y{y_dest} Z-20 F2000\n".encode())
        time.sleep(3)
        ser.write(f"G0 Z{z_drop} F1000\n".encode())
        time.sleep(2)
        activate_gripper("release")
        time.sleep(1)
        ser.write("G0 Z-20 F1000\n".encode())
        time.sleep(1)
        captured_counts[color] += 1
    else:
        x_end, y_end = get_coords(end)
        ser.write(f"G0 X{x_end:.1f} Y{y_end:.1f} Z-20 F2000\n".encode())
        time.sleep(3)
        ser.write("G0 Z-50 F1000\n".encode())
        time.sleep(2)
        activate_gripper("release")
        time.sleep(1)
        ser.write("G0 Z-20 F1000\n".encode())
        time.sleep(1)

board = {col+row: ' ' for row in rows for col in columns}
for row in ['8', '7', '6']:
    for col in columns:
        if (columns.index(col) + rows.index(row)) % 2 != 0:
            board[col+row] = 'b'
for row in ['3', '2', '1']:
    for col in columns:
        if (columns.index(col) + rows.index(row)) % 2 != 0:
            board[col+row] = 'r'

def print_board():
    print("\n  h g f e d c b a")
    for row in rows:
        line = row + " "
        for col in columns[::-1]:
            line += board[col+row] + " "
        print(line)
    print()

def make_move(start, end):
    board[end] = board[start]
    board[start] = ' '

def remove_piece(square):
    board[square] = ' '

def promote_if_needed(square):
    piece = board[square]
    if piece == 'r' and square[1] == '8':
        board[square] = 'R'
    elif piece == 'b' and square[1] == '1':
        board[square] = 'B'

def is_valid_human_move(start, end):
    if start not in board or end not in board:
        return False
    piece = board[start]
    if piece not in ['r', 'R']:
        return False
    if board[end] != ' ':
        return False
    col_s, row_s = start[0], start[1]
    col_e, row_e = end[0], end[1]
    dx = columns.index(col_e) - columns.index(col_s)
    dy = int(row_e) - int(row_s)
    if abs(dx) != abs(dy):
        return False
    if abs(dx) not in [1, 2]:
        return False
    if piece == 'r' and dy < 0:
        return False
    if abs(dx) == 2:
        mid_col = columns[columns.index(col_s) + dx // 2]
        mid_row = str(int(row_s) + dy // 2)
        mid_square = mid_col + mid_row
        if board[mid_square] not in ['b', 'B']:
            return False
    return True

def get_robot_moves():
    moves = []
    for square, piece in board.items():
        if piece not in ['b', 'B']:
            continue
        col, row = square[0], square[1]
        col_idx = columns.index(col)
        row_idx = rows.index(row)
        directions = [(-1, 1), (1, 1)] if piece == 'b' else [(-1, 1), (1, 1), (-1, -1), (1, -1)]
        for dx, dy in directions:
            c_idx, r_idx = col_idx + dx, row_idx + dy
            if 0 <= c_idx < 8 and 0 <= r_idx < 8:
                target = columns[c_idx] + rows[r_idx]
                if board[target] == ' ':
                    moves.append((square, target))
        for dx, dy in directions:
            c_idx, r_idx = col_idx + 2*dx, row_idx + 2*dy
            mid_c, mid_r = col_idx + dx, row_idx + dy
            if 0 <= c_idx < 8 and 0 <= r_idx < 8:
                target = columns[c_idx] + rows[r_idx]
                middle = columns[mid_c] + rows[mid_r]
                if board[target] == ' ' and board[middle] in ['r', 'R']:
                    moves.insert(0, (square, target, middle))
    return moves

while True:
    print_board()
    start = input("Your move - start square (e.g., e2) or 'q' to quit: ").lower()
    if start == 'q':
        break
    end = input("Your move - end square (e.g., e4): ").lower()
    if end == 'q':
        break

    try:
        if not is_valid_human_move(start, end):
            print("Invalid move. Try again.")
            continue
        dx = columns.index(end[0]) - columns.index(start[0])
        if abs(dx) == 2:
            mid_col = columns[columns.index(start[0]) + dx // 2]
            mid_row = str((int(start[1]) + int(end[1])) // 2)
            captured = mid_col + mid_row
            move_piece_physical(captured, None, capture=True, color='b')
            remove_piece(captured)
        make_move(start, end)
        promote_if_needed(end)
        move_piece_physical(start, end)

        robot_moves = get_robot_moves()
        if not robot_moves:
            print("Robot has no moves left. You win!")
            break
        move = robot_moves[0]
        if len(move) == 3:
            s, e, capture = move
            print(f"Robot jumps from {s} to {e} capturing {capture}")
            move_piece_physical(capture, None, capture=True, color='r')
            remove_piece(capture)
        else:
            s, e = move
            print(f"Robot moves from {s} to {e}")
        make_move(s, e)
        promote_if_needed(e)
        move_piece_physical(s, e)

    except Exception as ex:
        print(f"Error: {ex}")

ser.close()
print("Game over.")
