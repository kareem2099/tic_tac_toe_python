import tkinter as tk
import time
from typing import List, Tuple, Callable

class AnimationManager:
    """Handles all UI animations for the game."""
    
    def __init__(self, window: tk.Tk):
        self.window = window
        self.active_animations = []
        
    def fade_in(self, widget, duration=0.3, callback=None):
        """Fade in a widget from transparent to opaque."""
        widget.attributes("-alpha", 0)
        steps = int(duration / 0.02)
        step = 1.0 / steps
        
        def _fade(step_num=0):
            if step_num <= steps:
                alpha = step_num * step
                widget.attributes("-alpha", alpha)
                self.window.after(20, _fade, step_num + 1)
            elif callback:
                callback()
                
        _fade()
        
    def pulse(self, widget, color1, color2, cycles=3, duration=0.5):
        """Pulse animation between two colors."""
        def _pulse(cycle=0, reverse=False):
            if cycle < cycles:
                color = color2 if reverse else color1
                widget.config(bg=color)
                self.window.after(int(duration*500), _pulse, 
                                 cycle + (1 if reverse else 0), 
                                 not reverse)
        _pulse()
        
    def slide_in(self, widget, from_x, to_x, duration=0.3):
        """Slide animation for widgets."""
        widget.place(x=from_x)
        steps = int(duration / 0.02)
        step = (to_x - from_x) / steps
        
        def _slide(step_num=0):
            if step_num <= steps:
                widget.place(x=from_x + step_num*step)
                self.window.after(20, _slide, step_num + 1)
        _slide()
        
    def animate_win(self, cells: List[tk.Widget], win_color: str, cycles=3):
        """Animate winning cells with blinking effect."""
        original_colors = [cell.cget("bg") for cell in cells]
        
        def _blink(cycle=0, reverse=False):
            if cycle < cycles:
                color = win_color if not reverse else original_colors[cycle%len(cells)]
                for cell in cells:
                    try:
                        cell.config(bg=color)
                    except tk.TclError:
                        pass
                self.window.after(200, _blink, cycle + (1 if reverse else 0), not reverse)
        _blink()
