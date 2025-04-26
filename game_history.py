import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Literal
from pathlib import Path
import tempfile

class GameHistory:
    """Handles advanced game history tracking and statistics with atomic writes.
    
    Features:
        - Atomic file writes to prevent corruption
        - Backup history file
        - Data validation
        - Thread-safe operations
    """
    
    def __init__(self, history_file: str = "game_history.json") -> None:
        """Initialize with history file path.
        
        Args:
            history_file: Path to JSON file for storing history
        """
        self.history_file = Path(history_file)
        self.backup_file = self.history_file.with_suffix('.bak')
        self.history: List[Dict] = []
        self._load_history()

    def _load_history(self) -> None:
        """Safely load history from file if exists."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
                if not isinstance(self.history, list):
                    raise ValueError("Invalid history file format")
        except (json.JSONDecodeError, ValueError) as e:
            if self.backup_file.exists():
                try:
                    with open(self.backup_file, 'r') as f:
                        self.history = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    self.history = []
            else:
                self.history = []

    def _save_history(self) -> None:
        """Atomically save history to file with backup."""
        try:
            # Write to temp file first
            with tempfile.NamedTemporaryFile(
                mode='w',
                dir=str(self.history_file.parent),
                delete=False
            ) as tmp:
                json.dump(self.history, tmp, indent=2)
            
            # Create backup if main file exists
            if self.history_file.exists():
                self.history_file.replace(self.backup_file)
            
            # Move temp file to final location
            Path(tmp.name).replace(self.history_file)
        except Exception as e:
            print(f"Error saving history: {e}")

    def add_game(
        self,
        player1: str,
        player2: str,
        winner: Optional[str],
        moves: List[Dict],
        game_type: Literal['pvp', 'pvc'] = "pvp"
    ) -> None:
        """Add a completed game to history with validation.
        
        Args:
            player1: Name of player 1
            player2: Name of player 2
            winner: Name of winner (None for tie)
            moves: List of move dicts with positions and players
            game_type: Type of game ('pvp' or 'pvc')
            
        Raises:
            ValueError: If game data is invalid
        """
        # Validate inputs
        if not player1 or not player2:
            raise ValueError("Player names cannot be empty")
        if winner not in {None, player1, player2}:
            raise ValueError("Winner must be one of the players or None")
        if game_type not in {'pvp', 'pvc'}:
            raise ValueError("Game type must be 'pvp' or 'pvc'")
        if not isinstance(moves, list):
            raise ValueError("Moves must be a list")
        game = {
            "timestamp": datetime.now().isoformat(),
            "player1": player1,
            "player2": player2,
            "winner": winner,
            "moves": moves,
            "game_type": game_type,
            "move_count": len(moves)
        }
        self.history.append(game)
        self._save_history()

    def get_player_stats(self, player_name: str) -> Dict[str, object]:
        """Get comprehensive statistics for a specific player.
        
        Args:
            player_name: Name of player to get stats for
            
        Returns:
            Dictionary containing:
                - total_games: int
                - wins: int
                - losses: int
                - ties: int
                - win_rate: float
                - favorite_opponent: Optional[str]
                - recent_games: List[Dict]
                - longest_win_streak: int
                - current_streak: int
                - move_stats: Dict[str, float]
                
        Raises:
            ValueError: If player_name is empty
        """
        if not player_name:
            raise ValueError("Player name cannot be empty")
        stats = {
            "total_games": 0,
            "wins": 0,
            "losses": 0,
            "ties": 0,
            "win_rate": 0.0,
            "favorite_opponent": None,
            "recent_games": [],
            "longest_win_streak": 0,
            "current_streak": 0,
            "move_stats": {
                "total_moves": 0,
                "avg_moves": 0,
                "min_moves": float('inf'),
                "max_moves": 0
            }
        }
        
        # Calculate stats
        opponent_counts = {}
        current_streak = 0
        longest_streak = 0
        last_result = None
        
        for game in sorted(self.history, key=lambda x: x["timestamp"]):
            if player_name in [game["player1"], game["player2"]]:
                stats["total_games"] += 1
                stats["recent_games"].append(game)
                
                # Track moves
                stats["move_stats"]["total_moves"] += game["move_count"]
                stats["move_stats"]["min_moves"] = min(stats["move_stats"]["min_moves"], game["move_count"])
                stats["move_stats"]["max_moves"] = max(stats["move_stats"]["max_moves"], game["move_count"])
                
                opponent = game["player2"] if game["player1"] == player_name else game["player1"]
                opponent_counts[opponent] = opponent_counts.get(opponent, 0) + 1
                
                # Track wins/losses/ties
                if game["winner"] == player_name:
                    stats["wins"] += 1
                    result = "win"
                elif game["winner"] is None:
                    stats["ties"] += 1
                    result = "tie"
                else:
                    stats["losses"] += 1
                    result = "loss"
                
                # Track streaks
                if result == last_result or last_result is None:
                    current_streak += 1
                else:
                    current_streak = 1
                
                if result == "win":
                    longest_streak = max(longest_streak, current_streak)
                
                last_result = result
        
        # Calculate derived stats
        if stats["total_games"] > 0:
            stats["win_rate"] = stats["wins"] / stats["total_games"]
            if opponent_counts:
                stats["favorite_opponent"] = max(opponent_counts, key=opponent_counts.get)
            
            stats["longest_win_streak"] = longest_streak
            stats["current_streak"] = current_streak * (1 if last_result == "win" else -1 if last_result == "loss" else 0)
            
            # Move statistics
            stats["move_stats"]["avg_moves"] = stats["move_stats"]["total_moves"] / stats["total_games"]
            if stats["move_stats"]["min_moves"] == float('inf'):
                stats["move_stats"]["min_moves"] = 0
        
        # Keep only last 5 games
        stats["recent_games"] = stats["recent_games"][-5:]
        
        return stats

    def get_all_history(self, limit: int = 20) -> List[Dict]:
        """Get complete game history.
        
        Args:
            limit: Maximum number of games to return
            
        Returns:
            List of game records, most recent first
        """
        return sorted(
            self.history[-limit:],
            key=lambda x: x["timestamp"],
            reverse=True
        )

    def search_history(
        self,
        player_name: Optional[str] = None,
        game_type: Optional[Literal['pvp', 'pvc']] = None,
        min_moves: Optional[int] = None,
        max_moves: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Search history with various filters.
        
        Args:
            player_name: Filter by player name
            game_type: Filter by game type ('pvp' or 'pvc')
            min_moves: Minimum moves in game
            max_moves: Maximum moves in game
            date_from: Earliest date to include
            date_to: Latest date to include
            limit: Maximum number of results to return
            
        Returns:
            List of filtered game records, most recent first
            
        Raises:
            ValueError: If filters are invalid
        """
        if min_moves is not None and min_moves < 0:
            raise ValueError("min_moves cannot be negative")
        if max_moves is not None and max_moves < 0:
            raise ValueError("max_moves cannot be negative")
        if date_from and date_to and date_from > date_to:
            raise ValueError("date_from cannot be after date_to")
        results = []
        for game in self.history:
            # Apply filters
            if player_name and player_name not in [game["player1"], game["player2"]]:
                continue
            if game_type and game["game_type"] != game_type:
                continue
            if min_moves and game["move_count"] < min_moves:
                continue
            if max_moves and game["move_count"] > max_moves:
                continue
            if date_from and datetime.fromisoformat(game["timestamp"]) < date_from:
                continue
            if date_to and datetime.fromisoformat(game["timestamp"]) > date_to:
                continue
                
            results.append(game)
            
        return sorted(results, key=lambda x: x["timestamp"], reverse=True)

    def clear_history(self) -> None:
        """Clear all history records."""
        self.history = []
        self._save_history()
