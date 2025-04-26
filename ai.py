
from typing import List, Tuple, Optional
import random
import time
from game_base import BaseGameLogic

class AIPlayer:
    """Handles all AI move calculations for different board sizes and difficulties"""
    
    def __init__(self, difficulty_level: int = 5):
        """Initialize AI with difficulty level (1-10)"""
        self.difficulty_level = min(max(difficulty_level, 1), 10)
        self.win_requirements = {
            3: 3,  # 3x3 board
            4: 4,  # 4x4 board
            5: 5,  # 5x5 board
            6: 5   # 6x6 board (slightly easier)
        }
        # Difficulty parameters
        self.depth_limits = {
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
        
    def get_move(self, board: List[List[Optional[str]]], current_player: str) -> Tuple[int, int]:
        """Get AI move based on difficulty level (1-10)"""
        size = len(board)
        required = self.win_requirements.get(size, 3)
        
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
            return self._get_intermediate_move(board, current_player, required)
        elif self.difficulty_level <= 8:
            return self._get_advanced_move(board, current_player, required)
        else:  # levels 9-10
            return self._get_expert_move(board, current_player, required)

    def _get_random_move(self, board: List[List[Optional[str]]]) -> Tuple[int, int]:
        """Get a completely random valid move"""
        size = len(board)
        empty = [(r,c) for r in range(size) for c in range(size) if board[r][c] is None]
        return random.choice(empty) if empty else (0, 0)

    def _get_winning_move(self, board: List[List[Optional[str]]], player: str, required: int) -> Optional[Tuple[int, int]]:
        """Check if player can win in next move"""
        size = len(board)
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
        size = len(board)
        # Prefer center and corners
        corners = [(0,0),(0,size-1),(size-1,0),(size-1,size-1)]
        for r, c in corners:
            if board[r][c] is None:
                return (r, c)
                
        center = size // 2
        if board[center][center] is None:
            return (center, center)
            
        return self._get_minimax_move(board, player, required)

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

    def _get_ordered_moves(self, board: List[List[Optional[str]]], required: int) -> List[Tuple[int, int]]:
        """Get moves ordered by strategic importance with win potential"""
        size = len(board)
        center = size // 2
        moves = []
        
        # First check for immediate winning moves
        for r in range(size):
            for c in range(size):
                if board[r][c] is None:
                    board[r][c] = 'X'  # Check both players
                    if self._check_win(board, 'X', r, c, required):
                        board[r][c] = None
                        return [(r, c)]  # Return immediately if found
                    board[r][c] = None
        
        # Then prioritize center and strategic positions
        for distance in range(0, center + 1):
            for r in range(size):
                for c in range(size):
                    if board[r][c] is None:
                        # Calculate strategic value (center + potential)
                        dist = max(abs(r - center), abs(c - center))
                        potential = 0
                        # Check if move creates potential line
                        board[r][c] = 'X'
                        if self._check_potential(board, 'X', r, c, required):
                            potential = 1
                        board[r][c] = None
                        moves.append((r, c, -distance, potential))
        
        # Sort by strategic value (center first, then potential)
        moves.sort(key=lambda x: (x[2], x[3]), reverse=True)
        return [(r, c) for r, c, _, _ in moves]

    def _get_expert_move(self, board: List[List[Optional[str]]], player: str, required: int) -> Tuple[int, int]:
        """Expert strategy for difficulty levels 9-10 with optimizations"""
        size = len(board)
        start_time = time.time()
        max_time = 2.0  # Slightly longer time for expert level
        
        # Use iterative deepening with transposition table
        best_move = self._get_ordered_moves(board, required)[0] if board else (0, 0)
        best_score = -float('inf')
        
        for depth in range(1, self.depth_limits[self.difficulty_level] + 1):
            if time.time() - start_time > max_time:
                break
                
            for r in range(size):
                for c in range(size):
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
        for r, c in self._get_ordered_moves(board, required):
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
