import tkinter as tk
from tkinter import font
from typing import Callable, Optional
from animations import AnimationManager

class AdvancedGameUI:
    """Handles all advanced UI elements with enhanced animations."""
    
    def __init__(self, window: tk.Tk):
        """Initialize UI components with enhanced styling."""
        self.window = window
        self.window.configure(bg="#2c3e50")
        
        # Custom fonts
        self.title_font = font.Font(family="Helvetica", size=24, weight="bold")
        self.info_font = font.Font(family="Helvetica", size=14)
        self.cell_font = font.Font(family="Helvetica", size=48, weight="bold")
        
        # Colors
        self.bg_color = "#2c3e50"
        self.cell_color = "#34495e"
        self.x_color = "#e74c3c"
        self.o_color = "#3498db"
        self.text_color = "#ecf0f1"
        self.win_color = "#2ecc71"
        
        # Initialize animation manager
        self.animator = AnimationManager(window)
        
    def setup_game_board(self, cell_click_callback: Callable, 
                        restart_callback: Callable, 
                        menu_callback: Callable, 
                        quit_callback: Callable,
                        size: int = 3) -> None:
        """Create animated game board with enhanced styling and control buttons."""
        self.clear_window()
        
        # Game board frame
        self.board_frame = tk.Frame(self.window, bg=self.bg_color)
        self.board_frame.pack(pady=20)
        
        # Create game cells
        self.cells = []
        for row in range(size):
            row_cells = []
            for col in range(size):
                cell = tk.Button(
                    self.board_frame,
                    text="",
                    font=self.cell_font,
                    width=3,
                    height=1,
                    bg=self.cell_color,
                    fg=self.text_color,
                    activebackground="#4a6fa5",
                    relief="flat",
                    borderwidth=0,
                    command=lambda r=row, c=col: cell_click_callback(r, c)
                )
                cell.grid(row=row, column=col, padx=5, pady=5, ipadx=10, ipady=10)
                row_cells.append(cell)
            self.cells.append(row_cells)
            
        # Control buttons frame
        button_frame = tk.Frame(self.window, bg=self.bg_color)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Restart Game",
            font=self.info_font,
            bg=self.cell_color,
            fg=self.text_color,
            command=restart_callback,
            width=15
        ).pack(side="left", padx=10)
        
        tk.Button(
            button_frame,
            text="Main Menu",
            font=self.info_font,
            bg=self.cell_color,
            fg=self.text_color,
            command=menu_callback,
            width=15
        ).pack(side="left", padx=10)
        
        tk.Button(
            button_frame,
            text="Quit",
            font=self.info_font,
            bg="#e74c3c",
            fg=self.text_color,
            command=quit_callback,
            width=15
        ).pack(side="left", padx=10)
            
    def animate_move(self, row: int, col: int, symbol: str) -> None:
        """Animate symbol placement on the board with enhanced effects."""
        cell = self.cells[row][col]
        color = self.x_color if symbol == "X" else self.o_color
        
        # First pulse the cell background
        self.animator.pulse(cell, self.cell_color, "#4a6fa5", 2, 0.2)
        
        # Then fade in the symbol
        cell.config(text=symbol, fg=color)
        self.animator.fade_in(cell, 0.3, lambda: cell.config(state="disabled"))
        
    def animate_win(self, positions: list[tuple[int, int]]) -> None:
        """Animate winning combination with enhanced effects."""
        try:
            win_cells = []
            for row, col in positions:
                if (hasattr(self, 'cells') and 
                    row < len(self.cells) and 
                    col < len(self.cells[0])):
                    cell = self.cells[row][col]
                    if cell.winfo_exists():
                        win_cells.append(cell)
            
            if win_cells:
                self.animator.animate_win(win_cells, self.win_color, 5)
        except Exception as e:
            print(f"Animation error: {e}")  # Log animation errors
                
    def update_board(self, board: list[list[Optional[str]]]) -> None:
        """Update board with current game state."""
        for row in range(len(board)):
            for col in range(len(board[0])):
                cell = self.cells[row][col]
                if board[row][col]:
                    cell.config(text=board[row][col])
                    color = self.x_color if board[row][col] == "X" else self.o_color
                    cell.config(fg=color)
                else:
                    cell.config(text="", state="normal")
                    
    def show_message(self, title: str, message: str) -> None:
        """Show animated message dialog."""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.configure(bg=self.bg_color)
        
        tk.Label(
            dialog,
            text=title,
            font=self.title_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=10)
        
        tk.Label(
            dialog,
            text=message,
            font=self.info_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=10)
        
        # Use animator for fade-in
        dialog.attributes("-alpha", 0)
        self.animator.fade_in(dialog, duration=0.3)
            
        tk.Button(
            dialog,
            text="OK",
            command=dialog.destroy,
            font=self.info_font,
            bg=self.cell_color,
            fg=self.text_color
        ).pack(pady=10)
        
    def disable_board(self) -> None:
        """Disable all board cells with safety checks."""
        if not hasattr(self, 'cells'):
            return
            
        for row in self.cells:
            for cell in row:
                try:
                    if cell.winfo_exists():
                        cell.config(state="disabled")
                except tk.TclError:
                    continue
                
    def update_info(self, text: str) -> None:
        """Update game info display with safety checks."""
        try:
            # Add heart icon if player name is "tuqa"
            display_text = text.replace("tuqa", "tuqa ❤️") if "tuqa" in text.lower() else text
            if not hasattr(self, 'info_label') or not self.info_label.winfo_exists():
                self.info_label = tk.Label(
                    self.window,
                    text=display_text,
                    font=self.info_font,
                    bg=self.bg_color,
                    fg=self.text_color
                )
                self.info_label.pack(pady=10)
            else:
                self.info_label.config(text=display_text)
        except tk.TclError:
            # Recreate label if it was destroyed
            self.info_label = tk.Label(
                self.window,
                text=text,
                font=self.info_font,
                bg=self.bg_color,
                fg=self.text_color
            )
            self.info_label.pack(pady=10)
            
    def update_score(self, text: str) -> None:
        """Update score display with error handling."""
        try:
            # Add heart icon if player name is "tuqa"
            display_text = text.replace("tuqa", "tuqa ❤️") if "tuqa" in text.lower() else text
            
            # Create new label if it doesn't exist or was destroyed
            if not hasattr(self, 'score_label') or not self.score_label.winfo_exists():
                self.score_label = tk.Label(
                    self.window,
                    text=display_text,
                    font=self.info_font,
                    bg=self.bg_color,
                    fg=self.text_color
                )
                self.score_label.pack(pady=5)
            else:
                self.score_label.config(text=display_text)
        except tk.TclError:
            # Recreate label if it was destroyed
            self.score_label = tk.Label(
                self.window,
                text=display_text,
                font=self.info_font,
                bg=self.bg_color,
                fg=self.text_color
            )
            self.score_label.pack(pady=5)

    def menu_screen(self, pvp_callback: Callable, ai_callback: Callable, 
                   history_callback: Callable, quit_callback: Callable) -> None:
        """Display the main menu screen with difficulty selection."""
        self.clear_window()
        # Store callbacks for dialog close behavior
        self.pvp_callback = pvp_callback
        self.ai_callback = ai_callback
        
        tk.Label(
            self.window,
            text="Tic Tac Toe",
            font=self.title_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=20)
        
        # Difficulty selection frame
        diff_frame = tk.Frame(self.window, bg=self.bg_color)
        diff_frame.pack(pady=5)
        
        tk.Label(
            diff_frame,
            text="Game Difficulty:",
            font=self.info_font,
            bg=self.bg_color,
            fg=self.text_color
        ).grid(row=0, column=0, columnspan=4, pady=5)
        
        self.difficulty_var = tk.IntVar(value=5)
        tk.Scale(
            diff_frame,
            from_=1,
            to=10,
            orient="horizontal",
            variable=self.difficulty_var,
            label="AI Difficulty (1-10)",
            font=self.info_font,
            bg=self.bg_color,
            fg=self.text_color,
            troughcolor=self.cell_color,
            activebackground="#4a6fa5",
            length=300
        ).grid(row=1, column=0, columnspan=4, pady=10)
        
        button_frame = tk.Frame(self.window, bg=self.bg_color)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Player vs Player",
            font=self.info_font,
            bg=self.cell_color,
            fg=self.text_color,
            command=pvp_callback,
            width=20
        ).pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Player vs AI",
            font=self.info_font,
            bg=self.cell_color,
            fg=self.text_color,
            command=ai_callback,
            width=20
        ).pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Game History",
            font=self.info_font,
            bg=self.cell_color,
            fg=self.text_color,
            command=history_callback,
            width=20
        ).pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Quit",
            font=self.info_font,
            bg="#e74c3c",
            fg=self.text_color,
            command=quit_callback,
            width=20
        ).pack(pady=10)

    def ask_player_name(self, prompt: str) -> str:
        """Prompt for and validate player name input.
        
        Args:
            prompt: The text to display as prompt
            
        Returns:
            The entered and validated player name
        """
        dialog = tk.Toplevel(self.window)
        dialog.title("Player Name")
        dialog.configure(bg=self.bg_color)
        dialog.resizable(False, False)
        
        # Error message label
        error_var = tk.StringVar()
        error_label = tk.Label(
            dialog,
            textvariable=error_var,
            font=self.info_font,
            bg=self.bg_color,
            fg="#e74c3c"
        )
        
        tk.Label(
            dialog,
            text=prompt,
            font=self.info_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=10)
        
        name_var = tk.StringVar()
        entry = tk.Entry(
            dialog,
            textvariable=name_var,
            font=self.info_font,
            width=20
        )
        entry.pack(pady=5)
        entry.focus_set()
        
        error_label.pack()
        
        result = None
        
        def validate_name(name: str) -> bool:
            """Validate player name according to rules."""
            if not name:
                error_var.set("Name cannot be empty")
                return False
            if len(name) < 2:
                error_var.set("Name too short (min 2 chars)")
                return False
            if len(name) > 15:
                error_var.set("Name too long (max 15 chars)")
                return False
            if not all(c.isalnum() or c.isspace() for c in name):
                error_var.set("Only letters, numbers and spaces allowed")
                return False
            return True
            
        def on_ok():
            nonlocal result
            name = name_var.get().strip()
            if validate_name(name):
                result = name
                dialog.destroy()
                
        tk.Button(
            dialog,
            text="OK",
            command=on_ok,
            font=self.info_font,
            bg=self.cell_color,
            fg=self.text_color
        ).pack(pady=10)
        
        # Bind Enter key to OK button
        dialog.bind('<Return>', lambda e: on_ok())
        
        # Handle window close (X button) - just close the dialog
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.wait_window()
        return result if result is not None else "Player"

    def _set_difficulty_and_callback(self, callback: Callable) -> None:
        """Set difficulty level and execute callback."""
        from game_logic import GameLogic
        GameLogic().difficulty = self.difficulty_var.get()
        callback()

    def clear_window(self) -> None:
        """Clear all widgets from the window."""
        for widget in self.window.winfo_children():
            widget.destroy()
