from typing import List, Dict, Tuple, Optional, Literal, Set
from dataclasses import dataclass
from ai import AIPlayer

@dataclass
class WinResult:
    """Stores information about a winning condition."""
    winner: Optional[Literal['X', 'O']]
    cells: List[Tuple[int, int]]
    direction: Literal['horizontal', 'vertical', 'diagonal']

class GameLogic:
    """Handles all game logic including board operations and win checking.
    
    Features:
        - Win condition checking
        - Draw detection
        - Move validation
        - Board state management
    """
    
    def __init__(self, difficulty: int = 5) -> None:
        """Initialize the game with specified difficulty.
        
        Args:
            difficulty: Integer from 1 (easiest) to 10 (hardest)
        
        Raises:
            ValueError: If difficulty is outside 1-10 range
        """
        if not 1 <= difficulty <= 10:
            raise ValueError("Difficulty must be between 1 and 10")
            
        from game_manager import GameManager
        # Map numeric difficulty to board size
        board_size = {
            1: 3, 2: 3, 3: 3, 4: 4, 5: 4,
            6: 5, 7: 5, 8: 6, 9: 6, 10: 6
        }.get(difficulty, 4)
        
        # Map numeric difficulty to old string names for GameManager
        difficulty_map = {
            1: 'easy', 2: 'easy', 3: 'easy',
            4: 'medium', 5: 'medium',
            6: 'hard', 7: 'hard',
            8: 'insane', 9: 'insane', 10: 'insane'
        }
        self.manager = GameManager(difficulty_map.get(difficulty, 'medium'))
        self.difficulty = difficulty
        self.difficulty_descriptions = {
            1: "3x3 board (3 in a row to win) - Very Easy",
            2: "3x3 board (3 in a row to win) - Easy",
            3: "3x3 board (3 in a row to win) - Medium",
            4: "4x4 board (4 in a row to win) - Easy",
            5: "4x4 board (4 in a row to win) - Medium",
            6: "5x5 board (5 in a row to win) - Hard",
            7: "5x5 board (5 in a row to win) - Very Hard",
            8: "6x6 board (6 in a row to win) - Hard",
            9: "6x6 board (6 in a row to win) - Very Hard",
            10: "6x6 board (6 in a row to win) - Expert"
        }
        
    def check_winner(self, board: List[List[Optional[Literal['X', 'O']]]], player: Literal['X', 'O']) -> bool:
        """Check if the specified player has won.
        
        Args:
            board: Current game board state
            player: Player symbol ('X' or 'O') to check
            
        Returns:
            bool: True if player has won, False otherwise
            
        Raises:
            ValueError: If board is invalid or player symbol is invalid
        """
        if not board or len(board) != len(board[0]):
            raise ValueError("Invalid board dimensions")
        if player not in {'X', 'O'}:
            raise ValueError("Player must be 'X' or 'O'")
            
        size = len(board)
        # Get required in-a-row based on board size
        size = len(board)
        required = {
            3: 3,  # 3x3 board
            4: 4,  # 4x4 board
            5: 5,  # 5x5 board
            6: 5   # 6x6 board (slightly easier)
        }.get(size, 3)
        
        # Only check rows/columns that could possibly contain a win
        for r in range(size):
            for c in range(size):
                if board[r][c] == player:
                    # Check horizontal
                    if c <= size - required:
                        if all(board[r][c+i] == player for i in range(required)):
                            self._set_winner(player, [(r, c+i) for i in range(required)])
                            return True
                    
                    # Check vertical
                    if r <= size - required:
                        if all(board[r+i][c] == player for i in range(required)):
                            self._set_winner(player, [(r+i, c) for i in range(required)])
                            return True
                    
                    # Check diagonal \
                    if r <= size - required and c <= size - required:
                        if all(board[r+i][c+i] == player for i in range(required)):
                            self._set_winner(player, [(r+i, c+i) for i in range(required)])
                            return True
                    
                    # Check diagonal /
                    if r <= size - required and c >= required - 1:
                        if all(board[r+i][c-i] == player for i in range(required)):
                            self._set_winner(player, [(r+i, c-i) for i in range(required)])
                            return True
        return False

    def _set_winner(self, player: str, cells: List[Tuple[int, int]]) -> None:
        """Helper method to set winner state in game manager."""
        self.manager.game.winner = player
        self.manager.game.game_over = True
        self.manager.game.winning_cells = cells

    def get_win_positions(self, board: List[List[Optional[Literal['X', 'O']]]], player: Literal['X', 'O']) -> List[Tuple[int, int]]:
        """Get the winning positions for the specified player.
        
        Args:
            board: Current game board state
            player: Player symbol ('X' or 'O') to check
            
        Returns:
            List of (row, col) tuples representing winning positions
            
        Raises:
            ValueError: If board is invalid or player symbol is invalid
        """
        if not board or len(board) != len(board[0]):
            raise ValueError("Invalid board dimensions")
        if player not in {'X', 'O'}:
            raise ValueError("Player must be 'X' or 'O'")
            
        if hasattr(self.manager, 'game') and self.manager.game.winner == player:
            return self.manager.game.winning_cells
        return []

    def is_draw(self, board: List[List[Optional[str]]]) -> bool:
        """Check if the game is a draw."""
        return self.manager.game.check_draw()

    def get_ai_move(self, board: List[List[Optional[Literal['X', 'O']]]]) -> Tuple[int, int]:
        """Calculate AI move using the AIPlayer class.
        
        Args:
            board: Current game board state
            
        Returns:
            Tuple[int, int]: Row and column of AI move
            
        Raises:
            ValueError: If board is invalid or full
            RuntimeError: If AI move calculation fails
        """
        if not board or not all(len(row) == len(board) for row in board):
            raise ValueError("Invalid board dimensions")
            
        if all(cell is not None for row in board for cell in row):
            raise ValueError("Board is full")
            
        ai_player = AIPlayer(self.difficulty)
        return ai_player.get_move(board, "O")
