from typing import List, Dict, Tuple, Optional
from ai import AIPlayer

class GameLogic:
    """Handles all game logic including board operations and win checking."""
    
    def __init__(self, difficulty='medium'):
        """Initialize the game with specified difficulty."""
        from game_manager import GameManager
        self.manager = GameManager(difficulty)
        self.difficulty = difficulty
        self.difficulty_descriptions = {
            'easy': "3x3 board (3 in a row to win)",
            'medium': "4x4 board (4 in a row to win)",
            'hard': "5x5 board (5 in a row to win)", 
            'insane': "6x6 board (6 in a row to win)"
        }
        
    def check_winner(self, board: List[List[Optional[str]]], player: str) -> bool:
        """Check if the specified player has won."""
        size = len(board)
        directions = [
            (0, 1),  # Horizontal
            (1, 0),  # Vertical
            (1, 1),  # Diagonal \
            (1, -1)  # Diagonal /
        ]
        
        # Check all possible winning lines
        for r in range(size):
            for c in range(size):
                if board[r][c] == player:
                    for dr, dc in directions:
                        count = 1
                        cells = [(r, c)]
                        
                        # Check positive direction
                        nr, nc = r + dr, c + dc
                        while 0 <= nr < size and 0 <= nc < size and board[nr][nc] == player:
                            count += 1
                            cells.append((nr, nc))
                            nr += dr
                            nc += dc
                            
                        # Check negative direction
                        nr, nc = r - dr, c - dc
                        while 0 <= nr < size and 0 <= nc < size and board[nr][nc] == player:
                            count += 1
                            cells.append((nr, nc))
                            nr -= dr
                            nc -= dc
                            
                        # Check win condition based on difficulty
                        required = {
                            'easy': 3,
                            'medium': 4, 
                            'hard': 5,
                            'insane': 6
                        }.get(self.difficulty, 3)
                        
                        if count >= required:
                            self.manager.game.winner = player
                            self.manager.game.game_over = True
                            self.manager.game.winning_cells = cells
                            return True
        return False

    def get_win_positions(self, board: List[List[Optional[str]]], player: str) -> List[Tuple[int, int]]:
        """Get the winning positions for the specified player."""
        if self.manager.game.winner == player:
            return self.manager.game.winning_cells
        return []

    def is_draw(self, board: List[List[Optional[str]]]) -> bool:
        """Check if the game is a draw."""
        return self.manager.game.check_draw()

    def get_ai_move(self, board: List[List[Optional[str]]]) -> Tuple[int, int]:
        """Calculate AI move using the AIPlayer class"""
        ai_player = AIPlayer(self.difficulty)
        return ai_player.get_move(board, "O")
