from typing import List, Optional, Tuple

class BaseGameLogic:
    """Base class for all game difficulty levels"""
    
    def __init__(self, size: int = 3):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.current_player = "X"
        self.game_over = False
        self.winner = None
        self.winning_cells = []
        
    def reset(self) -> None:
        """Reset the game board"""
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = "X"
        self.game_over = False
        self.winner = None
        self.winning_cells = []
        
    def make_move(self, row: int, col: int) -> bool:
        """Make a move on the board"""
        if self.game_over or self.board[row][col] is not None:
            return False
            
        self.board[row][col] = self.current_player
        if self.check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
        elif self.check_draw():
            self.game_over = True
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
        return True
        
    def check_win(self, row: int, col: int) -> bool:
        """Check if the last move resulted in a win"""
        # To be implemented in child classes
        raise NotImplementedError
        
    def check_draw(self) -> bool:
        """Check if the game is a draw"""
        return all(cell is not None for row in self.board for cell in row)
        
    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Get list of valid moves"""
        return [(r, c) for r in range(self.size) 
                      for c in range(self.size) 
                      if self.board[r][c] is None]
