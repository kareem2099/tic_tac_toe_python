import tkinter as tk
from typing import List, Dict, Optional, Tuple, Literal
from dataclasses import dataclass
from game_history import GameHistory

@dataclass
class PlayerStats:
    """Tracks comprehensive player statistics.
    
    Attributes:
        wins: Number of games won
        losses: Number of games lost
        draws: Number of games drawn
        win_streak: Current consecutive wins
        max_streak: Highest win streak achieved
        first_move_win: Wins when player moved first
    """
    wins: int = 0
    losses: int = 0
    draws: int = 0
    win_streak: int = 0
    max_streak: int = 0
    first_move_win: int = 0

class PlayerManager:
    """Manages all player-related data and statistics.
    
    Features:
        - Player profile management
        - Score tracking
        - Game history recording
        - Statistics analysis
        - Streak tracking
    
    Attributes:
        player1: Name of first player (X)
        player2: Name of second player (O) 
        scores: Dictionary mapping player names to scores
        stats: Dictionary mapping player names to PlayerStats
        history: GameHistory instance for recording games
        mode: Current game mode ('pvp' or 'ai')
        _last_winner: Cache of last game winner
    """
    
    def __init__(self) -> None:
        """Initialize player data and game history."""
        self.player1 = "Player 1"
        self.player2 = "Player 2"
        self.scores: Dict[str, int] = {self.player1: 0, self.player2: 0}
        self.stats: Dict[str, PlayerStats] = {
            self.player1: PlayerStats(),
            self.player2: PlayerStats()
        }
        self.history = GameHistory()
        self.mode: Literal['pvp', 'ai'] = 'pvp'
        self.game_start_time: Optional[int] = None
        self.move_count: int = 0
        self._last_winner: Optional[str] = None

    def set_players(self, player1: str, player2: str, mode: Literal['pvp', 'ai'] = "pvp") -> None:
        """Set player names, game mode and reset scores.
        
        Args:
            player1: Name for Player 1 (X)
            player2: Name for Player 2 (O)
            mode: Game mode ('pvp' or 'ai')
            
        Raises:
            ValueError: If player names are empty after stripping
        """
        p1 = player1.strip() if player1 else "Player 1"
        p2 = player2.strip() if player2 else "Player 2"
        
        if not p1 or not p2:
            raise ValueError("Player names cannot be empty")
            
        self.player1 = p1
        self.player2 = p2
        self.mode = mode
        
        # Initialize scores and stats
        self.scores = {self.player1: 0, self.player2: 0}
        self.stats = {
            self.player1: PlayerStats(),
            self.player2: PlayerStats()
        }

    def record_game_result(self, result: str, window: tk.Tk, board: List[List[Optional[str]]]) -> None:
        """Record game results in history.
        
        Args:
            result: The game result (player name or 'Draw')
            window: The tkinter window for timestamp purposes
            board: The current game board state
            
        Raises:
            ValueError: If result is invalid
        """
        if result not in {self.player1, self.player2, "Draw"}:
            raise ValueError(f"Invalid game result: {result}")
            
        # Track moves in the order they were played
        moves = []
        size = len(board)
        # Create a list of all moves with coordinates
        all_moves = [
            (row, col, board[row][col])
            for row in range(size)
            for col in range(size)
            if board[row][col] is not None
        ]
        # Sort moves by player to reconstruct sequence
        x_moves = [(r,c) for r,c,p in all_moves if p == "X"]
        o_moves = [(r,c) for r,c,p in all_moves if p == "O"]
        
        # Interleave moves in play order
        for turn, (row, col) in enumerate(zip(x_moves, o_moves), 1):
            moves.append({"row": row[0], "col": row[1], "player": "X", "turn": turn*2-1})
            moves.append({"row": col[0], "col": col[1], "player": "O", "turn": turn*2})
        
        # Handle odd number of moves
        if len(x_moves) > len(o_moves):
            row, col = x_moves[-1]
            moves.append({"row": row, "col": col, "player": "X", "turn": len(moves)+1})
        
        self.history.add_game(
            player1=self.player1,
            player2=self.player2,
            winner=result if result != "Draw" else None,
            moves=moves,
            game_type="pvp" if self.mode == "pvp" else "pvc"
        )

    def update_score(self, winner: str) -> None:
        """Update player scores and statistics based on game result.
        
        Args:
            winner: The winning player (name) or 'Draw'
            
        Raises:
            ValueError: If winner is not a valid player or 'Draw'
        """
        if winner == "Draw":
            self.stats[self.player1].draws += 1
            self.stats[self.player2].draws += 1
            # Reset streaks on draw
            self.stats[self.player1].win_streak = 0
            self.stats[self.player2].win_streak = 0
        elif winner in {self.player1, self.player2}:
            self.scores[winner] += 1
            winner_stats = self.stats[winner]
            winner_stats.wins += 1
            winner_stats.win_streak += 1
            
            # Update max streak if needed
            if winner_stats.win_streak > winner_stats.max_streak:
                winner_stats.max_streak = winner_stats.win_streak
                
            # Update loser stats
            loser = self.player2 if winner == self.player1 else self.player1
            loser_stats = self.stats[loser]
            loser_stats.losses += 1
            loser_stats.win_streak = 0
            
            # Track if winner moved first
            if self._last_winner != winner:
                winner_stats.first_move_win += 1
                
            self._last_winner = winner
        else:
            raise ValueError(f"Invalid winner: {winner}")

    def show_history(self, window: tk.Tk) -> None:
        """Display enhanced game history with animations and replay.
        
        Args:
            window: The parent tkinter window
        """
        from history_viewer import HistoryViewer
        history = self.history.get_all_history()
        if not history:
            no_history = tk.Toplevel(window)
            no_history.title("Game History")
            tk.Label(no_history, text="No games played yet", pady=20).pack()
            return
            
        # Launch enhanced history viewer
        HistoryViewer(window, history)

    def get_score_text(self) -> str:
        """Generate detailed score display text with stats.
        
        Returns:
            Formatted string showing:
            - Player names and symbols
            - Current scores
            - Win/loss/draw stats
        """
        p1_stats = self.stats[self.player1]
        p2_stats = self.stats[self.player2]
        
        return (
            f"{self.player1} (X): {self.scores[self.player1]} "
            f"[W{p1_stats.wins} L{p1_stats.losses} D{p1_stats.draws}]\n"
            f"{self.player2} (O): {self.scores[self.player2]} "
            f"[W{p2_stats.wins} L{p2_stats.losses} D{p2_stats.draws}]"
        )
