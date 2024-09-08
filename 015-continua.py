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
STRIKE_THICKNESS = 10
FONT = cv2.FONT_HERSHEY_SIMPLEX
DRAW_FPS = 60  # Frames per second
ANIMATION_FRAMES = 5  # Number of frames for each drawing animation
VIDEO_DURATION = 60 * 1  # Duration of the video in seconds
TOTAL_FRAMES = VIDEO_DURATION * DRAW_FPS  # Total frames for the video

# Ensure render directory exists
if not os.path.exists('render'):
    os.makedirs('render')

# Get epoch time for filename
epoch_time = int(time.time())
filename = f'render/tic_tac_toe_animated_{epoch_time}.mp4'


def calculate_margins_and_cell_size(SIZE):
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

    # Check rows
    for i in range(SIZE):
        for j in range(SIZE - 2):  # Look for any 3 consecutive cells
            if board[i][j] != '' and board[i][j] == board[i][j+1] == board[i][j+2]:
                return board[i][j], ('row', i, j)

    # Check columns
    for i in range(SIZE):
        for j in range(SIZE - 2):  # Look for any 3 consecutive cells
            if board[j][i] != '' and board[j][i] == board[j+1][i] == board[j+2][i]:
                return board[j][i], ('col', i, j)

    # Check main diagonals
    for i in range(SIZE - 2):
        if board[i][i] != '' and board[i][i] == board[i+1][i+1] == board[i+2][i+2]:
            return board[i][i], ('diag', i)

    # Check anti-diagonals
    for i in range(SIZE - 2):
        if board[i][SIZE-i-1] != '' and board[i][SIZE-i-1] == board[i+1][SIZE-i-2] == board[i+2][SIZE-i-3]:
            return board[i][SIZE-i-1], ('anti_diag', i)

    # Check draw
    if all([cell != '' for row in board for cell in row]):
        return 'Draw', None

    return None, None


def draw_strike_line(frame, margin_x, margin_y, CELL_SIZE, SIZE, win_info, color):
    if win_info[0] == 'row':
        _, row, col_start = win_info
        start_point = (margin_x + col_start * CELL_SIZE, margin_y + row * CELL_SIZE + CELL_SIZE // 2)
        end_point = (margin_x + (col_start + 2) * CELL_SIZE + CELL_SIZE, margin_y + row * CELL_SIZE + CELL_SIZE // 2)
    elif win_info[0] == 'col':
        _, col, row_start = win_info
        start_point = (margin_x + col * CELL_SIZE + CELL_SIZE // 2, margin_y + row_start * CELL_SIZE)
        end_point = (margin_x + col * CELL_SIZE + CELL_SIZE // 2, margin_y + (row_start + 2) * CELL_SIZE + CELL_SIZE)
    elif win_info[0] == 'diag':
        _, start_idx = win_info
        start_point = (margin_x + start_idx * CELL_SIZE, margin_y + start_idx * CELL_SIZE)
        end_point = (margin_x + (start_idx + 2) * CELL_SIZE + CELL_SIZE, margin_y + (start_idx + 2) * CELL_SIZE + CELL_SIZE)
    elif win_info[0] == 'anti_diag':
        _, start_idx = win_info
        start_point = (margin_x + (SIZE - start_idx - 3) * CELL_SIZE + CELL_SIZE, margin_y + start_idx * CELL_SIZE)
        end_point = (margin_x + (SIZE - start_idx - 1) * CELL_SIZE, margin_y + (start_idx + 2) * CELL_SIZE + CELL_SIZE)

    cv2.line(frame, start_point, end_point, color, STRIKE_THICKNESS)


def random_move(board, player, opponent):
    empty_cells = [(r, c) for r in range(len(board)) for c in range(len(board)) if board[r][c] == '']
    if not empty_cells:
        return None, None

    # Check if player can win
    for r, c in empty_cells:
        board[r][c] = player
        if check_winner(board)[0] == player:
            return r, c
        board[r][c] = ''

    # Check if opponent can win and block
    for r, c in empty_cells:
        board[r][c] = opponent
        if check_winner(board)[0] == opponent:
            board[r][c] = player
            return r, c
        board[r][c] = ''

    # No immediate win or block, choose random
    return random.choice(empty_cells)


def draw_text_with_capsule(frame, text, font, font_scale, thickness, position, text_color, capsule_color, capsule_padding=20):
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x, text_y = position

    # Calculate capsule dimensions
    capsule_width = text_size[0] + capsule_padding * 2
    capsule_height = text_size[1] + capsule_padding * 2
    capsule_top_left = (text_x - capsule_padding, text_y - text_size[1] - capsule_padding)
    capsule_bottom_right = (text_x + text_size[0] + capsule_padding, text_y + capsule_padding)

    # Draw the capsule (rounded rectangle)
    radius = int(capsule_height / 2)
    cv2.rectangle(frame, capsule_top_left, capsule_bottom_right, capsule_color, -1, lineType=cv2.LINE_AA)
    cv2.circle(frame, (capsule_top_left[0] + radius, capsule_top_left[1] + radius), radius, capsule_color, -1, lineType=cv2.LINE_AA)
    cv2.circle(frame, (capsule_bottom_right[0] - radius, capsule_top_left[1] + radius), radius, capsule_color, -1, lineType=cv2.LINE_AA)

    # Draw the text
    cv2.putText(frame, text, position, font, font_scale, text_color, thickness, cv2.LINE_AA)


def main():
    SIZE = random.randint(10, 15)  # Randomize the size of the board at the start
    margin_x, margin_y, CELL_SIZE = calculate_margins_and_cell_size(SIZE)
    board = [['' for _ in range(SIZE)] for _ in range(SIZE)]

    frame = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255
    players = ['O', 'X']
    current_player_index = 0

    out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), DRAW_FPS, (WIDTH, HEIGHT))

    frame_count = 0

    while frame_count < TOTAL_FRAMES:
        draw_board(frame, board, margin_x, margin_y, CELL_SIZE)
        out.write(frame)
        frame_count += 1

        winner, win_info = check_winner(board)
        if winner and winner != 'Draw':
            color = O_COLOR if winner == 'O' else X_COLOR
            draw_strike_line(frame, margin_x, margin_y, CELL_SIZE, SIZE, win_info, color)

            for _ in range(DRAW_FPS):  # Pause briefly to show the strike
                if frame_count >= TOTAL_FRAMES:
                    break
                out.write(frame)
                frame_count += 1

        if winner == 'Draw':
            text = "Draw! Restarting..."
            draw_text_with_capsule(frame, text, FONT, 1.5, 3, ((WIDTH - cv2.getTextSize(text, FONT, 1.5, 3)[0][0]) // 2,
                                                              (HEIGHT + cv2.getTextSize(text, FONT, 1.5, 3)[0][1]) // 2), LINE_COLOR, (255, 255, 255))
            for _ in range(DRAW_FPS):  # Pause for 1 second to show the message
                if frame_count >= TOTAL_FRAMES:
                    break
                out.write(frame)
                frame_count += 1
            # Reset board after a draw
            board = [['' for _ in range(SIZE)] for _ in range(SIZE)]
            frame = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255  # Clear frame
            current_player_index = 0

        if winner != 'Draw':  # Continue the game after a win until all cells are filled
            player = players[current_player_index]
            opponent = players[(current_player_index + 1) % 2]

            row, col = random_move(board, player, opponent)
            if row is not None and col is not None:
                # Ensure the move is placed on an empty cell
                if board[row][col] == '':
                    center = (margin_x + col * CELL_SIZE + CELL_SIZE // 2,
                              margin_y + row * CELL_SIZE + CELL_SIZE // 2)
                    if player == 'O':
                        for frame in animate_O(frame.copy(), center, CELL_SIZE):
                            if frame_count >= TOTAL_FRAMES:
                                break
                            out.write(frame)
                            frame_count += 1
                    else:
                        for frame in animate_X(frame.copy(), center, CELL_SIZE):
                            if frame_count >= TOTAL_FRAMES:
                                break
                            out.write(frame)
                            frame_count += 1

                    board[row][col] = player

            if frame_count >= TOTAL_FRAMES:
                break

            current_player_index = (current_player_index + 1) % 2

        # Check if the board is full and restart
        if all([cell != '' for row in board for cell in row]):
            text = "Board full! Restarting..."
            draw_text_with_capsule(frame, text, FONT, 1.5, 3, ((WIDTH - cv2.getTextSize(text, FONT, 1.5, 3)[0][0]) // 2,
                                                              (HEIGHT + cv2.getTextSize(text, FONT, 1.5, 3)[0][1]) // 2), LINE_COLOR, (255, 255, 255))
            for _ in range(DRAW_FPS):  # Pause for 1 second to show the message
                if frame_count >= TOTAL_FRAMES:
                    break
                out.write(frame)
                frame_count += 1

            # Reset the board
            board = [['' for _ in range(SIZE)] for _ in range(SIZE)]
            frame = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255  # Clear frame
            current_player_index = 0

    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
