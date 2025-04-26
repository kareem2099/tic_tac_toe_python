import ai
import time
from typing import List, Tuple, Optional

def test_ai_level(level: int, board_size: int = 3, games: int = 5):
    """Test AI at specific difficulty level"""
    print(f"\nTesting AI level {level} on {board_size}x{board_size} board")
    ai_player = ai.AIPlayer(difficulty_level=level)
    
    for game in range(games):
        board = [[None for _ in range(board_size)] for _ in range(board_size)]
        player = 'X'
        
        print(f"\nGame {game+1}:")
        start_time = time.time()
        
        while True:
            # AI move
            r, c = ai_player.get_move(board, player)
            board[r][c] = player
            print(f"AI {player} move: ({r},{c})")
            print_board(board)
            
            # Check win
            if ai_player._check_win(board, player, r, c, board_size):
                print(f"AI {player} wins!")
                break
                
            # Check draw
            if all(cell is not None for row in board for cell in row):
                print("Draw!")
                break
                
            player = 'O' if player == 'X' else 'X'
            
        print(f"Game completed in {time.time()-start_time:.2f} seconds")

def print_board(board: List[List[Optional[str]]]):
    """Print the current board state"""
    for row in board:
        print(" ".join(cell if cell else '.' for cell in row))
    print()

if __name__ == "__main__":
    # Test all difficulty levels from 1 to 10
    for level in range(1, 11):
        test_ai_level(level)
