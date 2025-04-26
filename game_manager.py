from __future__ import annotations
from typing import List, Optional, Tuple, Dict, Type, Literal
from dataclasses import dataclass, field
from game_easy import EasyGame
from game_medium import MediumGame
from game_hard import HardGame
from game_insane import InsaneGame

@dataclass
class Move:
    """Represents a game move with validation.
    
    Attributes:
        row: Row index (0-based)
        col: Column index (0-based)
    """
    row: int
    col: int
    
    def __post_init__(self):
        """Validate move coordinates.
        
        Raises:
            ValueError: If coordinates are invalid
        """
        if self.row < 0 or self.col < 0:
            raise ValueError("Move coordinates cannot be negative")
        if not isinstance(self.row, int) or not isinstance(self.col, int):
            raise ValueError("Move coordinates must be integers")

@dataclass
class GameState:
    """Tracks complete game state for undo/redo functionality."""
    board: List[List[Optional[Literal['X', 'O']]]]
    current_player: Literal['X', 'O']
    game_over: bool
    winner: Optional[Literal['X', 'O']]
    winning_cells: List[Tuple[int, int]]

class GameManager:
    """Manages different game difficulty levels and game state.
    
    Features:
        - Difficulty level management
        - Move validation and tracking
        - Game state persistence
        - Undo/redo functionality
    
    Attributes:
        DIFFICULTIES: Mapping of difficulty names to game classes
        game: Current game instance
        last_move: Coordinates of last valid move
        _state_history: Stack of game states for undo
    """
    
    DIFFICULTIES: Dict[str, Type[GameBase]] = {
        'easy': EasyGame,
        'medium': MediumGame, 
        'hard': HardGame,
        'insane': InsaneGame
    }
    _state_history: List[GameState] = field(default_factory=list)
    
    def __init__(self, difficulty: str = 'easy') -> None:
        """Initialize game manager with specified difficulty.
        
        Args:
            difficulty: One of 'easy', 'medium', 'hard', or 'insane'
            
        Raises:
            ValueError: If invalid difficulty is provided
        """
        self._validate_difficulty(difficulty)
        self.game = self.DIFFICULTIES[difficulty]()
        self.last_move: Optional[Move] = None  # No initial move
        
    def _validate_difficulty(self, difficulty: str) -> None:
        """Validate difficulty level."""
        if difficulty not in self.DIFFICULTIES:
            raise ValueError(f"Invalid difficulty: {difficulty}. Must be one of {list(self.DIFFICULTIES.keys())}")
        
    def set_difficulty(self, difficulty: str) -> None:
        """Change the current game difficulty.
        
        Args:
            difficulty: One of 'easy', 'medium', 'hard', or 'insane'
            
        Raises:
            ValueError: If invalid difficulty is provided
        """
        self._validate_difficulty(difficulty)
        self.game = self.DIFFICULTIES[difficulty]()
        self.last_move = None  # Reset last move
        
    def get_board_size(self) -> int:
        """Get current board size"""
        return self.game.size
        
    def make_move(self, row: int, col: int) -> bool:
        """Make a move on the board.
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            
        Returns:
            bool: True if move was successful, False otherwise
            
        Raises:
            ValueError: If coordinates are invalid
            RuntimeError: If game state update fails
        """
        try:
            # Save current state for possible undo
            self._save_state()
            
            move = Move(row, col)
            success = self.game.make_move(move.row, move.col)
            if success:
                self.last_move = move
            return success
        except Exception as e:
            self._restore_state()
            raise RuntimeError(f"Move failed: {str(e)}") from e
        
    def get_board(self) -> List[List[Optional[str]]]:
        """Get current board state.
        
        Returns:
            List[List[Optional[str]]]: Deep copy of current board state
        """
        return [row.copy() for row in self.game.board]
        
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
        
    def get_last_move(self) -> Optional[Tuple[int, int]]:
        """Get coordinates of last move made
        
        Returns:
            Tuple[int, int] if move exists, None otherwise
        """
        return self.last_move if self.last_move else None
        
    def reset(self) -> None:
        """Reset the game state.
        
        Resets:
            - Game board
            - Current player
            - Game over status
            - Winner status
            - Last move tracking
        """
        self.game.reset()
        self.last_move = Move(-1, -1)
