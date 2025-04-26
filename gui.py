import tkinter as tk
from tkinter import simpledialog, messagebox
from typing import Optional, List, Dict, Tuple

class GameGUI:
    """Handles all GUI components for the Tic Tac Toe game."""
    
    def __init__(self, window: tk.Tk):
        """Initialize the GUI with the main window."""
        self.window = window
        self.window.title("Tic Tac Toe")
        self.window.configure(bg="#f5f7fa")
        try:
            self.window.wm_attributes('-zoomed', True)  # Try cross-platform maximize
        except:
            self.window.geometry("{0}x{1}+0+0".format(
                self.window.winfo_screenwidth(),
                self.window.winfo_screenheight()
            ))
        self.window.resizable(True, True)  # Allow resizing
        
        # Modern color scheme
        self.colors = {
            "primary": "#4f46e5",
            "secondary": "#6366f1",
            "accent": "#10b981",
            "danger": "#ef4444",
            "light": "#f5f7fa",
            "dark": "#1e293b",
            "text": "#334155"
        }
        
        self.board_buttons: List[List[tk.Button]] = []
        self.info_label: Optional[tk.Label] = None
        self.score_label: Optional[tk.Label] = None

    def menu_screen(self, pvp_callback, ai_callback, history_callback, quit_callback) -> None:
        """Display the main menu with game mode and difficulty options."""
        self.clear_window()
        
        # Main title
        tk.Label(self.window, text="Tic Tac Toe", font=("Helvetica", 24, "bold"), 
                bg=self.colors["light"], fg=self.colors["dark"]).pack(pady=20)

        # Game difficulty selection (always visible)
        self.game_diff_frame = tk.Frame(self.window, bg=self.colors["light"])
        self.game_diff_frame.pack(pady=5)
        
        tk.Label(self.game_diff_frame, text="Game Mode:", font=("Helvetica", 12),
                bg=self.colors["light"], fg=self.colors["dark"]).pack(side="left")
                
        self.game_diff_var = tk.StringVar(value="medium")
        game_diffs = ["easy", "medium", "hard", "insane"]
        game_diff_menu = tk.OptionMenu(self.game_diff_frame, self.game_diff_var, *game_diffs)
        game_diff_menu.config(bg=self.colors["primary"], fg="white", 
                            activebackground=self.colors["secondary"])
        game_diff_menu.pack(side="left", padx=10)

        # AI level selection (hidden by default)
        self.ai_level_frame = tk.Frame(self.window, bg=self.colors["light"])
        self.ai_level_frame.pack_forget()  # Start hidden
        
        tk.Label(self.ai_level_frame, text="AI Level (1-10):", font=("Helvetica", 12),
                bg=self.colors["light"], fg=self.colors["dark"]).pack(side="left")
                
        self.ai_level_var = tk.IntVar(value=5)
        ai_levels = list(range(1, 11))  # 1-10
        self.ai_level_menu = tk.OptionMenu(self.ai_level_frame, self.ai_level_var, *ai_levels)
        self.ai_level_menu.config(bg=self.colors["primary"], fg="white", 
                                activebackground=self.colors["secondary"])
        self.ai_level_menu.pack(side="left", padx=10)

        # Modern button styling
        button_style = {
            "font": ("Segoe UI", 12, "bold"),
            "width": 22,
            "height": 1,
            "bg": self.colors["primary"],
            "fg": "white",
            "activebackground": self.colors["secondary"],
            "borderwidth": 0,
            "highlightthickness": 0,
            "relief": "flat",
            "padx": 10,
            "pady": 5,
            "cursor": "hand2"
        }

        # Menu container frame for better spacing
        menu_frame = tk.Frame(self.window, bg=self.colors["light"])
        menu_frame.pack(pady=20, padx=20, fill="both", expand=True)

        tk.Label(menu_frame, text="Tic Tac Toe", font=("Segoe UI", 28, "bold"), 
                bg=self.colors["light"], fg=self.colors["dark"]).pack(pady=(0, 20))

        # Menu buttons with hover effects
        # Player vs Player button
        pvp_btn = tk.Button(menu_frame, text="Player vs Player", 
                           command=lambda: [pvp_callback(), self.ai_level_frame.pack_forget()],
                           **button_style)
        pvp_btn.pack(pady=8, ipady=5)
        pvp_btn.bind("<Enter>", lambda e, b=pvp_btn: b.config(bg=self.colors["secondary"]))
        pvp_btn.bind("<Leave>", lambda e, b=pvp_btn: b.config(bg=self.colors["primary"]))

        # Player vs AI button
        ai_btn = tk.Button(menu_frame, text="Player vs AI", 
                         command=lambda: [ai_callback(), self.ai_level_frame.pack(pady=5)],
                         **button_style)
        ai_btn.pack(pady=8, ipady=5)
        ai_btn.bind("<Enter>", lambda e, b=ai_btn: b.config(bg=self.colors["secondary"]))
        ai_btn.bind("<Leave>", lambda e, b=ai_btn: b.config(bg=self.colors["primary"]))

        # Other buttons
        buttons = [
            ("Game History", history_callback),
            ("Exit", quit_callback)
        ]

        for text, callback in buttons:
            btn = tk.Button(menu_frame, text=text, command=callback, **button_style)
            btn.pack(pady=8, ipady=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.colors["secondary"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors["primary"]))

    def setup_game_board(self, cell_click_callback, restart_callback, menu_callback, quit_callback, size=3) -> None:
        """Initialize and display the game board with responsive layout.
        
        Args:
            cell_click_callback: Function to call when a cell is clicked (row, col)
            restart_callback: Function to call for restarting game
            menu_callback: Function to call to return to main menu
            quit_callback: Function to call to exit game
            size: Size of the game board (3-6)
        """
        self.clear_window()
        self.board_buttons = []
        
        # Main game container
        game_frame = tk.Frame(self.window, bg=self.colors["light"])
        game_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Game info display
        self.info_label = tk.Label(game_frame, text="", font=("Segoe UI", 16, "bold"), 
                                 bg=self.colors["light"], fg=self.colors["dark"])
        self.info_label.grid(row=0, column=0, columnspan=size, pady=(0, 15))

        # Adjust font size based on board size
        font_size = 36 if size <= 4 else 24 if size == 5 else 20
        btn_width = 6 if size <= 4 else 4 if size == 5 else 3

        # Game board with modern styling and animations
        for r in range(size):
            row_buttons = []
            for c in range(size):
                btn = tk.Button(game_frame, text="", font=("Segoe UI", font_size, "bold"), 
                              width=btn_width, height=2,
                              bg="white", fg=self.colors["dark"], activebackground="#f8fafc",
                              relief="flat", borderwidth=2,
                              command=lambda row=r, col=c: cell_click_callback(row, col))
                # Add hover animations
                btn.bind("<Enter>", lambda e, b=btn: (
                    b.config(bg="#f3f4f6"),
                    b.config(relief="groove")
                ))
                btn.bind("<Leave>", lambda e, b=btn: (
                    b.config(bg="white"),
                    b.config(relief="flat")
                ))
                btn.grid(row=r+1, column=c, padx=5, pady=5, sticky="nsew")
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#f3f4f6"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="white"))
                row_buttons.append(btn)
            self.board_buttons.append(row_buttons)

        # Score display
        self.score_label = tk.Label(game_frame, text="", font=("Segoe UI", 14), 
                                   bg=self.colors["light"], fg=self.colors["text"])
        self.score_label.grid(row=4, column=0, columnspan=3, pady=(15, 10))

        # Control buttons with hover effects
        control_btn_style = {
            "font": ("Segoe UI", 10, "bold"),
            "width": 8,
            "height": 1,
            "bg": self.colors["primary"],
            "fg": "white",
            "activebackground": self.colors["secondary"],
            "borderwidth": 0,
            "relief": "flat",
            "cursor": "hand2"
        }

        controls_frame = tk.Frame(game_frame, bg=self.colors["light"])
        controls_frame.grid(row=5, column=0, columnspan=3, pady=(10, 0), sticky="ew")
        game_frame.grid_rowconfigure(0, weight=0)
        game_frame.grid_rowconfigure(1, weight=1)
        game_frame.grid_rowconfigure(2, weight=1)
        game_frame.grid_rowconfigure(3, weight=1)
        game_frame.grid_rowconfigure(4, weight=0)
        game_frame.grid_rowconfigure(5, weight=0)
        for c in range(3):
            game_frame.grid_columnconfigure(c, weight=1)

        # Left-align Restart button
        tk.Button(controls_frame, text="Restart", command=restart_callback, **control_btn_style).pack(side="left", padx=5)
        
        # Center Menu button
        menu_frame = tk.Frame(controls_frame, bg=self.colors["light"])
        menu_frame.pack(side="left", expand=True, fill="x")
        tk.Button(menu_frame, text="Menu", command=menu_callback, **control_btn_style).pack(padx=5)
        
        # Right-align Exit button
        tk.Button(controls_frame, text="Exit", command=quit_callback, **control_btn_style).pack(side="right", padx=5)

    def update_board(self, board: List[List[Optional[str]]]) -> None:
        """Update the visual state of the board.
        
        Args:
            board: The current game board state
        """
        size = len(board)
        for r in range(size):
            for c in range(size):
                self.board_buttons[r][c]["text"] = board[r][c] if board[r][c] else ""

    def disable_board(self) -> None:
        """Disable all board buttons after game ends."""
        for r in range(3):
            for c in range(3):
                self.board_buttons[r][c]["state"] = "disabled"

    def update_info(self, text: str) -> None:
        """Update the turn information label.
        
        Args:
            text: The text to display
        """
        self.info_label.config(text=text)

    def update_score(self, text: str) -> None:
        """Update the score display.
        
        Args:
            text: The text to display
        """
        self.score_label.config(text=text)

    def clear_window(self) -> None:
        """Clear all widgets from the window."""
        for widget in self.window.winfo_children():
            widget.destroy()

    def show_message(self, title: str, message: str) -> None:
        """Show a message box.
        
        Args:
            title: The message box title
            message: The message content
        """
        messagebox.showinfo(title, message)

    def ask_player_name(self, prompt: str) -> str:
        """Prompt for a player name with validation.
        
        Args:
            prompt: The prompt text
            
        Returns:
            The entered player name (guaranteed valid) or None if canceled
            
        Raises:
            ValueError: If name validation fails
        """
        while True:
            name = simpledialog.askstring("Player", prompt)
            if name is None:  # User clicked cancel
                return None
                
            # Trim whitespace
            name = name.strip()
            
            # Validate
            if not name:
                messagebox.showerror("Invalid Name", "Name cannot be empty!")
                continue
            if len(name) < 2:
                messagebox.showerror("Invalid Name", "Name must be at least 2 characters!")
                continue
            if not name.replace(" ", "").isalnum():
                messagebox.showerror("Invalid Name", "Name can only contain letters, numbers and spaces!")
                continue
                
            return name
