import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import requests
import json
import os
import webbrowser
import subprocess
import platform
from threading import Thread
import time

class RiskyBiscyGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Risky Biscy - Risk it for a Biscuit!")
        self.root.geometry("500x600")
        self.root.configure(bg='#2c3e50')
        
        # Game state
        self.player_name = ""
        self.points = 0
        self.test_mode = False
        
        # JSONBin.io configuration - You'll need to replace with your actual bin ID and API key
        self.jsonbin_url = "https://api.jsonbin.io/v3/b/68b2750843b1c97be9300330"  # Replace with your bin ID
        self.jsonbin_headers = {
            "Content-Type": "application/json",
            "X-Master-Key": "$2a$10$/eFQr.hrjbIla3majd3wOOL0nLxEiBTlY382wHafeQj2GhPKQfiYW",  # Replace with your API key
            "X-Bin-Meta": "false"  # Don't return metadata
        }
        
        # Prank probabilities (out of 100)
        self.prank_chance = 25  # 25% chance of prank
        self.point_chance = 60  # 60% chance of point
        self.nothing_chance = 15  # 15% chance of nothing
        
        self.setup_ui()
        self.load_leaderboard()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="🍪 RISKY BISCY 🍪", 
                              font=('Arial', 20, 'bold'), 
                              bg='#2c3e50', fg='#f39c12')
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(self.root, text="Risk it for a Biscuit!", 
                                 font=('Arial', 12), 
                                 bg='#2c3e50', fg='#ecf0f1')
        subtitle_label.pack(pady=5)
        
        # Player name input
        name_frame = tk.Frame(self.root, bg='#2c3e50')
        name_frame.pack(pady=10)
        
        tk.Label(name_frame, text="Your Name:", font=('Arial', 12), 
                bg='#2c3e50', fg='#ecf0f1').pack(side=tk.LEFT)
        
        self.name_entry = tk.Entry(name_frame, font=('Arial', 12), width=20)
        self.name_entry.pack(side=tk.LEFT, padx=10)
        self.name_entry.bind('<Return>', self.set_name)
        
        set_name_btn = tk.Button(name_frame, text="Set Name", command=self.set_name,
                                bg='#3498db', fg='white', font=('Arial', 10))
        set_name_btn.pack(side=tk.LEFT, padx=5)
        
        # Current player display
        self.player_display = tk.Label(self.root, text="Enter your name to start!", 
                                      font=('Arial', 14, 'bold'), 
                                      bg='#2c3e50', fg='#e74c3c')
        self.player_display.pack(pady=10)
        
        # Points display
        self.points_display = tk.Label(self.root, text="Points: 0", 
                                      font=('Arial', 16, 'bold'), 
                                      bg='#2c3e50', fg='#2ecc71')
        self.points_display.pack(pady=10)
        
        # Main button
        self.risk_button = tk.Button(self.root, text="RISK IT!", 
                                    command=self.risk_it,
                                    font=('Arial', 20, 'bold'),
                                    bg='#e74c3c', fg='white',
                                    width=15, height=2,
                                    state='disabled')
        self.risk_button.pack(pady=20)
        
        # Test mode controls
        test_frame = tk.Frame(self.root, bg='#2c3e50')
        test_frame.pack(pady=10)
        
        self.test_mode_var = tk.BooleanVar()
        test_checkbox = tk.Checkbutton(test_frame, text="Test Mode", 
                                      variable=self.test_mode_var,
                                      command=self.toggle_test_mode,
                                      bg='#2c3e50', fg='#ecf0f1',
                                      selectcolor='#34495e')
        test_checkbox.pack(side=tk.LEFT)
        
        self.test_buttons_frame = tk.Frame(self.root, bg='#2c3e50')
        self.test_buttons_frame.pack(pady=5)
        
        # Test buttons (initially hidden)
        self.test_buttons = []
        test_pranks = ["Desktop Files", "Rickroll", "Lose Points", "Name Change"]
        for i, prank in enumerate(test_pranks):
            btn = tk.Button(self.test_buttons_frame, text=prank,
                           command=lambda x=i: self.test_prank(x),
                           bg='#9b59b6', fg='white', font=('Arial', 8))
            btn.pack(side=tk.LEFT, padx=2)
            btn.pack_forget()  # Hide initially
            self.test_buttons.append(btn)
        
        # Leaderboard
        leaderboard_frame = tk.Frame(self.root, bg='#2c3e50')
        leaderboard_frame.pack(pady=20, fill='both', expand=True)
        
        tk.Label(leaderboard_frame, text="🏆 LEADERBOARD 🏆", 
                font=('Arial', 16, 'bold'), bg='#2c3e50', fg='#f39c12').pack()
        
        # Leaderboard listbox with scrollbar
        lb_frame = tk.Frame(leaderboard_frame, bg='#2c3e50')
        lb_frame.pack(pady=10, fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(lb_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.leaderboard_listbox = tk.Listbox(lb_frame, yscrollcommand=scrollbar.set,
                                             bg='#34495e', fg='#ecf0f1',
                                             font=('Arial', 10))
        self.leaderboard_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.leaderboard_listbox.yview)
        
        # Refresh leaderboard button
        refresh_btn = tk.Button(leaderboard_frame, text="Refresh Leaderboard",
                               command=self.load_leaderboard,
                               bg='#27ae60', fg='white', font=('Arial', 10))
        refresh_btn.pack(pady=5)
        
    def set_name(self, event=None):
        name = self.name_entry.get().strip()
        if name:
            self.player_name = name
            self.player_display.config(text=f"Player: {self.player_name}")
            self.risk_button.config(state='normal')
        
    def toggle_test_mode(self):
        self.test_mode = self.test_mode_var.get()
        if self.test_mode:
            for btn in self.test_buttons:
                btn.pack(side=tk.LEFT, padx=2)
        else:
            for btn in self.test_buttons:
                btn.pack_forget()
    
    def test_prank(self, prank_index):
        if not self.player_name:
            messagebox.showwarning("Warning", "Please set your name first!")
            return
            
        if prank_index == 0:
            self.prank_desktop_files()
        elif prank_index == 1:
            self.prank_rickroll()
        elif prank_index == 2:
            self.prank_lose_points()
        elif prank_index == 3:
            self.prank_name_change()
    
    def risk_it(self):
        if not self.player_name:
            messagebox.showwarning("Warning", "Please set your name first!")
            return
            
        if self.test_mode:
            messagebox.showinfo("Test Mode", "Use the test buttons below!")
            return
        
        # Determine outcome
        roll = random.randint(1, 100)
        
        if roll <= self.prank_chance:
            # Execute random prank
            prank_type = random.randint(0, 3)
            self.execute_prank(prank_type)
        elif roll <= self.prank_chance + self.point_chance:
            # Give point
            self.points += 1
            self.update_points_display()
            messagebox.showinfo("Success!", "🍪 You earned a biscuit point! 🍪")
            self.update_leaderboard()
        else:
            # Nothing happens
            messagebox.showinfo("Nothing", "Nothing happened... this time 😏")
    
    def execute_prank(self, prank_type):
        if prank_type == 0:
            self.prank_desktop_files()
        elif prank_type == 1:
            self.prank_rickroll()
        elif prank_type == 2:
            self.prank_lose_points()
        elif prank_type == 3:
            self.prank_name_change()
    
    def prank_desktop_files(self):
        """Create blank files on desktop"""
        try:
            # Get the path to the user's home directory (works on all OS)
            home_dir = os.path.expanduser("~")
            
            # List of possible desktop paths relative to the home directory.
            # This handles standard setups and common cloud-synced folders like OneDrive.
            possible_desktop_paths = [
                os.path.join(home_dir, "Desktop"),
                os.path.join(home_dir, "OneDrive", "Desktop")
            ]
            
            desktop_path = None
            for path in possible_desktop_paths:
                if os.path.isdir(path):
                    desktop_path = path
                    break
            
            file_names = ["you_got_pranked.txt", "no_biscuits_for_you.txt", 
                         "risky_business.txt", "shouldnt_have_risked_it.txt"]
            
            for filename in file_names:
                filepath = os.path.join(desktop_path, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("You got pranked by Risky Biscy!\n")
                    f.write("Maybe you shouldn't have risked it...\n")
                    f.write("Risk it for a biscuit - but sometimes you get pranked!\n")
                    
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
        self.points = max(0, self.points - 2)
        self.update_points_display()
        messagebox.showwarning("PRANKED!", "😭 You lost 2 biscuit points! 😭")
        self.update_leaderboard()
    
    def prank_name_change(self):
        """Add 'has no biscuits' to username"""
        if " has no biscuits" not in self.player_name:
            self.player_name += " has no biscuits"
            self.player_display.config(text=f"Player: {self.player_name}")
            messagebox.showwarning("PRANKED!", "🏷️ Your name got a special addition! 🏷️")
            self.update_leaderboard()
    
    def update_points_display(self):
        self.points_display.config(text=f"Points: {self.points}")
    
    def load_leaderboard(self):
        """Load leaderboard from JSONBin.io"""
        try:
            # Note: You'll need to create a JSONBin.io account and replace the URL and headers
            response = requests.get(self.jsonbin_url, headers=self.jsonbin_headers, timeout=10)
            print(f"Load response status: {response.status_code}")  # Debug
            print(f"Load response content: {response.text[:200]}...")  # Debug
            
            if response.status_code == 200:
                data = response.json()
                # Handle different JSONBin response formats
                if 'record' in data:
                    leaderboard = data['record'].get('leaderboard', [])
                else:
                    leaderboard = data.get('leaderboard', [])
                self.display_leaderboard(leaderboard)
            else:
                print(f"Failed to load leaderboard: {response.status_code}")
                self.display_leaderboard([])
        except Exception as e:
            print(f"Failed to load leaderboard: {e}")
            self.display_leaderboard([])
    
    def update_leaderboard(self):
        """Update player score on leaderboard"""
        try:
            # First, get current leaderboard
            response = requests.get(self.jsonbin_url, headers=self.jsonbin_headers, timeout=10)
            print(f"Get response status: {response.status_code}")  # Debug
            
            if response.status_code == 200:
                data = response.json()
                # Handle different JSONBin response formats
                if 'record' in data:
                    leaderboard = data['record'].get('leaderboard', [])
                else:
                    leaderboard = data.get('leaderboard', [])
            else:
                leaderboard = []
            
            # Update or add player
            player_found = False
            for player in leaderboard:
                if player['name'] == self.player_name:
                    player['points'] = self.points
                    player_found = True
                    break
            
            if not player_found:
                leaderboard.append({'name': self.player_name, 'points': self.points})
            
            # Sort by points (descending)
            leaderboard.sort(key=lambda x: x['points'], reverse=True)
            
            # Keep only top 20
            leaderboard = leaderboard[:20]
            
            # Update JSONBin
            update_data = {'leaderboard': leaderboard}
            update_response = requests.put(self.jsonbin_url, 
                        json=update_data, 
                        headers=self.jsonbin_headers, 
                        timeout=10)
            
            print(f"Update response status: {update_response.status_code}")  # Debug
            print(f"Update response content: {update_response.text[:200]}...")  # Debug
            
            self.display_leaderboard(leaderboard)
            
        except Exception as e:
            print(f"Failed to update leaderboard: {e}")
            import traceback
            traceback.print_exc()  # More detailed error info
    
    def display_leaderboard(self, leaderboard):
        """Display leaderboard in the listbox"""
        self.leaderboard_listbox.delete(0, tk.END)
        
        for i, player in enumerate(leaderboard, 1):
            if i <= 3:
                medals = ["🥇", "🥈", "🥉"]
                medal = medals[i-1]
            else:
                medal = f"{i}."
            
            entry = f"{medal} {player['name']} - {player['points']} points"
            self.leaderboard_listbox.insert(tk.END, entry)
            
            # Highlight current player
            if player['name'] == self.player_name:
                self.leaderboard_listbox.selection_set(i-1)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = RiskyBiscyGame()
    game.run()
