# Risky Biscy - Setup Guide

## 🍪 Game Overview
**Risky Biscy** is a desktop game where players risk it for a biscuit! Click the button to either gain points, get pranked, or have nothing happen. Compete on the global leaderboard!

## 📋 Prerequisites
- Python 3.7 or higher
- Internet connection (for leaderboard)
- Windows (Mac support included but Windows is primary target)

## 🛠️ Setup Instructions

### Step 1: JSONBin.io Setup (IMPORTANT!)
1. Go to [JSONBin.io](https://jsonbin.io/) and create a free account
2. Create a new bin with this initial content:
   ```json
   {
     "leaderboard": []
   }
   ```
3. Note down your:
   - **Bin ID** (from the URL, e.g., `642a1b2c8e4aa6225e123456`)
   - **Master Key** (from your account settings)

### Step 2: Configure the Game
1. Open `risky_biscy.py` in a text editor
2. Find these lines around line 25-30:
   ```python
   self.jsonbin_url = "https://api.jsonbin.io/v3/b/YOUR_BIN_ID"  # Replace with your bin ID
   self.jsonbin_headers = {
       "Content-Type": "application/json",
       "X-Master-Key": "YOUR_API_KEY"  # Replace with your API key
   }
   ```
3. Replace:
   - `YOUR_BIN_ID` with your actual bin ID
   - `YOUR_API_KEY` with your master key from JSONBin.io

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Test the Game
```bash
python risky_biscy.py
```

### Step 5: Build Executable

#### For Windows:
```bash
# Run the build script
build.bat
```

#### For Mac/Linux:
```bash
# Make script executable and run
chmod +x build.sh
./build.sh
```

The executable will be created in the `dist/` folder.

## 🎮 How to Play

1. **Enter Your Name**: Type your name and click "Set Name"
2. **Risk It**: Click the "RISK IT!" button to take your chance
3. **Outcomes**:
   - **25% chance**: Get pranked! (lose points, rickroll, desktop files, or name change)
   - **60% chance**: Earn 1 biscuit point! 🍪
   - **15% chance**: Nothing happens

## 🧪 Test Mode
Enable "Test Mode" to manually trigger each prank for debugging:
- **Desktop Files**: Creates harmless text files on your desktop
- **Rickroll**: Opens Rick Astley in your browser
- **Lose Points**: Removes 2 points from your score
- **Name Change**: Adds "has no biscuits" to your name

## 🏆 Leaderboard
- Global leaderboard shows top 20 players
- Updates automatically when you gain/lose points
- Your current position is highlighted

## 🔧 Troubleshooting

### Leaderboard Not Working
- Double-check your JSONBin.io configuration
- Make sure you have internet connection
- Verify your API key has proper permissions

### Executable Won't Run
- Make sure all dependencies are installed
- Try running `python risky_biscy.py` first to test
- Check Windows Defender/antivirus isn't blocking it

### Pranks Not Working
- Desktop files prank requires write permissions to Desktop folder
- Rickroll requires a default web browser
- Some pranks may fail gracefully on different systems

## 📁 File Structure
```
risky-biscy/
├── risky_biscy.py          # Main game file
├── requirements.txt        # Python dependencies
├── build.bat              # Windows build script
├── build.sh               # Mac/Linux build script
├── SETUP_GUIDE.md         # This file
└── dist/                  # Built executable (after building)
    └── RiskyBiscy.exe
```

## 🎯 Game Jam Submission
The built executable (`RiskyBiscy.exe`) is ready for game jam submission! It's a self-contained file that doesn't require Python installation on the target machine.

## 🐛 Known Issues
- Desktop files prank may not work on some Linux distributions
- Rickroll requires internet connection
- Leaderboard requires stable internet connection

## 🚀 Future Enhancements
- Local leaderboard backup
- More prank types
- Sound effects
- Custom themes
- Multiplayer modes

Enjoy the game and remember: always risk it for the biscuit! 🍪
