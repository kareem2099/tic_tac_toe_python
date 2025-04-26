from game_easy import EasyGame
from game_medium import MediumGame
from game_hard import HardGame
from game_insane import InsaneGame

from typing import List, Optional, Tuple

class GameManager:
    """Manages different game difficulty levels"""
    
    DIFFICULTIES = {
        'easy': EasyGame,
        'medium': MediumGame,
        'hard': HardGame,
        'insane': InsaneGame
    }
    
    def __init__(self, difficulty='easy'):
        self.set_difficulty(difficulty)
        self.last_move = (-1, -1)  # Track last move coordinates
        
    def set_difficulty(self, difficulty: str):
        """Change the current game difficulty"""
        if difficulty not in self.DIFFICULTIES:
            raise ValueError(f"Invalid difficulty: {difficulty}")
        self.game = self.DIFFICULTIES[difficulty]()
        
    def get_board_size(self) -> int:
        """Get current board size"""
        return self.game.size
        
    def make_move(self, row: int, col: int) -> bool:
        """Make a move on the board"""
        success = self.game.make_move(row, col)
        if success:
            self.last_move = (row, col)
        return success
        
    def get_board(self) -> List[List[Optional[str]]]:
        """Get current board state"""
        return self.game.board
        
    def get_current_player(self) -> str:
        """Get current player"""
        return self.game.current_player
        
    def is_game_over(self) -> bool:
        """Check if game is over"""
        return self.game.game_over
        
    def get_winner(self) -> Optional[str]:
        """Get game winner"""
        return self.game.winner
        
    def get_winning_cells(self) -> List[Tuple[int, int]]:
        """Get winning cell positions"""
        return self.game.winning_cells
        
    def get_last_move(self) -> Tuple[int, int]:
        """Get coordinates of last move made"""
        return self.last_move
        
    def reset(self) -> None:
        """Reset the game"""
        self.game.reset()
