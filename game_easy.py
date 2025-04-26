from game_base import BaseGameLogic

class EasyGame(BaseGameLogic):
    """3x3 Tic-Tac-Toe game logic"""
    
    def __init__(self):
        super().__init__(size=3)
        
    def check_win(self, row: int, col: int) -> bool:
        """Check for win in 3x3 grid"""
        player = self.board[row][col]
        
        # Check row
        if all(self.board[row][c] == player for c in range(self.size)):
            self.winning_cells = [(row, c) for c in range(self.size)]
            return True
            
        # Check column
        if all(self.board[r][col] == player for r in range(self.size)):
            self.winning_cells = [(r, col) for r in range(self.size)]
            return True
            
        # Check diagonals
        if row == col and all(self.board[i][i] == player for i in range(self.size)):
            self.winning_cells = [(i, i) for i in range(self.size)]
            return True
            
        if row + col == self.size - 1 and all(self.board[i][self.size-1-i] == player for i in range(self.size)):
            self.winning_cells = [(i, self.size-1-i) for i in range(self.size)]
            return True
            
        return False
