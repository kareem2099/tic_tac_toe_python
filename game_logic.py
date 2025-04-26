from typing import List, Dict, Tuple, Optional
import random

class GameLogic:
    """Handles all game logic including board operations, win checking, and AI moves."""
    
    def __init__(self):
        """Initialize the game board."""
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.difficulty = 5  # Default medium difficulty
        self.difficulty_descriptions = {
            1: "Very Easy: Makes random moves, often loses",
            2: "Easy: Occasionally blocks wins",
            3: "Novice: Blocks wins but poor strategy",
            4: "Beginner: Basic strategy with mistakes",
            5: "Medium: Balanced play with some mistakes",
            6: "Intermediate: Good strategy, few mistakes",
            7: "Advanced: Strong play, rare mistakes",
            8: "Expert: Near-perfect play",
            9: "Master: Almost perfect play",
            10: "Unbeatable: Perfect minimax AI"
        }
        
    def check_winner(self, board: List[List[Optional[str]]], player: str) -> bool:
        """Check if the specified player has won."""
        # Check rows
        for row in board:
            if all(cell == player for cell in row):
                return True
        # Check columns
        for col in range(3):
            if all(board[row][col] == player for row in range(3)):
                return True
        # Check diagonals
        if all(board[i][i] == player for i in range(3)):
            return True
        if all(board[i][2-i] == player for i in range(3)):
            return True
        return False

    def get_win_positions(self, board: List[List[Optional[str]]], player: str) -> List[Tuple[int, int]]:
        """Get the winning positions for the specified player."""
        # Check rows
        for row in range(3):
            if all(board[row][col] == player for col in range(3)):
                return [(row, col) for col in range(3)]
        # Check columns
        for col in range(3):
            if all(board[row][col] == player for row in range(3)):
                return [(row, col) for row in range(3)]
        # Check diagonals
        if all(board[i][i] == player for i in range(3)):
            return [(i, i) for i in range(3)]
        if all(board[i][2-i] == player for i in range(3)):
            return [(i, 2-i) for i in range(3)]
        return []

    def is_draw(self, board: List[List[Optional[str]]]) -> bool:
        """Check if the game is a draw.
        
        Args:
            board: The current game board
            
        Returns:
            True if the board is full with no winner, False otherwise
        """
        return all(board[r][c] is not None for r in range(3) for c in range(3))

    def minimax(self, board: List[List[Optional[str]]], is_maximizing: bool, depth: int = 0, alpha: float = -float('inf'), beta: float = float('inf')) -> int:
        """Optimized minimax algorithm with alpha-beta pruning.
        
        Args:
            board: The current game board
            is_maximizing: Whether the AI is maximizing (True) or minimizing (False)
            depth: Current recursion depth (used for difficulty scaling)
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            
        Returns:
            The best score for the current board state
        """
        if self.check_winner(board, "O"):
            return 1
        if self.check_winner(board, "X"):
            return -1
        if self.is_draw(board):
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] is None:
                        board[r][c] = "O"
                        score = self.minimax(board, False, depth+1, alpha, beta)
                        board[r][c] = None
                        best_score = max(score, best_score)
                        alpha = max(alpha, best_score)
                        if beta <= alpha:
                            break  # Beta cutoff
            return best_score
        else:
            best_score = float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] is None:
                        board[r][c] = "X"
                        score = self.minimax(board, True, depth+1, alpha, beta)
                        board[r][c] = None
                        best_score = min(score, best_score)
                        beta = min(beta, best_score)
                        if beta <= alpha:
                            break  # Alpha cutoff
            return best_score

    def _get_random_move(self, board: List[List[Optional[str]]]) -> Tuple[int, int]:
        """Get a random valid move."""
        empty = [(r,c) for r in range(3) for c in range(3) if board[r][c] is None]
        return random.choice(empty) if empty else (0, 0)

    def _get_winning_move(self, board: List[List[Optional[str]]]) -> Optional[Tuple[int, int]]:
        """Check if AI can win immediately."""
        for r in range(3):
            for c in range(3):
                if board[r][c] is None:
                    board[r][c] = "O"
                    if self.check_winner(board, "O"):
                        board[r][c] = None
                        return (r, c)
                    board[r][c] = None
        return None

    def _get_blocking_move(self, board: List[List[Optional[str]]]) -> Optional[Tuple[int, int]]:
        """Check if need to block player's win."""
        for r in range(3):
            for c in range(3):
                if board[r][c] is None:
                    board[r][c] = "X"
                    if self.check_winner(board, "X"):
                        board[r][c] = None
                        return (r, c)
                    board[r][c] = None
        return None

    def _get_minimax_move(self, board: List[List[Optional[str]]]) -> Tuple[int, int]:
        """Get optimal move using minimax."""
        best_score = -float('inf')
        best_move = None
        
        for r in range(3):
            for c in range(3):
                if board[r][c] is None:
                    board[r][c] = "O"
                    score = self.minimax(board, False)
                    board[r][c] = None
                    
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
        return best_move or (0, 0)

    def get_ai_move(self, board: List[List[Optional[str]]]) -> Tuple[int, int]:
        """Calculate AI move based on difficulty level."""
        # Level 1-2: Random moves
        if self.difficulty <= 2:
            return self._get_random_move(board)

        # Level 3-4: Block wins sometimes
        if self.difficulty <= 4:
            if random.random() < 0.5:
                return self._get_random_move(board)
            if block := self._get_blocking_move(board):
                return block
            return self._get_random_move(board)

        # Level 5-7: Block wins and sometimes win
        if self.difficulty <= 7:
            if win := self._get_winning_move(board):
                return win
            if block := self._get_blocking_move(board):
                return block
            if random.random() < 0.7:
                return self._get_minimax_move(board)
            return self._get_random_move(board)

        # Level 8-10: Mostly perfect play
        return self._get_minimax_move(board)
