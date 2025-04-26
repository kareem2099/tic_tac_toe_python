from game_base import BaseGameLogic

class HardGame(BaseGameLogic):
    """5x5 Tic-Tac-Toe game logic (5 in a row to win)"""
    
    def __init__(self):
        super().__init__(size=5)
        
    def check_win(self, row: int, col: int) -> bool:
        """Check for 5 in a row/column/diagonal in 5x5 grid"""
        player = self.board[row][col]
        directions = [
            (0, 1),  # Horizontal
            (1, 0),  # Vertical
            (1, 1),  # Diagonal \
            (1, -1)  # Diagonal /
        ]
        
        for dr, dc in directions:
            count = 1
            cells = [(row, col)]
            
            # Check in positive direction
            r, c = row + dr, col + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                cells.append((r, c))
                r += dr
                c += dc
                
            # Check in negative direction
            r, c = row - dr, col - dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                cells.append((r, c))
                r -= dr
                c -= dc
                
            if count >= 5:
                self.winning_cells = cells
                return True
                
        return False
