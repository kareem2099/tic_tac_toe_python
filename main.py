import tkinter as tk
from game_logic import GameLogic
from player import PlayerManager
from advanced_ui import AdvancedGameUI
from game_history import GameHistory
from typing import Optional, Literal, Callable, Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class GameConfig:
    """Configuration for game settings."""
    mode: Literal['pvp', 'ai']
    difficulty: str
    player1: str
    player2: str
    board_size: int = 3

class TicTacToe:
    """Main Tic Tac Toe game class that coordinates between components.
    
    Features:
        - Manages game lifecycle
        - Coordinates between UI and game logic
        - Handles player input
        - Manages AI moves
    """
    
    def __init__(self) -> None:
        """Initialize game components and start the menu.
        
        Creates the main window, initializes game components (GUI, logic, player manager),
        and sets up the initial menu screen.
        
        Raises:
            RuntimeError: If initialization fails
        """
        self.window = tk.Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.cleanup)
        self.gui = AdvancedGameUI(self.window)
        self.logic = GameLogic()
        self.players = PlayerManager()
        
        self.current_player = "X"
        self.mode = None
        
        self.gui.menu_screen(
            pvp_callback=self.setup_pvp,
            ai_callback=self.setup_ai,
            history_callback=self.show_history,
            quit_callback=self.window.quit
        )
        
        self.window.mainloop()

    def setup_pvp(self) -> None:
        """Set up Player vs Player mode with difficulty selection.
        
        Gets player names via GUI prompts and initializes game logic
        with selected difficulty level.
        
        Raises:
            ValueError: If player names are invalid
        """
        self.mode = "pvp"
        while True:
            player1 = self.gui.ask_player_name("Enter name for Player X:")
            player2 = self.gui.ask_player_name("Enter name for Player O:")
            if player1 and player2:
                break
            self.gui.show_message("Error", "Player names cannot be empty")
        
        difficulty = self.gui.difficulty_var.get()
        self.logic = GameLogic(difficulty)
        self.players.set_players(player1, player2, "pvp")
        self.start_game()

    def setup_ai(self) -> None:
        """Set up Player vs AI mode with selected difficulty.
        
        Gets player name via GUI prompt and initializes game logic
        with selected difficulty level for AI opponent.
        
        Raises:
            ValueError: If player name is invalid
            RuntimeError: If AI initialization fails
        """
        self.mode = "ai"
        while True:
            player1 = self.gui.ask_player_name("Enter your name:")
            if player1:
                break
            self.gui.show_message("Error", "Player name cannot be empty")
        
        difficulty = self.gui.difficulty_var.get()
        self.logic = GameLogic(difficulty)
        self.players.set_players(player1, "Computer", "ai")
        self.start_game()

    def return_to_menu(self) -> None:
        """Return to the main menu."""
        self.gui.menu_screen(
            pvp_callback=self.setup_pvp,
            ai_callback=self.setup_ai,
            history_callback=self.show_history,
            quit_callback=self.window.quit
        )

    def start_game(self) -> None:
        """Start a new game with correct board size.
        
        Initializes game state and UI for a new game.
        
        Raises:
            RuntimeError: If game initialization fails
        """
        self.current_player = "X"
        size = self.logic.manager.get_board_size()
        self.logic.board = [[None for _ in range(size)] for _ in range(size)]
        self.players.game_start_time = int(self.window.tk.call('clock', 'seconds'))
        self.players.move_count = 0
        
        # Preserve game mode when restarting
        callback = self.ai_move if self.mode == "ai" else None
        
        self.gui.setup_game_board(
            cell_click_callback=self.cell_clicked,
            restart_callback=self.start_game,
            menu_callback=self.return_to_menu,
            quit_callback=self.window.quit,
            size=size
        )
        
        self.update_display()

    def cell_clicked(self, row: int, col: int) -> None:
        """Handle cell click event with improved validation.
        
        Args:
            row: Row index of clicked cell
            col: Column index of clicked cell
            
        Raises:
            ValueError: If move is invalid
            RuntimeError: If game state update fails
        """
        try:
            size = len(self.logic.board)
            if row not in range(size) or col not in range(size):
                return
                
            if self.logic.board[row][col] is not None:
                return
                
            # Make the move and update UI
            self.logic.board[row][col] = self.current_player
            self.players.move_count += 1
            self.gui.update_board(self.logic.board)
            
            # Force immediate UI update
            self.window.update()
            
            # Check for win/draw
            if self.logic.check_winner(self.logic.board, self.current_player):
                winner = self.players.player1 if self.current_player == "X" else self.players.player2
                self.players.update_score(winner)
                win_positions = self.logic.get_win_positions(self.logic.board, self.current_player)
                self.gui.animate_win(win_positions)
                self.gui.show_message("Game Over", f"{winner} wins!")
                self.gui.disable_board()
                self.players.record_game_result(winner, self.window, self.logic.board)
                return
                
            if self.logic.is_draw(self.logic.board):
                self.gui.show_message("Game Over", "It's a draw!")
                self.players.record_game_result("Draw", self.window, self.logic.board)
                return
                
        except (IndexError, AttributeError) as e:
            print(f"Cell click error: {e}")
            self.gui.show_message("Error", "Invalid move attempted")
            return
            
        self.current_player = "O" if self.current_player == "X" else "X"
        self.update_display()
        
        if self.mode == "ai" and self.current_player == "O":
            self.window.after(500, self.ai_move)

    def ai_move(self) -> None:
        """Make AI move using minimax algorithm.
        
        Calculates and executes AI move with appropriate delay.
        
        Raises:
            RuntimeError: If AI move calculation fails
        """
        row, col = self.logic.get_ai_move(self.logic.board)
        self.cell_clicked(row, col)

    def update_display(self) -> None:
        """Update all UI elements."""
        player_name = self.players.player1 if self.current_player == "X" else self.players.player2
        self.gui.update_info(f"{player_name}'s Turn ({self.current_player})")
        self.gui.update_score(self.players.get_score_text())

    def show_history(self) -> None:
        """Display game history."""
        self.players.show_history(self.window)

    def cleanup(self) -> None:
        """Clean up resources before closing the application.
        
        Ensures all resources are properly released and
        game state is saved if needed.
        """
        if hasattr(self, 'window'):
            self.window.destroy()

if __name__ == "__main__":
    try:
        game = TicTacToe()
    except Exception as e:
        print(f"Fatal error: {e}")
