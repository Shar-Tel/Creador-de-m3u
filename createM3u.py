"""
Script to organize multi-disc games into folders and create .m3u playlist files.

This script searches for files with pattern (disc N), groups them by base name,
creates folders for each game and generates an ordered .m3u file.
"""

import os
import re
import sys
import time
from collections import defaultdict

# Get working directory (as parameter or by input)
if len(sys.argv) > 1:
    directory = sys.argv[1]
else:
    directory = input("Enter the directory to work on: ")

# Validate that the directory exists
if not os.path.isdir(directory):
    print("The directory does not exist.")
    sys.exit()

# Dictionary to group multi-disc files by game base name
# Structure: {game_name: [file1, file2, ...]}
multi_disc_games = defaultdict(list)

# Phase 1: Scan files and group by multi-disc game
print("Phase 1: Scanning files...")
for file in os.listdir(directory):
    full_path = os.path.join(directory, file)
    
    # Process only files (not directories)
    if os.path.isfile(full_path):
        # Search for pattern "(disc N)" in filename
        match = re.search(r'(.*?)\s*\(disc\s*(\d+)\)', file, re.IGNORECASE)
        
        if match:
            # Extract base game name (everything before "disc N")
            base_name = match.group(1).strip()
            # Store file in list of corresponding game
            multi_disc_games[base_name].append(file)
            print(f"  Found: {file} -> {base_name}")

print(f"Found {len(multi_disc_games)} multi-disc games.\n")
time.sleep(1)  # Brief pause to improve output readability

# Phase 2: Process multi-disc games (with 2 or more discs)
print("Phase 2: Processing multi-disc games...")
for base_name, files in multi_disc_games.items():
    if len(files) > 1:  # Only process if there are multiple discs
        print(f"\n  Processing: {base_name} ({len(files)} discs)")

        m3u_path = os.path.join(directory, f"{base_name}.m3u")
        
        # Check if .m3u file already exists and ask user if they want to process the game
        if os.path.exists(m3u_path):
            response = input(f"    The file '{base_name}.m3u' already exists. Do you want to process this game? (y/n): ").lower()
            if response.lower() != 'y':
                print(f"    Game not processed: {base_name}")
                continue
        
        # Create folder for the game
        game_directory = os.path.join(directory, base_name)
        if not os.path.exists(game_directory):
            os.makedirs(game_directory)
            print(f"    Folder created: {base_name}")
        else:
            print(f"    Folder already exists: {base_name}")
        
        # Helper function to extract disc number from filename
        def get_disc_number(x):
            """Extracts the disc number from the filename for sorting."""
            match = re.search(r'\(disc\s*(\d+)\)', x, re.IGNORECASE)
            return int(match.group(1)) if match else 0
        
        # Sort files by disc number and move them to the game folder
        ordered_files = []
        for file in sorted(files, key=get_disc_number):
            source_path = os.path.join(directory, file)
            destination_path = os.path.join(game_directory, file)
            
            # Move file if it doesn't already exist in destination
            if not os.path.exists(destination_path):
                os.rename(source_path, destination_path)
                print(f"    Moved: {file}")
            else:
                print(f"    Already exists: {file}")
            
            ordered_files.append(file)
        
        # Create .m3u file with the list of ordered discs
        with open(m3u_path, 'w', encoding='utf-8') as m3u:
            for file in ordered_files:
                m3u.write(os.path.join(base_name, f"{file}\n"))
        print(f"    .m3u file created: {base_name}.m3u")
        time.sleep(1)
        
        # Inform user that processing is completed
