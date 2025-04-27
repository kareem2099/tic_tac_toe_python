
from typing import List, Tuple, Optional, Dict, Literal
import random
import time
from dataclasses import dataclass
from game_base import BaseGameLogic

@dataclass
class MoveEvaluation:
    """Represents an evaluated move with score and position."""
    row: int
    col: int
    score: float = 0.0

class AIPlayer:
    """Handles all AI move calculations for different board sizes and difficulties.
    
    Features:
        - Multiple difficulty levels (1-10)
        - Progressive move evaluation
        - Optimized search algorithms
        - Time-limited calculations
    """
    
    def __init__(self, difficulty_level: int = 5) -> None:
        """Initialize AI with difficulty level (1-10).
        
        Args:
            difficulty_level: AI difficulty from 1 (easiest) to 10 (hardest)
            
        Raises:
            ValueError: If difficulty_level is outside 1-10 range
        """
        if not 1 <= difficulty_level <= 10:
            raise ValueError("Difficulty level must be between 1 and 10")
            
        self.difficulty_level = difficulty_level
        self.win_requirements: Dict[int, int] = {
            3: 3,  # 3x3 board
            4: 4,  # 4x4 board
            5: 5,  # 5x5 board
            6: 5   # 6x6 board (slightly easier)
        }
        self.depth_limits: Dict[int, int] = {
            1: 0,   # Level 1: Random moves
            2: 1,    # Level 2: 1-ply lookahead
            3: 1,    # Level 3: 1-ply with better eval
            4: 2,    # Level 4: 2-ply
            5: 2,    # Level 5: 2-ply with better eval
            6: 3,    # Level 6: 3-ply
            7: 4,    # Level 7: 4-ply
            8: 5,    # Level 8: 5-ply
            9: 6,    # Level 9: 6-ply
            10: 7    # Level 10: 7-ply with optimizations
        }
        self.evaluation_cache: Dict[str, float] = {}
        
    def get_move(self, board: List[List[Optional[str]]], current_player: Literal['X', 'O']) -> Tuple[int, int]:
        """Get AI move based on difficulty level (1-10).
        
        Args:
            board: Current game board state
            current_player: The AI's player symbol ('X' or 'O')
            
        Returns:
            Tuple of (row, col) coordinates for the AI's move
            
        Raises:
            ValueError: If board is invalid or current_player is invalid
        """
        if not board or len(board) != len(board[0]):
            raise ValueError("Invalid board dimensions")
        if current_player not in {'X', 'O'}:
            raise ValueError("Player must be 'X' or 'O'")
            
        size = len(board)
        required = self.win_requirements.get(size, 3)
        self.evaluation_cache.clear()  # Clear cache for new move
        
        # Always check for immediate wins/blocks first
        if move := self._get_winning_move(board, current_player, required):
            return move
            
        opponent = 'X' if current_player == 'O' else 'O'
        if move := self._get_winning_move(board, opponent, required):
            return move
            
        # Select strategy based on difficulty level
        if self.difficulty_level == 1:
            return self._get_random_move(board)
        elif self.difficulty_level <= 3:
            return self._get_basic_strategy_move(board, current_player, required)
        elif self.difficulty_level <= 6:
            return self._get_advanced_move(board, current_player, required)
        elif self.difficulty_level <= 8:
            return self._get_expert_move(board, current_player, required)
        else:  # levels 9-10
            return self._get_expert_move(board, current_player, required)

    def _get_random_move(self, board: List[List[Optional[str]]]) -> Tuple[int, int]:
        """Get a completely random valid move.
        
        Args:
            board: Current game board state
            
        Returns:
            Tuple of (row, col) coordinates for a random empty cell
            
        Raises:
            ValueError: If board is full
        """
        size = len(board)
        empty = [(r,c) for r in range(size) for c in range(size) if board[r][c] is None]
        if not empty:
            raise ValueError("No valid moves available - board is full")
        return random.choice(empty)

    def _get_winning_move(self, board: List[List[Optional[str]]], player: Literal['X', 'O'], required: int) -> Optional[Tuple[int, int]]:
        """Check if player can win in next move.
        
        Args:
            board: Current game board state
            player: Player to check ('X' or 'O')
            required: Number in a row needed to win
            
        Returns:
            Winning move coordinates if found, else None
        """
        size = len(board)
        # Check rows first for better cache locality
        for r in range(size):
            for c in range(size):
                if board[r][c] is None:
                    board[r][c] = player
                    if self._check_win(board, player, r, c, required):
                        board[r][c] = None
                        return (r, c)
                    board[r][c] = None
        return None

    def _check_win(self, board: List[List[Optional[str]]], player: str, row: int, col: int, required: int) -> bool:
        """Check if move at (row,col) creates a win"""
        directions = [(0,1),(1,0),(1,1),(1,-1)]
        for dr, dc in directions:
            count = 1
            # Check positive direction
            r, c = row + dr, col + dc
            while 0 <= r < len(board) and 0 <= c < len(board) and board[r][c] == player:
                count += 1
                r += dr
                c += dc
            # Check negative direction
            r, c = row - dr, col - dc
            while 0 <= r < len(board) and 0 <= c < len(board) and board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            if count >= required:
                return True
        return False

    def _get_basic_strategy_move(self, board: List[List[Optional[str]]], player: str, required: int) -> Tuple[int, int]:
        """Basic strategy for difficulty levels 2-3"""
        size = len(board)
        # 50% chance for random move
        if random.random() < 0.5:
            return self._get_random_move(board)
            
        # Try to find good positional moves
        center = size // 2
        if board[center][center] is None:
            return (center, center)
            
        # Look for potential lines
        for r in range(size):
            for c in range(size):
                if board[r][c] is None:
                    board[r][c] = player
                    if self._check_potential(board, player, r, c, required):
                        board[r][c] = None
                        return (r, c)
                    board[r][c] = None
        return self._get_random_move(board)

    def _get_intermediate_move(self, board: List[List[Optional[str]]], player: str, required: int) -> Tuple[int, int]:
        """Intermediate strategy for difficulty levels 4-6"""
        return self._get_advanced_move(board, player, required)

    def _get_advanced_move(self, board: List[List[Optional[str]]], player: str, required: int) -> Tuple[int, int]:
        """Advanced strategy for difficulty levels 7-8"""
        print(f"\nAI {player} calculating move (difficulty level: {self.difficulty_level})")
        print("Current board:")
        for row in board:
            print(" ".join(cell if cell else '.' for cell in row))
            
        size = len(board)
        start_time = time.time()
        max_time = 1.5  # Max seconds to calculate
        
        # Get ordered moves first
        moves = self._get_ordered_moves(board, required)
        best_move = moves[0] if moves else (0, 0)
        
        # Simple evaluation if board is mostly empty
        empty_count = sum(1 for row in board for cell in row if cell is None)
        if empty_count > size*size - 3:
            return best_move
            
        best_score = -float('inf')
        evaluated_moves = 0
        
        for r, c in moves:
            if time.time() - start_time > max_time:
                print(f"Time limit reached after evaluating {evaluated_moves} moves")
                break
                
            if board[r][c] is None:
                board[r][c] = player
                score = self._simple_evaluate(board, player, required)
                board[r][c] = None
                evaluated_moves += 1
                
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
                    if score == 1:  # Winning move found
                        break
        
        return best_move

    def _simple_evaluate(self, board: List[List[Optional[str]]], player: str, required: int) -> int:
        """Fast evaluation of board state"""
        opponent = 'X' if player == 'O' else 'O'
        
        # Check immediate win
        for r in range(len(board)):
            for c in range(len(board)):
                if board[r][c] == player and self._check_win(board, player, r, c, required):
                    return 1
                if board[r][c] == opponent and self._check_win(board, opponent, r, c, required):
                    return -1
                    
        # Count potential lines
        player_potential = sum(1 for r in range(len(board)) for c in range(len(board)) 
                          if board[r][c] is None and self._check_potential(board, player, r, c, required))
        opponent_potential = sum(1 for r in range(len(board)) for c in range(len(board)) 
                            if board[r][c] is None and self._check_potential(board, opponent, r, c, required))
        
        return player_potential - opponent_potential

    def _get_ordered_moves(self, board: List[List[Optional[str]]], required: int) -> List[MoveEvaluation]:
        """Get moves ordered by strategic importance with win potential.
        
        Args:
            board: Current game board state
            required: Number in a row needed to win
            
        Returns:
            List of MoveEvaluation objects sorted by score
        """
        size = len(board)
        center = size // 2
        moves: List[MoveEvaluation] = []
        
        # First check for immediate winning moves for either player
        for player in ['X', 'O']:
            if move := self._get_winning_move(board, player, required):
                return [MoveEvaluation(move[0], move[1], float('inf'))]
        
        # Evaluate all empty cells
        for r in range(size):
            for c in range(size):
                if board[r][c] is None:
                    # Calculate center distance score
                    dist = max(abs(r - center), abs(c - center))
                    center_score = (size - dist) / size
                    
                    # Calculate potential score
                    potential_score = 0
                    for player in ['X', 'O']:
                        board[r][c] = player
                        if self._check_potential(board, player, r, c, required):
                            potential_score += 0.5
                        board[r][c] = None
                    
                    moves.append(MoveEvaluation(
                        row=r,
                        col=c,
                        score=center_score + potential_score
                    ))
        
        # Sort moves by evaluation score and return just the coordinates
        moves.sort(key=lambda m: m.score, reverse=True)
        return [(m.row, m.col) for m in moves]

    def _get_expert_move(self, board: List[List[Optional[str]]], player: str, required: int) -> Tuple[int, int]:
        """Expert strategy for difficulty levels 9-10 with optimizations"""
        size = len(board)
        start_time = time.time()
        max_time = 2.0  # Slightly longer time for expert level
        
        # Use iterative deepening with transposition table
        ordered_moves = self._get_ordered_moves(board, required)
        best_move = ordered_moves[0] if ordered_moves else (0, 0)
        best_score = -float('inf')
        
        for depth in range(1, self.depth_limits[self.difficulty_level] + 1):
            if time.time() - start_time > max_time:
                break
                
            for move in ordered_moves:
                r, c = move  # Unpack tuple directly
                if board[r][c] is None:
                    board[r][c] = player
                    score = -self._negamax(board, depth-1, -float('inf'), float('inf'), 
                                          'X' if player == 'O' else 'O', required)
                    board[r][c] = None
                    
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
                        if score == 1:  # Winning move found
                            return best_move
        return best_move

    def _negamax(self, board: List[List[Optional[str]]], depth: int, alpha: float, beta: float,
                player: str, required: int) -> float:
        """Negamax algorithm with alpha-beta pruning"""
        # Check for terminal state
        if self._check_win(board, 'X' if player == 'O' else 'O', -1, -1, required):
            return -1
        if depth == 0:
            return self._advanced_evaluate(board, player, required)
            
        max_score = -float('inf')
        for move in self._get_ordered_moves(board, required):
            r, c = move  # Unpack tuple directly
            if board[r][c] is None:
                board[r][c] = player
                score = -self._negamax(board, depth-1, -beta, -alpha, 
                                     'X' if player == 'O' else 'O', required)
                board[r][c] = None
                
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if alpha >= beta:
                    break  # Beta cutoff
        return max_score

    def _advanced_evaluate(self, board: List[List[Optional[str]]], player: str, required: int) -> float:
        """Advanced board evaluation considering multiple factors"""
        opponent = 'X' if player == 'O' else 'O'
        score = 0
        
        # Check for immediate wins
        if self._get_winning_move(board, player, required):
            return 1
        if self._get_winning_move(board, opponent, required):
            return -1
            
        # Evaluate board control and potential
        for r in range(len(board)):
            for c in range(len(board)):
                if board[r][c] is None:
                    # Evaluate player's potential
                    board[r][c] = player
                    score += 0.1 * self._count_potential_lines(board, player, required)
                    board[r][c] = None
                    
                    # Evaluate opponent's potential
                    board[r][c] = opponent
                    score -= 0.1 * self._count_potential_lines(board, opponent, required)
                    board[r][c] = None
        return score

    def _count_potential_lines(self, board: List[List[Optional[str]]], player: str, required: int) -> int:
        """Count potential winning lines for player"""
        count = 0
        for r in range(len(board)):
            for c in range(len(board)):
                if board[r][c] is None:
                    board[r][c] = player
                    if self._check_potential(board, player, r, c, required):
                        count += 1
                    board[r][c] = None
        return count

    def _check_potential(self, board: List[List[Optional[str]]], player: str, row: int, col: int, required: int) -> bool:
        """Check if move creates potential winning line"""
        directions = [(0,1),(1,0),(1,1),(1,-1)]
        for dr, dc in directions:
            count = 1
            # Check positive direction
            r, c = row + dr, col + dc
            while 0 <= r < len(board) and 0 <= c < len(board) and (board[r][c] == player or board[r][c] is None):
                count += 1
                r += dr
                c += dc
            # Check negative direction
            r, c = row - dr, col - dc
            while 0 <= r < len(board) and 0 <= c < len(board) and (board[r][c] == player or board[r][c] is None):
                count += 1
                r -= dr
                c -= dc
            if count >= required:
                return True
        return False
