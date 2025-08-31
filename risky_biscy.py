import tkinter as tk
from tkinter import messagebox
import random
import requests
import math
from pranks import PrankHandler

class RiskyBiscyGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Risky Biscy")
        self.root.configure(bg='#2c3e50')
        
        # Game state
        self.player_name = ""
        self.points = 0
        self.test_mode = False
        self.name_locked = False
        self.has_no_biscuits_taunt = False
        self.selected_risk_set = tk.StringVar(value="general")
        
        # JSONBin.io configuration
        self.jsonbin_url = "https://api.jsonbin.io/v3/b/68b2750843b1c97be9300330"
        self.jsonbin_headers = {
            "Content-Type": "application/json",
            "X-Master-Key": "$2a$10$/eFQr.hrjbIla3majd3wOOL0nLxEiBTlY382wHafeQj2GhPKQfiYW",
            "X-Bin-Meta": "false"
        }
        
        # Prank and Risk Set Handling
        self.prank_handler = PrankHandler(self)
        self.risk_sets = self.prank_handler.get_risk_sets()
        
        # Wheel animation state
        self.spinning = False
        self.spin_angle = 0
        self.spin_speed = 0
        
        # Show tutorial first
        self.show_tutorial()
        
    def show_tutorial(self):
        """Show tutorial splash screen within the main window"""
        width, height = 450, 600
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.resizable(False, False)

        self.tutorial_frame = tk.Frame(self.root, bg='#2c3e50')
        self.tutorial_frame.pack(pady=20, padx=20, fill="both", expand=True)

        tk.Label(self.tutorial_frame, text="🍪 RISKY BISCY 🍪", 
                 font=('Arial', 24, 'bold'), bg='#2c3e50', fg='#f39c12').pack(pady=20)
        
        tutorial_text = "Welcome to Risky Biscy!\n\nPick your risk mode, then spin the wheel.\nYou'll either earn biscuit points or get pranked!\n\nYour goal is to earn as many biscuit \npoints as possible and climb the \nleaderboard!"
        tk.Label(self.tutorial_frame, text=tutorial_text, font=('Arial', 10),
                 bg='#2c3e50', fg='#ecf0f1', justify=tk.LEFT).pack(pady=20, padx=20)
        
        tk.Label(self.tutorial_frame, text="Enter your player name:", font=('Arial', 14, 'bold'),
                 bg='#2c3e50', fg='#e74c3c').pack(pady=(20, 5))
        
        self.name_entry = tk.Entry(self.tutorial_frame, font=('Arial', 14), width=20)
        self.name_entry.pack(pady=5)
        self.name_entry.focus()
        
        tk.Label(self.tutorial_frame, text="⚠️ Your name cannot be changed later! ⚠️",
                 font=('Arial', 10), bg='#2c3e50', fg='#f39c12').pack(pady=5)
        
        self.name_entry.bind('<Return>', self.start_game)
        
        start_btn = tk.Button(self.tutorial_frame, text="START GAME!", command=self.start_game,
                             font=('Arial', 16, 'bold'), bg='#e74c3c', fg='white',
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
        self.tutorial_frame.destroy()

        self.root.resizable(True, True)
        width, height = 1000, 800
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self.setup_ui()
        self.load_leaderboard()
        
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        left_frame = tk.Frame(main_frame, bg='#2c3e50')
        left_frame.pack(side=tk.LEFT, fill='y', padx=(0, 10))

        right_frame = tk.Frame(main_frame, bg='#2c3e50')
        right_frame.pack(side=tk.RIGHT, fill='both', expand=True)

        self.player_display = tk.Label(left_frame, text=f"Player: {self.get_display_name()}", 
                                      font=('Arial', 14, 'bold'), bg='#2c3e50', fg='#e74c3c')
        self.player_display.pack(pady=10)
        
        self.points_display = tk.Label(left_frame, text="Points: 0", font=('Arial', 16, 'bold'), 
                                      bg='#2c3e50', fg='#2ecc71')
        self.points_display.pack(pady=10)
        
        risk_selection_frame = tk.Frame(left_frame, bg='#2c3e50')
        risk_selection_frame.pack(pady=10)
        
        for risk_id, risk_data in self.risk_sets.items():
            radio_frame = tk.Frame(risk_selection_frame, bg='#2c3e50')
            radio_frame.pack(pady=5, fill='x', anchor='w')
            tk.Radiobutton(radio_frame, text=risk_data["name"], variable=self.selected_risk_set, 
                           value=risk_id, command=self.update_wheel, bg='#2c3e50', 
                           fg='#ecf0f1', selectcolor='#34495e', font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
            tk.Label(radio_frame, text=risk_data["description"], bg='#2c3e50', fg='#95a5a6',
                     font=('Arial', 10)).pack(side=tk.LEFT, padx=(10, 0))
        
        self.wheel_canvas = tk.Canvas(left_frame, width=300, height=300, bg='#34495e', highlightthickness=0)
        self.wheel_canvas.pack(pady=15)
        self.update_wheel()
        
        self.risk_button = tk.Button(left_frame, text="SPIN THE WHEEL!", command=self.spin_wheel,
                                    font=('Arial', 18, 'bold'), bg='#e74c3c', fg='white',
                                    width=18, height=2)
        self.risk_button.pack(pady=15)
        
        # Test mode controls are now created by the PrankHandler
        self.test_mode_var, self.test_buttons = self.prank_handler.create_test_ui(left_frame)
        
        leaderboard_frame = tk.Frame(right_frame, bg='#2c3e50')
        leaderboard_frame.pack(fill='both', expand=True)
        tk.Label(leaderboard_frame, text="🏆 LEADERBOARD 🏆", 
                font=('Arial', 16, 'bold'), bg='#2c3e50', fg='#f39c12').pack()
        
        lb_frame = tk.Frame(leaderboard_frame, bg='#2c3e50')
        lb_frame.pack(pady=10, fill='both', expand=True)
        scrollbar = tk.Scrollbar(lb_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.leaderboard_listbox = tk.Listbox(lb_frame, yscrollcommand=scrollbar.set,
                                             bg='#34495e', fg='#ecf0f1', font=('Arial', 12))
        self.leaderboard_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.leaderboard_listbox.yview)
        
        refresh_btn = tk.Button(leaderboard_frame, text="Refresh Leaderboard",
                               command=self.load_leaderboard, bg='#27ae60', fg='white', font=('Arial', 10))
        refresh_btn.pack(pady=5)
    
    def get_display_name(self):
        return f"{self.player_name} has no biscuits" if self.has_no_biscuits_taunt else self.player_name
    
    def toggle_test_mode(self):
        """Toggles test mode and updates UI visibility via the PrankHandler."""
        self.test_mode = self.test_mode_var.get()
        self.prank_handler.toggle_test_buttons_visibility(self.test_mode, self.test_buttons)
    
    def update_wheel(self):
        """Update the wheel display based on selected risk set"""
        if not hasattr(self, 'wheel_canvas'): return
        self.wheel_canvas.delete("all")
        
        sections = self.risk_sets[self.selected_risk_set.get()]["sections"]
        total_angle, center_x, center_y, radius = 0, 150, 150, 120
        
        for section in sections:
            section_angle = (section["chance"] / 100.0) * 360
            self.wheel_canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                                         start=total_angle, extent=section_angle, fill=section["color"], outline='white', width=2)
            
            text_angle = math.radians(total_angle + section_angle / 2)
            self.wheel_canvas.create_text(center_x + (radius * 0.85) * math.cos(text_angle),
                                          center_y - (radius * 0.85) * math.sin(text_angle),
                                          text=section["emoji"], font=('Arial', 20), fill='white')
            self.wheel_canvas.create_text(center_x + (radius * 0.7) * math.cos(text_angle),
                                          center_y - (radius * 0.7) * math.sin(text_angle),
                                          text=f"{section['chance']}%", font=('Arial', 12, 'bold'), fill='white')
            total_angle += section_angle
        
        self.wheel_canvas.create_oval(center_x - 15, center_y - 15, center_x + 15, center_y + 15,
                                      fill='#2c3e50', outline='white', width=2)
        pointer_points = [center_x, center_y - radius - 20, center_x - 15, center_y - radius - 5, center_x + 15, center_y - radius - 5]
        self.wheel_canvas.create_polygon(pointer_points, fill='#f39c12', outline='white', width=2)
    
    def spin_wheel(self):
        """Spin the wheel with animation"""
        if self.spinning or self.test_mode:
            if self.test_mode: messagebox.showinfo("Test Mode", "Use the test buttons below!")
            return
        
        self.spinning = True
        self.risk_button.config(state='disabled', text='SPINNING...')
        
        sections = self.risk_sets[self.selected_risk_set.get()]["sections"]
        roll = random.randint(1, 100)
        cumulative_chance = 0
        selected_section = sections[-1]
        
        for section in sections:
            cumulative_chance += section["chance"]
            if roll <= cumulative_chance:
                selected_section = section
                break
        
        section_start_angle = 0
        for section in sections:
            if section == selected_section:
                section_angle = (section["chance"] / 100.0) * 360
                target_angle = section_start_angle + random.uniform(section_angle * 0.1, section_angle * 0.9)
                break
            section_start_angle += (section["chance"] / 100.0) * 360
        
        self.spin_speed = 20
        total_spins = random.randint(3, 6) * 360
        self.target_angle = (360 - target_angle + total_spins) % 360
        self.current_spin_angle = 0
        self.animate_spin(selected_section)
    
    def animate_spin(self, final_section):
        """Animate the wheel spinning"""
        if not self.spinning: return
        self.current_spin_angle += self.spin_speed
        
        if self.current_spin_angle >= self.target_angle - 180: self.spin_speed *= 0.95
        
        if self.current_spin_angle >= self.target_angle and self.spin_speed < 1:
            self.spinning = False
            self.risk_button.config(state='normal', text='SPIN THE WHEEL!')
            self.root.after(500, lambda: self.execute_outcome(final_section))
            return
        
        self.draw_rotated_wheel(self.current_spin_angle)
        self.root.after(50, lambda: self.animate_spin(final_section))
    
    def draw_rotated_wheel(self, rotation_angle):
        self.wheel_canvas.delete("all")
        sections = self.risk_sets[self.selected_risk_set.get()]["sections"]
        total_angle, center_x, center_y, radius = rotation_angle, 150, 150, 120
        
        for section in sections:
            section_angle = (section["chance"] / 100.0) * 360
            self.wheel_canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                                         start=total_angle, extent=section_angle, fill=section["color"], outline='white', width=2)
            text_angle = math.radians(total_angle + section_angle / 2)
            self.wheel_canvas.create_text(center_x + (radius * 0.85) * math.cos(text_angle),
                                          center_y - (radius * 0.85) * math.sin(text_angle),
                                          text=section["emoji"], font=('Arial', 20), fill='white')
            self.wheel_canvas.create_text(center_x + (radius * 0.7) * math.cos(text_angle),
                                          center_y - (radius * 0.7) * math.sin(text_angle),
                                          text=f"{section['chance']}%", font=('Arial', 12, 'bold'), fill='white')
            total_angle += section_angle
        
        self.wheel_canvas.create_oval(center_x - 15, center_y - 15, center_x + 15, center_y + 15,
                                      fill='#2c3e50', outline='white', width=2)
        pointer_points = [center_x, center_y - radius - 20, center_x - 15, center_y - radius - 5, center_x + 15, center_y - radius - 5]
        self.wheel_canvas.create_polygon(pointer_points, fill='#f39c12', outline='white', width=2)
    
    def execute_outcome(self, section):
        section["method"]()
    
    def general_reward(self):
        self.points += 1
        self.update_points_display()
        messagebox.showinfo("Success!", "🍪 You earned a biscuit point! 🍪")
        self.update_leaderboard()
    
    def sabotage_reward(self):
        try:
            response = requests.get(self.jsonbin_url, headers=self.jsonbin_headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                leaderboard = data.get('record', data).get('leaderboard', [])
                other_players = [p for p in leaderboard if p['name'] != self.player_name and p['points'] > 0]
                if other_players:
                    target = random.choice(other_players)
                    target['points'] = max(0, target['points'] - 1)
                    leaderboard.sort(key=lambda x: x['points'], reverse=True)
                    requests.put(self.jsonbin_url, json={'leaderboard': leaderboard[:20]}, headers=self.jsonbin_headers, timeout=10)
                    messagebox.showinfo("Sabotage Success!", f"💀 You reduced {target['name']}'s score by 1 point! 💀")
                    self.load_leaderboard()
                else:
                    messagebox.showinfo("No Target", "🤷 No other players to sabotage! You get nothing.")
            else:
                messagebox.showinfo("Connection Error", "Could not connect to leaderboard for sabotage!")
        except Exception as e:
            print(f"Sabotage failed: {e}")
            messagebox.showinfo("Sabotage Failed", "Could not execute sabotage!")
    
    def sabotage_prank(self):
        self.points -= 5
        self.update_points_display()
        messagebox.showwarning("SABOTAGE BACKFIRED!", "😱 Your sabotage attempt failed! You lost 5 points! 😱")
        self.update_leaderboard()
    
    def update_points_display(self):
        self.points_display.config(text=f"Points: {self.points}")
    
    def load_leaderboard(self):
        try:
            response = requests.get(self.jsonbin_url, headers=self.jsonbin_headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                leaderboard = data.get('record', data).get('leaderboard', [])
                self.display_leaderboard(leaderboard)
            else:
                print(f"Failed to load leaderboard: {response.status_code}")
                self.display_leaderboard([])
        except Exception as e:
            print(f"Failed to load leaderboard: {e}")
            self.display_leaderboard([])
    
    def update_leaderboard(self):
        try:
            response = requests.get(self.jsonbin_url, headers=self.jsonbin_headers, timeout=10)
            leaderboard = response.json().get('record', response.json()).get('leaderboard', []) if response.status_code == 200 else []
            
            player_found = False
            for player in leaderboard:
                if player['name'] == self.player_name:
                    player['points'] = self.points
                    player_found = True
                    break
            if not player_found:
                leaderboard.append({'name': self.player_name, 'points': self.points})
            
            leaderboard.sort(key=lambda x: x['points'], reverse=True)
            leaderboard = leaderboard[:20]
            
            requests.put(self.jsonbin_url, json={'leaderboard': leaderboard}, headers=self.jsonbin_headers, timeout=10)
            self.display_leaderboard(leaderboard)
        except Exception as e:
            print(f"Failed to update leaderboard: {e}")
    
    def display_leaderboard(self, leaderboard):
        self.leaderboard_listbox.delete(0, tk.END)
        for i, player in enumerate(leaderboard, 1):
            display_name = self.get_display_name() if player['name'] == self.player_name else player['name']
            entry = f"{i}. {display_name} - {player['points']} points"
            self.leaderboard_listbox.insert(tk.END, entry)
            if player['name'] == self.player_name:
                self.leaderboard_listbox.selection_set(i-1)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = RiskyBiscyGame()
    game.run()
