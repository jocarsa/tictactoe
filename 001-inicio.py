import cv2
import numpy as np
import random

# Constants
SIZE = 3
WIDTH, HEIGHT = 1920, 1080
CELL_SIZE = WIDTH // SIZE
LINE_COLOR = (0, 0, 0)
LINE_THICKNESS = 10
O_COLOR = (255, 0, 0)
X_COLOR = (0, 0, 255)
FONT = cv2.FONT_HERSHEY_SIMPLEX
DRAW_FPS = 1  # Frames per second

def draw_board(frame, board):
    for i in range(1, SIZE):
        # Horizontal lines
        cv2.line(frame, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), LINE_COLOR, LINE_THICKNESS)
        # Vertical lines
        cv2.line(frame, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), LINE_COLOR, LINE_THICKNESS)
        
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == 'O':
                cv2.circle(frame, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3, O_COLOR, LINE_THICKNESS)
            elif board[row][col] == 'X':
                cv2.line(frame, (col * CELL_SIZE + CELL_SIZE // 4, row * CELL_SIZE + CELL_SIZE // 4),
                         (col * CELL_SIZE + 3 * CELL_SIZE // 4, row * CELL_SIZE + 3 * CELL_SIZE // 4), X_COLOR, LINE_THICKNESS)
                cv2.line(frame, (col * CELL_SIZE + 3 * CELL_SIZE // 4, row * CELL_SIZE + CELL_SIZE // 4),
                         (col * CELL_SIZE + CELL_SIZE // 4, row * CELL_SIZE + 3 * CELL_SIZE // 4), X_COLOR, LINE_THICKNESS)

def check_winner(board):
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
    empty_cells = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] == '']
    if empty_cells:
        r, c = random.choice(empty_cells)
        board[r][c] = player

def main():
    board = [['' for _ in range(SIZE)] for _ in range(SIZE)]
    frame = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255
    players = ['O', 'X']
    current_player_index = 0

    out = cv2.VideoWriter('tic_tac_toe.mp4', cv2.VideoWriter_fourcc(*'mp4v'), DRAW_FPS, (WIDTH, HEIGHT))

    for _ in range(100):  # Assuming a maximum of 100 moves in 1 minute
        draw_board(frame, board)
        out.write(frame)

        winner = check_winner(board)
        if winner:
            if winner == 'Draw':
                text = "Draw! Restarting..."
            else:
                text = f"{winner} Wins! Restarting..."
            cv2.putText(frame, text, (WIDTH // 3, HEIGHT // 2), FONT, 3, LINE_COLOR, 6, cv2.LINE_AA)
            for _ in range(30):  # Display message for a second
                out.write(frame)
            board = [['' for _ in range(SIZE)] for _ in range(SIZE)]  # Reset board
            frame = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255  # Clear frame
            current_player_index = 0
        else:
            random_move(board, players[current_player_index])
            current_player_index = (current_player_index + 1) % 2

    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
