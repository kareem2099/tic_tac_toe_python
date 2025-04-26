import tkinter as tk
from typing import List, Dict, Optional
from game_history import GameHistory

class PlayerManager:
    """Handles player information, scores, and game history."""
    
    def __init__(self):
        """Initialize player data and game history."""
        self.player1 = "Player 1"
        self.player2 = "Player 2"
        self.scores = {self.player1: 0, self.player2: 0}
        self.history = GameHistory()
        self.game_start_time = None
        self.move_count = 0

    def set_players(self, player1: str, player2: str, mode: str = "pvp") -> None:
        """Set player names, game mode and reset scores.
        
        Args:
            player1: Name for Player 1 (X)
            player2: Name for Player 2 (O)
            mode: Game mode ('pvp' or 'ai')
            
        Features:
            - Validates player names
            - Tracks player stats
            - Handles AI player specially
        """
        self.player1 = player1.strip() if player1 else "Player 1"
        self.player2 = player2.strip() if player2 else "Player 2"
        self.mode = mode
        
        # Initialize scores and stats
        self.scores = {self.player1: 0, self.player2: 0}
        self.stats = {
            self.player1: {"wins": 0, "losses": 0, "draws": 0},
            self.player2: {"wins": 0, "losses": 0, "draws": 0}
        }

    def record_game_result(self, result: str, window: tk.Tk, board: List[List[Optional[str]]]) -> None:
        """Record game results in history.
        
        Args:
            result: The game result ('Player 1', 'Player 2', or 'Draw')
            window: The tkinter window for timestamp purposes
            board: The current game board state
        """
        # Track moves in the order they were played
        moves = []
        move_count = 0
        # Create a temporary board to track move sequence
        temp_board = [[None for _ in range(3)] for _ in range(3)]
        # Reconstruct move sequence by comparing boards
        for turn in range(1, 10):
            for row in range(3):
                for col in range(3):
                    if board[row][col] != temp_board[row][col] and board[row][col] is not None:
                        moves.append({
                            "row": row,
                            "col": col,
                            "player": board[row][col],
                            "turn": turn
                        })
                        temp_board[row][col] = board[row][col]
                        move_count += 1
                        break  # Only one move per turn
                else:
                    continue
                break
        
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
            winner: The winning player ('Player 1', 'Player 2') or 'Draw'
            
        Features:
            - Updates scores
            - Maintains win/loss/draw stats
            - Handles draws specially
        """
        if winner == "Draw":
            if self.player1 in self.stats:
                self.stats[self.player1]["draws"] += 1
            if self.player2 in self.stats:
                self.stats[self.player2]["draws"] += 1
        elif winner in self.scores:
            self.scores[winner] += 1
            if winner in self.stats:
                self.stats[winner]["wins"] += 1
            loser = self.player2 if winner == self.player1 else self.player1
            if loser in self.stats:
                self.stats[loser]["losses"] += 1

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
        p1_stats = self.stats.get(self.player1, {})
        p2_stats = self.stats.get(self.player2, {})
        
        return (
            f"{self.player1} (X): {self.scores[self.player1]} "
            f"[W{p1_stats.get('wins',0)} L{p1_stats.get('losses',0)} D{p1_stats.get('draws',0)}]\n"
            f"{self.player2} (O): {self.scores[self.player2]} "
            f"[W{p2_stats.get('wins',0)} L{p2_stats.get('losses',0)} D{p2_stats.get('draws',0)}]"
        )
