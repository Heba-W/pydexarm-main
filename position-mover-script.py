import serial
import time

# === Config ===
# Chessboard start values (from H8 = -130mm, Y = 200mm)
x_start = -130
y_start = 200
x_spacing = 30  # space between columns (30mm per tile)
y_spacing = (390 - 200) / 7  # ~27.14mm between rows (default)

# Chessboard column mapping
columns = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
rows = ['8', '7', '6', '5', '4', '3', '2', '1']

# Chessboard x, y coordinates for each row (row 8, row 7, row 6 provided)
coords = {
    '8': {'a': 80, 'b': 55, 'c': 25, 'd': -5, 'e': -35, 'f': -60, 'g': -90, 'h': -120},
    '7': {'a': 80, 'b': 55, 'c': 25, 'd': -5, 'e': -35, 'f': -60, 'g': -90, 'h': -120},
    '6': {'a': 80, 'b': 55, 'c': 25, 'd': -5, 'e': -35, 'f': -60, 'g': -90, 'h': -120},
    '5': {'a': 80, 'b': 50, 'c': 20, 'd': -10, 'e': -40, 'f': -70, 'g': -100, 'h': -130},  # Adjusted X coordinates for row 5
    '4': {'a': 80, 'b': 50, 'c': 20, 'd': -10, 'e': -40, 'f': -70, 'g': -100, 'h': -130},  # Adjusted X coordinates for row 4
    '3': {'a': 80, 'b': 50, 'c': 20, 'd': -10, 'e': -40, 'f': -70, 'g': -100, 'h': -130},  # Adjusted X coordinates for row 3
    '2': {'a': 80, 'b': 50, 'c': 20, 'd': -10, 'e': -40, 'f': -70, 'g': -100, 'h': -130},  # Adjusted X coordinates for row 2
    '1': {'a': 80, 'b': 50, 'c': 20, 'd': -10, 'e': -40, 'f': -70, 'g': -100, 'h': -130},  # Adjusted X coordinates for row 1
}

# Adjustments for row Y values
y_offsets = {
    '8': 200,  # Row 8 is at Y = 200
    '7': 220,  # Row 7 is at Y = 220
    '6': 250,  # Row 6 is at Y = 250
    '5': 280,  # Row 5 is at Y = 280
    '4': 310,  # Row 4 is at Y = 310
    '3': 340,  # Row 3 is at Y = 340
    '2': 370,  # Row 2 is at Y = 370
    '1': 390,  # Row 1 is at Y = 390
}

# Function to return the coordinates of any square
def get_coords(square):
    col = square[0].lower()
    row = square[1]

    if col not in columns or row not in rows:
        raise ValueError("Invalid square. Use format like 'e2'")

    # For rows 7-1, X spacing remains consistent, adjust the Y based on the row
    if row in coords:
        if col in coords[row]:
            x = coords[row][col]
            y = y_offsets[row]
            return x, y
    raise ValueError(f"Invalid position for {square}. Please check the row and column.")

# === Serial connection ===
ser = serial.Serial("COM4", 115200, timeout=1)
time.sleep(2)

# === Move to center first ===
print("Moving to board centering position (X-20 Y290 Z-40)...")
ser.write("G0 X-20 Y290 Z-40 F2000\n".encode())
time.sleep(4)

user_input = input("Is the chessboard centered? (y/n): ").lower()
if user_input == "y":
    print("Great! The board is centered.")
else:
    print("You can adjust the board manually while the arm is in position.")

# === Position control ===
while True:
    square = input("Enter square (e.g., e2) or 'q' to quit: ").lower()
    if square == 'q':
        break
    try:
        x, y = get_coords(square)
        print(f"Moving to {square.upper()} at X{x:.1f} Y{y:.1f} Z-40")
        ser.write(f"G0 X{x:.1f} Y{y:.1f} Z-40 F2000\n".encode())
        time.sleep(3)
    except ValueError as e:
        print(e)

ser.close()
print("Program ended.")
