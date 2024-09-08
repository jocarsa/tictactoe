import cv2
import numpy as np
import random
import os
import time

# Constants
WIDTH, HEIGHT = 1920, 1080
LINE_COLOR = (0, 0, 0)
LINE_THICKNESS = 5
O_COLOR = (255, 0, 0)
X_COLOR = (0, 0, 255)
FONT = cv2.FONT_HERSHEY_SIMPLEX
DRAW_FPS = 60  # Frames per second
ANIMATION_FRAMES = 5  # Number of frames for each drawing animation
VIDEO_DURATION = 60  # Duration of the video in seconds
TOTAL_FRAMES = VIDEO_DURATION * DRAW_FPS  # Total frames for the video

# Ensure render directory exists
if not os.path.exists('render'):
    os.makedirs('render')

# Get epoch time for filename
epoch_time = int(time.time())
filename = f'render/tic_tac_toe_animated_{epoch_time}.mp4'

def calculate_margins_and_cell_size(SIZE):
    # Calculate cell size to fit within the screen
    max_cell_size = min(WIDTH, HEIGHT) // SIZE - LINE_THICKNESS
    margin_x = (WIDTH - (max_cell_size * SIZE)) // 2
    margin_y = (HEIGHT - (max_cell_size * SIZE)) // 2
    return margin_x, margin_y, max_cell_size

def draw_board(frame, board, margin_x, margin_y, CELL_SIZE):
    SIZE = len(board)
    for i in range(1, SIZE):
        # Horizontal lines
        cv2.line(frame, (margin_x, margin_y + i * CELL_SIZE), 
                 (margin_x + CELL_SIZE * SIZE, margin_y + i * CELL_SIZE), LINE_COLOR, LINE_THICKNESS)
        # Vertical lines
        cv2.line(frame, (margin_x + i * CELL_SIZE, margin_y), 
                 (margin_x + i * CELL_SIZE, margin_y + CELL_SIZE * SIZE), LINE_COLOR, LINE_THICKNESS)
        
    for row in range(SIZE):
        for col in range(SIZE):
            center = (margin_x + col * CELL_SIZE + CELL_SIZE // 2, 
                      margin_y + row * CELL_SIZE + CELL_SIZE // 2)
            if board[row][col] == 'O':
                cv2.circle(frame, center, CELL_SIZE // 3, O_COLOR, LINE_THICKNESS)
            elif board[row][col] == 'X':
                cv2.line(frame, (center[0] - CELL_SIZE // 4, center[1] - CELL_SIZE // 4),
                         (center[0] + CELL_SIZE // 4, center[1] + CELL_SIZE // 4), X_COLOR, LINE_THICKNESS)
                cv2.line(frame, (center[0] + CELL_SIZE // 4, center[1] - CELL_SIZE // 4),
                         (center[0] - CELL_SIZE // 4, center[1] + CELL_SIZE // 4), X_COLOR, LINE_THICKNESS)

def animate_O(frame, center, CELL_SIZE):
    for i in range(ANIMATION_FRAMES):
        angle = int(360 * i / ANIMATION_FRAMES)
        axes = (CELL_SIZE // 3, CELL_SIZE // 3)
        cv2.ellipse(frame, center, axes, 0, 0, angle, O_COLOR, LINE_THICKNESS)
        yield frame.copy()

def animate_X(frame, center, CELL_SIZE):
    line_step = CELL_SIZE // (4 * ANIMATION_FRAMES)
    # Draw the first diagonal
    for i in range(ANIMATION_FRAMES):
        cv2.line(frame, (center[0] - line_step * i, center[1] - line_step * i),
                 (center[0] - CELL_SIZE // 4, center[1] - CELL_SIZE // 4), X_COLOR, LINE_THICKNESS)
        cv2.line(frame, (center[0] + CELL_SIZE // 4, center[1] + CELL_SIZE // 4),
                 (center[0] + line_step * i, center[1] + line_step * i), X_COLOR, LINE_THICKNESS)
        yield frame.copy()
    # Draw the second diagonal
    for i in range(ANIMATION_FRAMES):
        cv2.line(frame, (center[0] + line_step * i, center[1] - line_step * i),
                 (center[0] + CELL_SIZE // 4, center[1] - CELL_SIZE // 4), X_COLOR, LINE_THICKNESS)
        cv2.line(frame, (center[0] - CELL_SIZE // 4, center[1] + CELL_SIZE // 4),
                 (center[0] - line_step * i, center[1] + line_step * i), X_COLOR, LINE_THICKNESS)
        yield frame.copy()

def check_winner(board):
    SIZE = len(board)
    # Check rows and columns
    for i in range(SIZE):
        if all([board[i][j] == 'O' for j in range(SIZE)]) or all([board[i][j] == 'X' for j in range(SIZE)]):
            return board[i][0]
        if all([board[j][i] == 'O' for j in range(SIZE)]) or all([board[j][i] == 'X' for j in range(SIZE)]):
            return board[0][i]

    # Check diagonals
    if all([board[i][i] == 'O' for i in range(SIZE)]) or all([board[i][i] == 'X' for i in range(SIZE)]):
        return board[0][0]
    if all([board[i][SIZE - i - 1] == 'O' for i in range(SIZE)]) or all([board[i][SIZE - i - 1] == 'X' for i in range(SIZE)]):
        return board[0][SIZE - 1]

    # Check draw
    if all([cell != '' for row in board for cell in row]):
        return 'Draw'

    return None

def random_move(board, player):
    empty_cells = [(r, c) for r in range(len(board)) for c in range(len(board)) if board[r][c] == '']
    if empty_cells:
        r, c = random.choice(empty_cells)
        board[r][c] = player
        return r, c
    return None, None

def main():
    SIZE = random.randint(3, 10)  # Randomize the size of the board at the start
    margin_x, margin_y, CELL_SIZE = calculate_margins_and_cell_size(SIZE)
    board = [['' for _ in range(SIZE)] for _ in range(SIZE)]
    
    frame = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255
    players = ['O', 'X']
    current_player_index = 0

    out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), DRAW_FPS, (WIDTH, HEIGHT))

    for frame_count in range(TOTAL_FRAMES):  # Control the total number of frames
        draw_board(frame, board, margin_x, margin_y, CELL_SIZE)
        out.write(frame)

        winner = check_winner(board)
        if winner:
            if winner == 'Draw':
                text = "Draw! Restarting..."
            else:
                text = f"{winner} Wins! Restarting..."
            text_size = cv2.getTextSize(text, FONT, 1.5, 3)[0]
            text_x = (WIDTH - text_size[0]) // 2
            text_y = (HEIGHT + text_size[1]) // 2
            cv2.putText(frame, text, (text_x, text_y), FONT, 1.5, LINE_COLOR, 3, cv2.LINE_AA)
            for _ in range(DRAW_FPS):  # Pause for 1 second to show the message
                out.write(frame)
            board = [['' for _ in range(SIZE)] for _ in range(SIZE)]  # Reset board
            frame = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255  # Clear frame
            current_player_index = 0
        else:
            row, col = random_move(board, players[current_player_index])
            if row is not None and col is not None:
                center = (margin_x + col * CELL_SIZE + CELL_SIZE // 2, 
                          margin_y + row * CELL_SIZE + CELL_SIZE // 2)
                if players[current_player_index] == 'O':
                    for frame in animate_O(frame.copy(), center, CELL_SIZE):
                        out.write(frame)
                else:
                    for frame in animate_X(frame.copy(), center, CELL_SIZE):
                        out.write(frame)

            current_player_index = (current_player_index + 1) % 2

    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
