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
import math

class RiskyBiscyGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Risky Biscy")
        self.root.configure(bg='#2c3e50')
        
        # Game state
        self.player_name = ""
        self.points = 0
        self.test_mode = False
        self.name_locked = False  # Prevent name changes after tutorial
        self.has_no_biscuits_taunt = False  # Boolean flag for name taunt
        self.selected_risk_set = tk.StringVar(value="general")  # Default selection
        
        # JSONBin.io configuration - You'll need to replace with your actual bin ID and API key
        self.jsonbin_url = "https://api.jsonbin.io/v3/b/68b2750843b1c97be9300330"  # Replace with your bin ID
        self.jsonbin_headers = {
            "Content-Type": "application/json",
            "X-Master-Key": "$2a$10$/eFQr.hrjbIla3majd3wOOL0nLxEiBTlY382wHafeQj2GhPKQfiYW",  # Replace with your API key
            "X-Bin-Meta": "false"  # Don't return metadata
        }
        
        # Define risk sets with their probabilities and actions
        self.risk_sets = {
            "general": {
                "name": "General Risks",
                "description": "Classic risk/reward gameplay",
                "sections": [
                    {"name": "Win Point!", "chance": 60, "color": "#2ecc71", "method": self.general_reward, "emoji": "🍪"},
                    {"name": "Get Pranked!", "chance": 25, "color": "#e74c3c", "method": self.general_prank, "emoji": "😈"},
                    {"name": "Nothing...", "chance": 15, "color": "#95a5a6", "method": lambda: messagebox.showinfo("Nothing", "Nothing happened... this time 😐"), "emoji": "😐"}
                ]
            },
            "sabotage": {
                "name": "Sabotage Mode", 
                "description": "Reduce another player's score by 1, but risk losing 5 points",
                "sections": [
                    {"name": "Sabotage Success!", "chance": 45, "color": "#9b59b6", "method": self.sabotage_reward, "emoji": "💀"},
                    {"name": "Lose 5 Points!", "chance": 40, "color": "#c0392b", "method": self.sabotage_prank, "emoji": "😱"},
                    {"name": "Nothing...", "chance": 15, "color": "#95a5a6", "method": lambda: messagebox.showinfo("Nothing", "Nothing happened... this time 😐"), "emoji": "😐"}
                ]
            }
        }
        
        # Wheel animation state
        self.spinning = False
        self.spin_angle = 0
        self.spin_speed = 0
        
        # DRY prank enumeration mapping for general risks
        self.general_pranks = {
            0: {
                'name': 'Desktop Files',
                'method': self.prank_desktop_files,
                'description': 'Create files on desktop'
            },
            1: {
                'name': 'Rickroll',
                'method': self.prank_rickroll,
                'description': 'Open rickroll in browser'
            },
            2: {
                'name': 'Lose Points',
                'method': self.prank_lose_points,
                'description': 'Lose 2 biscuit points'
            },
            3: {
                'name': 'Name Taunt',
                'method': self.prank_name_taunt,
                'description': 'Add taunt to your name'
            }
        }
        
        # Show tutorial first
        self.show_tutorial()
        
    def show_tutorial(self):
        """Show tutorial splash screen within the main window"""
        # Center the window for the tutorial
        width = 450
        height = 600
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.resizable(False, False)

        # Create a frame to hold all tutorial widgets for easy removal
        self.tutorial_frame = tk.Frame(self.root, bg='#2c3e50')
        self.tutorial_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Tutorial content
        tk.Label(self.tutorial_frame, text="🍪 RISKY BISCY 🍪", 
                 font=('Arial', 24, 'bold'), 
                 bg='#2c3e50', fg='#f39c12').pack(pady=20)
        
        tutorial_text = """Welcome to Risky Biscy!

Pick your risk mode, then spin the wheel.
You'll either earn biscuit points or get pranked!

Your goal is to earn as many biscuit 
points as possible and climb the 
leaderboard!"""
        
        text_label = tk.Label(self.tutorial_frame, text=tutorial_text,
                             font=('Arial', 10),
                             bg='#2c3e50', fg='#ecf0f1',
                             justify=tk.LEFT)
        text_label.pack(pady=20, padx=20)
        
        # Name input section
        tk.Label(self.tutorial_frame, text="Enter your player name:",
                 font=('Arial', 14, 'bold'),
                 bg='#2c3e50', fg='#e74c3c').pack(pady=(20, 5))
        
        self.name_entry = tk.Entry(self.tutorial_frame, font=('Arial', 14), width=20)
        self.name_entry.pack(pady=5)
        self.name_entry.focus()
        
        tk.Label(self.tutorial_frame, 
                 text="⚠️ Your name cannot be changed later! ⚠️",
                 font=('Arial', 10),
                 bg='#2c3e50', fg='#f39c12').pack(pady=5)
        
        self.name_entry.bind('<Return>', self.start_game)
        
        start_btn = tk.Button(self.tutorial_frame, text="START GAME!",
                             command=self.start_game,
                             font=('Arial', 16, 'bold'),
                             bg='#e74c3c', fg='white',
                             width=15, height=2)
        start_btn.pack(pady=20)
        
    def start_game(self, event=None):
        """Validates name, destroys tutorial, and starts the main game."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Name Required", "Please enter your name!")
            return
        if len(name) > 20:
            messagebox.showwarning("Name Too Long", "Name must be 20 characters or less!")
            return
            
        self.player_name = name
        self.name_locked = True
        
        # Remove the tutorial frame
        self.tutorial_frame.destroy()

        # Resize and re-center the main window for the game
        self.root.resizable(True, True)
        width = 1000
        height = 800
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self.setup_ui()
        self.load_leaderboard()
        
    def setup_ui(self):
        # Main container frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Left frame for game controls
        left_frame = tk.Frame(main_frame, bg='#2c3e50')
        left_frame.pack(side=tk.LEFT, fill='y', padx=(0, 10))

        # Right frame for leaderboard
        right_frame = tk.Frame(main_frame, bg='#2c3e50')
        right_frame.pack(side=tk.RIGHT, fill='both', expand=True)

        # --- Populate Left Frame ---
        # Player name display (no editing allowed after tutorial)
        self.player_display = tk.Label(left_frame, text=f"Player: {self.get_display_name()}", 
                                      font=('Arial', 14, 'bold'), 
                                      bg='#2c3e50', fg='#e74c3c')
        self.player_display.pack(pady=10)
        
        # Points display
        self.points_display = tk.Label(left_frame, text="Points: 0", 
                                      font=('Arial', 16, 'bold'), 
                                      bg='#2c3e50', fg='#2ecc71')
        self.points_display.pack(pady=10)
        
        # Risk set selection frame
        risk_selection_frame = tk.Frame(left_frame, bg='#2c3e50')
        risk_selection_frame.pack(pady=10)
        
        # Radio buttons for risk sets
        for risk_id, risk_data in self.risk_sets.items():
            radio_frame = tk.Frame(risk_selection_frame, bg='#2c3e50')
            radio_frame.pack(pady=5, fill='x', anchor='w')
            
            radio = tk.Radiobutton(radio_frame, 
                                  text=risk_data["name"], 
                                  variable=self.selected_risk_set, 
                                  value=risk_id,
                                  command=self.update_wheel,
                                  bg='#2c3e50', fg='#ecf0f1',
                                  selectcolor='#34495e',
                                  font=('Arial', 12, 'bold'))
            radio.pack(side=tk.LEFT)
            
            desc_label = tk.Label(radio_frame, 
                                 text=risk_data["description"],
                                 bg='#2c3e50', fg='#95a5a6',
                                 font=('Arial', 10))
            desc_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Wheel of Fortune
        wheel_frame = tk.Frame(left_frame, bg='#2c3e50')
        wheel_frame.pack(pady=15)
        
        # Create canvas for the wheel
        self.wheel_canvas = tk.Canvas(wheel_frame, width=300, height=300, bg='#34495e', highlightthickness=0)
        self.wheel_canvas.pack(pady=10)
        
        # Draw initial wheel
        self.update_wheel()
        
        # Confirm risk button
        self.risk_button = tk.Button(left_frame, text="SPIN THE WHEEL!", 
                                    command=self.spin_wheel,
                                    font=('Arial', 18, 'bold'),
                                    bg='#e74c3c', fg='white',
                                    width=18, height=2)
        self.risk_button.pack(pady=15)
        
        # Test mode controls
        test_frame = tk.Frame(left_frame, bg='#2c3e50')
        test_frame.pack(pady=10)
        
        self.test_mode_var = tk.BooleanVar()
        test_checkbox = tk.Checkbutton(test_frame, text="Test Mode", 
                                      variable=self.test_mode_var,
                                      command=self.toggle_test_mode,
                                      bg='#2c3e50', fg='#ecf0f1',
                                      selectcolor='#34495e')
        test_checkbox.pack(side=tk.LEFT)
        
        self.test_buttons_frame = tk.Frame(left_frame, bg='#2c3e50')
        self.test_buttons_frame.pack(pady=5)
        
        # Test buttons (initially hidden)
        self.test_buttons = []
        test_options = (list(self.general_pranks.values()) + 
                       [{'name': 'Gain Point', 'method': self.test_gain_point},
                        {'name': 'Sabotage Success', 'method': self.test_sabotage_success},
                        {'name': 'Sabotage Fail', 'method': self.test_sabotage_fail}])
        
        for i, option in enumerate(test_options):
            btn = tk.Button(self.test_buttons_frame, text=option['name'],
                           command=lambda method=option['method']: method(),
                           bg='#9b59b6', fg='white', font=('Arial', 8))
            btn.pack(side=tk.LEFT, padx=2)
            btn.pack_forget()  # Hide initially
            self.test_buttons.append(btn)
        
        # Test mode name change button (only in test mode)
        self.test_name_btn = tk.Button(self.test_buttons_frame, text="Change Name",
                                      command=self.test_change_name,
                                      bg='#e67e22', fg='white', font=('Arial', 8))
        self.test_name_btn.pack(side=tk.LEFT, padx=2)
        self.test_name_btn.pack_forget()
        self.test_buttons.append(self.test_name_btn)
        
        # --- Populate Right Frame ---
        leaderboard_frame = tk.Frame(right_frame, bg='#2c3e50')
        leaderboard_frame.pack(fill='both', expand=True)
        
        tk.Label(leaderboard_frame, text="🏆 LEADERBOARD 🏆", 
                font=('Arial', 16, 'bold'), bg='#2c3e50', fg='#f39c12').pack()
        
        # Leaderboard listbox with scrollbar
        lb_frame = tk.Frame(leaderboard_frame, bg='#2c3e50')
        lb_frame.pack(pady=10, fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(lb_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.leaderboard_listbox = tk.Listbox(lb_frame, yscrollcommand=scrollbar.set,
                                             bg='#34495e', fg='#ecf0f1',
                                             font=('Arial', 12))
        self.leaderboard_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.leaderboard_listbox.yview)
        
        # Refresh leaderboard button
        refresh_btn = tk.Button(leaderboard_frame, text="Refresh Leaderboard",
                               command=self.load_leaderboard,
                               bg='#27ae60', fg='white', font=('Arial', 10))
        refresh_btn.pack(pady=5)
    
    def get_display_name(self):
        """Get the display name with taunt suffix if applicable"""
        if self.has_no_biscuits_taunt:
            return f"{self.player_name} has no biscuits"
        return self.player_name
    
    def toggle_test_mode(self):
        self.test_mode = self.test_mode_var.get()
        if self.test_mode:
            for btn in self.test_buttons:
                btn.pack(side=tk.LEFT, padx=2)
        else:
            for btn in self.test_buttons:
                btn.pack_forget()
    
    def test_change_name(self):
        """Allow name change only in test mode"""
        new_name = simpledialog.askstring("Change Name", "Enter new name:")
        if new_name and new_name.strip():
            self.player_name = new_name.strip()
            self.has_no_biscuits_taunt = False  # Reset taunt
            self.player_display.config(text=f"Player: {self.get_display_name()}")
    
    def test_gain_point(self):
        """Test function to gain a point"""
        self.points += 1
        self.update_points_display()
        messagebox.showinfo("Test", "🍪 Gained 1 biscuit point! 🍪")
        self.update_leaderboard()
    
    def test_sabotage_success(self):
        """Test function for successful sabotage"""
        self.sabotage_reward()
    
    def test_sabotage_fail(self):
        """Test function for failed sabotage"""
        self.sabotage_prank()
    
    def update_wheel(self):
        """Update the wheel display based on selected risk set"""
        if not hasattr(self, 'wheel_canvas'):
            return
            
        self.wheel_canvas.delete("all")
        
        selected_risk = self.selected_risk_set.get()
        if selected_risk not in self.risk_sets:
            return
            
        sections = self.risk_sets[selected_risk]["sections"]
        
        # Calculate angles for each section
        total_angle = 0
        center_x, center_y = 150, 150
        radius = 120
        
        # Draw wheel sections
        for section in sections:
            section_angle = (section["chance"] / 100.0) * 360
            start_angle = total_angle
            
            # Draw the pie slice
            self.wheel_canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=start_angle, extent=section_angle,
                fill=section["color"], outline='white', width=2
            )
            
            # Add text labels
            text_angle = math.radians(start_angle + section_angle / 2)
            text_radius = radius * 0.7
            text_x = center_x + text_radius * math.cos(text_angle)
            text_y = center_y - text_radius * math.sin(text_angle)  # Negative because canvas Y is inverted
            
            # Add emoji
            emoji_x = center_x + (radius * 0.85) * math.cos(text_angle)
            emoji_y = center_y - (radius * 0.85) * math.sin(text_angle)
            self.wheel_canvas.create_text(emoji_x, emoji_y, text=section["emoji"], 
                                        font=('Arial', 20), fill='white')
            
            # Add percentage text
            self.wheel_canvas.create_text(text_x, text_y, text=f"{section['chance']}%", 
                                        font=('Arial', 12, 'bold'), fill='white')
            
            total_angle += section_angle
        
        # Draw center circle
        center_radius = 15
        self.wheel_canvas.create_oval(
            center_x - center_radius, center_y - center_radius,
            center_x + center_radius, center_y + center_radius,
            fill='#2c3e50', outline='white', width=2
        )
        
        # Draw pointer (arrow pointing down)
        pointer_points = [
            center_x, center_y - radius - 20,  # Top point
            center_x - 15, center_y - radius - 5,  # Left point
            center_x + 15, center_y - radius - 5   # Right point
        ]
        self.wheel_canvas.create_polygon(pointer_points, fill='#f39c12', outline='white', width=2)
    
    def spin_wheel(self):
        """Spin the wheel with animation"""
        if self.spinning or self.test_mode:
            if self.test_mode:
                messagebox.showinfo("Test Mode", "Use the test buttons below!")
            return
        
        self.spinning = True
        self.risk_button.config(state='disabled', text='SPINNING...')
        
        # Determine final outcome first
        selected_risk = self.selected_risk_set.get()
        sections = self.risk_sets[selected_risk]["sections"]
        
        # Calculate outcome
        roll = random.randint(1, 100)
        cumulative_chance = 0
        selected_section = None
        
        for section in sections:
            cumulative_chance += section["chance"]
            if roll <= cumulative_chance:
                selected_section = section
                break
        
        if not selected_section:
            selected_section = sections[-1]  # Fallback
        
        # Calculate target angle (where the pointer should land)
        section_start_angle = 0
        for section in sections:
            if section == selected_section:
                # Land somewhere in this section
                section_angle = (section["chance"] / 100.0) * 360
                target_angle = section_start_angle + random.uniform(section_angle * 0.1, section_angle * 0.9)
                break
            section_start_angle += (section["chance"] / 100.0) * 360
        
        # Animation parameters
        self.spin_speed = 20  # Initial speed
        total_spins = random.randint(3, 6) * 360  # Multiple full rotations
        self.target_angle = (360 - target_angle + total_spins) % 360  # Adjust for pointer position
        self.current_spin_angle = 0
        
        # Start animation
        self.animate_spin(selected_section)
    
    def animate_spin(self, final_section):
        """Animate the wheel spinning"""
        if not self.spinning:
            return
        
        # Update spin angle
        self.current_spin_angle += self.spin_speed
        
        # Gradually slow down as we approach the target
        if self.current_spin_angle >= self.target_angle - 180:
            self.spin_speed *= 0.95  # Slow down
        
        # Stop when we've reached the target and speed is low enough
        if self.current_spin_angle >= self.target_angle and self.spin_speed < 1:
            self.spinning = False
            self.risk_button.config(state='normal', text='SPIN THE WHEEL!')
            
            # Execute the outcome after a brief pause
            self.root.after(500, lambda: self.execute_outcome(final_section))
            return
        
        # Redraw the wheel with rotation
        self.draw_rotated_wheel(self.current_spin_angle)
        
        # Continue animation
        self.root.after(50, lambda: self.animate_spin(final_section))
    
    def draw_rotated_wheel(self, rotation_angle):
        """Draw the wheel rotated by the given angle"""
        self.wheel_canvas.delete("all")
        
        selected_risk = self.selected_risk_set.get()
        sections = self.risk_sets[selected_risk]["sections"]
        
        total_angle = rotation_angle
        center_x, center_y = 150, 150
        radius = 120
        
        # Draw wheel sections
        for section in sections:
            section_angle = (section["chance"] / 100.0) * 360
            start_angle = total_angle
            
            # Draw the pie slice
            self.wheel_canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=start_angle, extent=section_angle,
                fill=section["color"], outline='white', width=2
            )
            
            # Add text labels
            text_angle = math.radians(start_angle + section_angle / 2)
            text_radius = radius * 0.7
            text_x = center_x + text_radius * math.cos(text_angle)
            text_y = center_y - text_radius * math.sin(text_angle)
            
            # Add emoji
            emoji_x = center_x + (radius * 0.85) * math.cos(text_angle)
            emoji_y = center_y - (radius * 0.85) * math.sin(text_angle)
            self.wheel_canvas.create_text(emoji_x, emoji_y, text=section["emoji"], 
                                        font=('Arial', 20), fill='white')
            
            # Add percentage text
            self.wheel_canvas.create_text(text_x, text_y, text=f"{section['chance']}%", 
                                        font=('Arial', 12, 'bold'), fill='white')
            
            total_angle += section_angle
        
        # Draw center circle
        center_radius = 15
        self.wheel_canvas.create_oval(
            center_x - center_radius, center_y - center_radius,
            center_x + center_radius, center_y + center_radius,
            fill='#2c3e50', outline='white', width=2
        )
        
        # Draw pointer (always pointing down, doesn't rotate)
        pointer_points = [
            center_x, center_y - radius - 20,
            center_x - 15, center_y - radius - 5,
            center_x + 15, center_y - radius - 5
        ]
        self.wheel_canvas.create_polygon(pointer_points, fill='#f39c12', outline='white', width=2)
    
    def execute_outcome(self, section):
        """Execute the outcome that the wheel landed on"""
        section["method"]()
    
    def risk_it(self):
        """Legacy method - now handled by spin_wheel"""
        self.spin_wheel()
    
    # General risk set methods
    def general_reward(self):
        """General risk set reward: gain 1 point"""
        self.points += 1
        self.update_points_display()
        messagebox.showinfo("Success!", "🍪 You earned a biscuit point! 🍪")
        self.update_leaderboard()
    
    def general_prank(self):
        """General risk set prank: execute random general prank"""
        prank_id = random.choice(list(self.general_pranks.keys()))
        self.execute_general_prank(prank_id)
    
    # Sabotage risk set methods
    def sabotage_reward(self):
        """Sabotage risk set reward: reduce another player's score by 1"""
        try:
            # Get current leaderboard
            response = requests.get(self.jsonbin_url, headers=self.jsonbin_headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'record' in data:
                    leaderboard = data['record'].get('leaderboard', [])
                else:
                    leaderboard = data.get('leaderboard', [])
                
                # Filter out current player and players with 0 points
                other_players = [p for p in leaderboard if p['name'] != self.player_name and p['points'] > 0]
                
                if other_players:
                    # Select random player to sabotage
                    target = random.choice(other_players)
                    target['points'] = max(0, target['points'] - 1)
                    
                    # Update leaderboard
                    leaderboard.sort(key=lambda x: x['points'], reverse=True)
                    leaderboard = leaderboard[:20]
                    
                    update_data = {'leaderboard': leaderboard}
                    requests.put(self.jsonbin_url, json=update_data, headers=self.jsonbin_headers, timeout=10)
                    
                    messagebox.showinfo("Sabotage Success!", f"💀 You reduced {target['name']}'s score by 1 point! 💀")
                    self.load_leaderboard()  # Refresh to show changes
                else:
                    messagebox.showinfo("No Target", "🤷 No other players to sabotage! You get nothing.")
            else:
                messagebox.showinfo("Connection Error", "Could not connect to leaderboard for sabotage!")
                
        except Exception as e:
            print(f"Sabotage failed: {e}")
            messagebox.showinfo("Sabotage Failed", "Could not execute sabotage!")
    
    def sabotage_prank(self):
        """Sabotage risk set prank: lose 5 points"""
        self.points = self.points - 5
        self.update_points_display()
        messagebox.showwarning("SABOTAGE BACKFIRED!", "😱 Your sabotage attempt failed! You lost 5 points! 😱")
        self.update_leaderboard()
    
    def execute_general_prank(self, prank_id):
        """Execute general prank by ID using the DRY mapping"""
        if prank_id in self.general_pranks:
            self.general_pranks[prank_id]['method']()
        else:
            messagebox.showinfo("Error", "Unknown prank!")
    
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
            
            if not desktop_path:
                messagebox.showinfo("Prank Failed", "Could not find desktop folder!")
                return
            
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
        self.points = self.points - 2
        self.update_points_display()
        messagebox.showwarning("PRANKED!", "😭 You lost 2 biscuit points! 😭")
        self.update_leaderboard()
    
    def prank_name_taunt(self):
        """Add 'has no biscuits' taunt flag (client-side only)"""
        if not self.has_no_biscuits_taunt:
            self.has_no_biscuits_taunt = True
            self.player_display.config(text=f"Player: {self.get_display_name()}")
            messagebox.showwarning("PRANKED!", "🏷️ Your name got a special addition! 🏷️")
            # Note: We don't update leaderboard here since the server name stays the same
    
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
        """Update player score on leaderboard using the original name (not display name)"""
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
            
            # Update or add player using original name (not display name with taunt)
            player_found = False
            for player in leaderboard:
                if player['name'] == self.player_name:  # Use original name
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
            medal = f"{i}."
            
            # Show display name if it's the current player
            display_name = player['name']
            if player['name'] == self.player_name:
                display_name = self.get_display_name()
            
            entry = f"{medal} {display_name} - {player['points']} points"
            self.leaderboard_listbox.insert(tk.END, entry)
            
            # Highlight current player
            if player['name'] == self.player_name:
                self.leaderboard_listbox.selection_set(i-1)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = RiskyBiscyGame()
    game.run()
