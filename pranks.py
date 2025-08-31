import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import webbrowser
import random

class PrankHandler:
    def __init__(self, game_instance):
        """
        Initializes the PrankHandler.
        :param game_instance: An instance of the main RiskyBiscyGame class.
        """
        self.game = game_instance

        # DRY prank enumeration mapping for general risks
        self.general_pranks = {
            0: {'name': 'Desktop Files', 'method': self.prank_desktop_files},
            1: {'name': 'Rickroll', 'method': self.prank_rickroll},
            2: {'name': 'Lose Points', 'method': self.prank_lose_points},
            3: {'name': 'Name Taunt', 'method': self.prank_name_taunt}
        }

    def get_risk_sets(self):
        """Returns the dictionary defining all risk sets and their behaviors."""
        return {
            "general": {
                "name": "General Risks",
                "description": "Classic risk/reward gameplay",
                "sections": [
                    {"name": "Win Point!", "chance": 60, "color": "#2ecc71", "method": self.game.general_reward, "emoji": "🍪"},
                    {"name": "Get Pranked!", "chance": 25, "color": "#e74c3c", "method": self.execute_random_general_prank, "emoji": "😈"},
                    {"name": "Nothing...", "chance": 15, "color": "#95a5a6", "method": lambda: messagebox.showinfo("Nothing", "Nothing happened... this time 😐"), "emoji": "😐"}
                ]
            },
            "sabotage": {
                "name": "Sabotage Mode", 
                "description": "Reduce another player's score by 1, but risk losing 5 points",
                "sections": [
                    {"name": "Sabotage Success!", "chance": 45, "color": "#9b59b6", "method": self.game.sabotage_reward, "emoji": "💀"},
                    {"name": "Lose 5 Points!", "chance": 40, "color": "#c0392b", "method": self.game.sabotage_prank, "emoji": "😱"},
                    {"name": "Nothing...", "chance": 15, "color": "#95a5a6", "method": lambda: messagebox.showinfo("Nothing", "Nothing happened... this time 😐"), "emoji": "😐"}
                ]
            }
        }

    def execute_random_general_prank(self):
        """General risk set prank: execute random general prank"""
        prank_id = random.choice(list(self.general_pranks.keys()))
        self.general_pranks[prank_id]['method']()

    # --- PRANK IMPLEMENTATIONS ---
    def prank_desktop_files(self):
        """Create blank files on desktop"""
        try:
            home_dir = os.path.expanduser("~")
            possible_desktop_paths = [os.path.join(home_dir, "Desktop"), os.path.join(home_dir, "OneDrive", "Desktop")]
            desktop_path = next((path for path in possible_desktop_paths if os.path.isdir(path)), None)
            
            if not desktop_path:
                messagebox.showinfo("Prank Failed", "Could not find desktop folder!")
                return
            
            file_names = ["you_got_pranked.txt", "no_biscuits_for_you.txt", "risky_business.txt", "shouldnt_have_risked_it.txt"]
            for filename in file_names:
                with open(os.path.join(desktop_path, filename), 'w', encoding='utf-8') as f:
                    f.write("You got pranked by Risky Biscy!\n")
            messagebox.showwarning("PRANKED!", "Your desktop got some new 'friends'!")
        except Exception as e:
            messagebox.showinfo("Prank Failed", f"Desktop prank failed: {e}")

    def prank_rickroll(self):
        """Open browser with rickroll"""
        try:
            webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            messagebox.showwarning("PRANKED!", "🎵 Never gonna give you up! 🎵")
        except Exception as e:
            messagebox.showinfo("Prank Failed", f"Rickroll prank failed: {e}")

    def prank_lose_points(self):
        """Lose 2 points"""
        self.game.points -= 2
        self.game.update_points_display()
        messagebox.showwarning("PRANKED!", "😭 You lost 2 biscuit points! 😭")
        self.game.update_leaderboard()

    def prank_name_taunt(self):
        """Add 'has no biscuits' taunt flag (client-side only)"""
        if not self.game.has_no_biscuits_taunt:
            self.game.has_no_biscuits_taunt = True
            self.game.player_display.config(text=f"Player: {self.game.get_display_name()}")
            messagebox.showwarning("PRANKED!", "🏷️ Your name got a special addition! 🏷️")

    # --- TEST MODE UI AND LOGIC ---
    def create_test_ui(self, parent_frame):
        """Creates and packs the test mode UI elements."""
        test_frame = tk.Frame(parent_frame, bg='#2c3e50')
        test_frame.pack(pady=10)
        
        test_mode_var = tk.BooleanVar()
        test_checkbox = tk.Checkbutton(test_frame, text="Test Mode", variable=test_mode_var,
                                      command=self.game.toggle_test_mode, bg='#2c3e50', fg='#ecf0f1',
                                      selectcolor='#34495e')
        test_checkbox.pack(side=tk.LEFT)
        
        test_buttons_frame = tk.Frame(parent_frame, bg='#2c3e50')
        test_buttons_frame.pack(pady=5)
        
        test_buttons = []
        test_options = [{'name': 'Desktop Files', 'method': self.prank_desktop_files},
                        {'name': 'Rickroll', 'method': self.prank_rickroll},
                        {'name': 'Lose Points', 'method': self.prank_lose_points},
                        {'name': 'Name Taunt', 'method': self.prank_name_taunt},
                        {'name': 'Gain Point', 'method': self.test_gain_point},
                        {'name': 'Sabotage Success', 'method': self.test_sabotage_success},
                        {'name': 'Sabotage Fail', 'method': self.test_sabotage_fail}]
        
        for option in test_options:
            btn = tk.Button(test_buttons_frame, text=option['name'], command=option['method'],
                           bg='#9b59b6', fg='white', font=('Arial', 8))
            btn.pack_forget()  # Hide initially
            test_buttons.append(btn)
        
        test_name_btn = tk.Button(test_buttons_frame, text="Change Name", command=self.test_change_name,
                                  bg='#e67e22', fg='white', font=('Arial', 8))
        test_name_btn.pack_forget()
        test_buttons.append(test_name_btn)

        self.test_buttons_frame = test_buttons_frame # Store frame for visibility toggling
        return test_mode_var, test_buttons
        
    def toggle_test_buttons_visibility(self, show, buttons):
        """Shows or hides the test buttons."""
        for btn in buttons:
            if show:
                btn.pack(side=tk.LEFT, padx=2)
            else:
                btn.pack_forget()

    def test_gain_point(self):
        """Test function to gain a point"""
        self.game.points += 1
        self.game.update_points_display()
        messagebox.showinfo("Test", "🍪 Gained 1 biscuit point! 🍪")
        self.game.update_leaderboard()

    def test_sabotage_success(self):
        """Test function for successful sabotage"""
        self.game.sabotage_reward()

    def test_sabotage_fail(self):
        """Test function for failed sabotage"""
        self.game.sabotage_prank()

    def test_change_name(self):
        """Allow name change only in test mode"""
        new_name = simpledialog.askstring("Change Name", "Enter new name:")
        if new_name and new_name.strip():
            self.game.player_name = new_name.strip()
            self.game.has_no_biscuits_taunt = False
            self.game.player_display.config(text=f"Player: {self.game.get_display_name()}")
