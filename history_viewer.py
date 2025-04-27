import tkinter as tk
from tkinter import ttk
from typing import List, Dict
from animations import AnimationManager
from datetime import datetime

class HistoryViewer:
    """Enhanced game history viewer with animations and detailed game replay."""
    
    def __init__(self, parent: tk.Toplevel, history_data: List[Dict]):
        """Initialize the history viewer window."""
        self.parent = parent
        self.history = history_data
        self.current_game = 0
        self.current_move = 0
        
        # Setup window
        self.window = tk.Toplevel(parent)
        self.window.title("Game History")
        self.window.geometry("800x600")
        self.window.configure(bg="#2c3e50")
        
        # Initialize animation manager
        self.animator = AnimationManager(self.window)
        
        # Create UI components
        self._setup_ui()
        self._load_game(0)
        
    def _setup_ui(self) -> None:
        """Create all UI components."""
        # Main container
        main_frame = tk.Frame(self.window, bg="#2c3e50")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Game selection controls
        control_frame = tk.Frame(main_frame, bg="#2c3e50")
        control_frame.pack(fill="x", pady=10)
        
        self.game_var = tk.StringVar()
        self.game_dropdown = ttk.Combobox(
            control_frame,
            textvariable=self.game_var,
            state="readonly",
            width=50
        )
        self.game_dropdown.pack(side="left", padx=5)
        self.game_dropdown.bind("<<ComboboxSelected>>", self._on_game_select)
        
        tk.Button(
            control_frame,
            text="Previous",
            command=self._prev_game,
            width=10
        ).pack(side="left", padx=5)
        
        tk.Button(
            control_frame,
            text="Next",
            command=self._next_game,
            width=10
        ).pack(side="left", padx=5)
        
        # Game info display
        info_frame = tk.Frame(main_frame, bg="#34495e", padx=10, pady=10)
        info_frame.pack(fill="x", pady=10)
        
        self.info_labels = {
            "players": tk.Label(info_frame, bg="#34495e", fg="white"),
            "result": tk.Label(info_frame, bg="#34495e", fg="white"),
            "date": tk.Label(info_frame, bg="#34495e", fg="white"),
            "moves": tk.Label(info_frame, bg="#34495e", fg="white")
        }
        
        for i, (key, label) in enumerate(self.info_labels.items()):
            label.grid(row=i, column=0, sticky="w", pady=2)
        
        # Game board display
        self.board_frame = tk.Frame(main_frame, bg="#2c3e50")
        self.board_frame.pack(pady=20)
        
        # Initialize empty cells list - will be populated when loading a game
        self.cells = []
            
        # Move controls
        move_frame = tk.Frame(main_frame, bg="#2c3e50")
        move_frame.pack(fill="x", pady=10)
        
        self.move_slider = tk.Scale(
            move_frame,
            from_=0,
            to=0,
            orient="horizontal",
            command=self._on_move_slider
        )
        self.move_slider.pack(fill="x", expand=True, padx=10)
        
        tk.Button(
            move_frame,
            text="Replay",
            command=self._replay_game,
            width=10
        ).pack(side="left", padx=5)
        
        tk.Button(
            move_frame,
            text="Step",
            command=self._step_move,
            width=10
        ).pack(side="left", padx=5)
        
        # Populate game dropdown
        self._update_game_list()
        
    def _update_game_list(self) -> None:
        """Update the game selection dropdown."""
        game_list = []
        for i, game in enumerate(self.history):
            date = datetime.fromisoformat(game["timestamp"]).strftime("%Y-%m-%d %H:%M")
            players = f"{game['player1']} vs {game['player2']}"
            result = "Draw" if game["winner"] is None else f"Winner: {game['winner']}"
            game_list.append(f"{date} - {players} - {result}")
        
        self.game_dropdown["values"] = game_list
        if game_list:
            self.game_dropdown.current(0)
            
    def _load_game(self, index: int) -> None:
        """Load a game from history."""
        if not self.history or index < 0 or index >= len(self.history):
            return
            
        self.current_game = index
        game = self.history[index]
        
        # Update info labels
        date = datetime.fromisoformat(game["timestamp"]).strftime("%Y-%m-%d %H:%M")
        result = "Draw" if game["winner"] is None else f"{game['winner']} won"
        
        self.info_labels["players"].config(text=f"Players: {game['player1']} vs {game['player2']}")
        self.info_labels["result"].config(text=f"Result: {result}")
        self.info_labels["date"].config(text=f"Date: {date}")
        self.info_labels["moves"].config(text=f"Moves: {game['move_count']}")
        
        # Reset board
        for row in self.cells:
            for cell in row:
                cell.config(text="", bg="#34495e")
                
        # Update move slider
        self.move_slider.config(to=len(game["moves"]))
        self.move_slider.set(0)
        self.current_move = 0
        
        # Animate game info update
        self.animator.fade_in(self.info_labels["players"])
        self.animator.fade_in(self.info_labels["result"])
        
    def _on_game_select(self, event=None) -> None:
        """Handle game selection from dropdown."""
        index = self.game_dropdown.current()
        if index >= 0:
            self._load_game(index)
            
    def _prev_game(self) -> None:
        """Load previous game in history."""
        if self.current_game > 0:
            self._load_game(self.current_game - 1)
            self.game_dropdown.current(self.current_game)
            
    def _next_game(self) -> None:
        """Load next game in history."""
        if self.current_game < len(self.history) - 1:
            self._load_game(self.current_game + 1)
            self.game_dropdown.current(self.current_game)
            
    def _on_move_slider(self, value: str) -> None:
        """Handle move slider change."""
        move_num = int(value)
        if move_num != self.current_move:
            self._show_move(move_num)
            
    def _show_move(self, move_num: int) -> None:
        """Show specific move in the game using stored board states."""
        game = self.history[self.current_game]
        if move_num < 0 or move_num > len(game["moves"]):
            return
            
        # Get the board state at this move
        if move_num == 0:
            board_state = [[None for _ in range(len(self.cells))] for _ in range(len(self.cells))]
        else:
            try:
                board_state = game["moves"][move_num-1]["board_state"]
                # Validate board state matches current cell count
                if len(board_state) != len(self.cells) or len(board_state[0]) != len(self.cells[0]):
                    board_state = [[None for _ in range(len(self.cells[0]))] for _ in range(len(self.cells))]
            except (KeyError, IndexError):
                board_state = [[None for _ in range(len(self.cells[0]))] for _ in range(len(self.cells))]
            
        # Update board display
        for row in range(len(board_state)):
            for col in range(len(board_state[row])):
                cell = self.cells[row][col]
                symbol = board_state[row][col]
                if symbol:
                    color = "#e74c3c" if symbol == "X" else "#3498db"
                    cell.config(text=symbol, fg=color)
                else:
                    cell.config(text="", bg="#34495e")
            
        self.current_move = move_num
        
    def _step_move(self) -> None:
        """Advance to next move in current game."""
        game = self.history[self.current_game]
        if self.current_move < len(game["moves"]):
            move = game["moves"][self.current_move]
            row, col = move["row"], move["col"]
            symbol = "X" if move["player"] == "X" else "O"
            color = "#e74c3c" if symbol == "X" else "#3498db"
            
            # Animate the move
            self.animator.pulse(self.cells[row][col], "#34495e", "#4a6fa5", 1, 0.2)
            self.cells[row][col].config(text=symbol, fg=color)
            
            self.current_move += 1
            self.move_slider.set(self.current_move)
            
    def _replay_game(self) -> None:
        """Animate replay of the entire game using stored board states."""
        self._show_move(0)
        game = self.history[self.current_game]
        
        def play_next_move(i=0):
            if i <= len(game["moves"]):
                try:
                    # Get board state for this move
                    if i == 0:
                        board_state = [[None for _ in range(len(self.cells))] for _ in range(len(self.cells))]
                    else:
                        board_state = game["moves"][i-1].get("board_state")
                        if board_state is None:
                            # Fallback: reconstruct board from moves
                            board_state = [[None for _ in range(len(self.cells))] for _ in range(len(self.cells))]
                            for move in game["moves"][:i]:
                                if "row" in move and "col" in move and "player" in move:
                                    board_state[move["row"]][move["col"]] = move["player"]
                except (KeyError, IndexError):
                    board_state = [[None for _ in range(len(self.cells))] for _ in range(len(self.cells))]
                
                # Update board display
                for row in range(len(board_state)):
                    for col in range(len(board_state[row])): 
                        cell = self.cells[row][col]
                        symbol = board_state[row][col]
                        if symbol:
                            color = "#e74c3c" if symbol == "X" else "#3498db"
                            if cell["text"] != symbol:  # Only animate changed cells
                                self.animator.pulse(cell, "#34495e", "#4a6fa5", 1, 0.2)
                            cell.config(text=symbol, fg=color)
                        else:
                            cell.config(text="", bg="#34495e")
                
                self.current_move = i
                self.move_slider.set(i)
                self.window.after(500, play_next_move, i + 1)
                
        play_next_move()
        
        # Highlight winning moves if applicable
        if game["winner"]:
            self.window.after(len(game["moves"]) * 500 + 200, self._highlight_winner)
            
    def _highlight_winner(self) -> None:
        """Animate winning positions."""
        game = self.history[self.current_game]
        winner = game.get("winner")
        if not winner or not self.cells:
            return
            
        try:
            # Find winning positions (this would need game logic integration)
            # For now just highlight all moves by winner
            win_cells = []
            player_symbol = "X" if winner == game["player1"] else "O"
            
            for move in game["moves"]:
                try:
                    if (move.get("player") == player_symbol and 
                        "row" in move and "col" in move and
                        0 <= move["row"] < len(self.cells) and 
                        0 <= move["col"] < len(self.cells[0])):
                        win_cells.append(self.cells[move["row"]][move["col"]])
                except (KeyError, TypeError):
                    continue
                    
            if win_cells:
                self.animator.animate_win(win_cells, "#2ecc71", 3)
        except Exception:
            pass  # Skip highlighting if there are any errors
