# stand_app/match_commands.py
"""
Standalone command matcher for transcribed CSV output.

Usage:
  python match_commands.py --in transcriptions.csv

Prints matched commands and executes stub handlers from commands.py.

CSV Format:
  start_time, end_time, text
Example:
  0.80, 1.80, Stop music
  2.90, 3.60, start music.
  4.30, 6.40, Play La Bamba by Ritchie Valens.

Dependencies:
  - standard library
  - stand_app.commands
"""

import argparse
import csv
import re
from pathlib import Path

from commands import *
import commands

# Command match patterns → canonical function names
COMMAND_PATTERNS = [
    (re.compile(r"\bstop music\b", re.IGNORECASE), "stop_music"),
    (re.compile(r"\bstart music\b", re.IGNORECASE), "start_music"),
    (re.compile(r"\bnext song\b", re.IGNORECASE), "next_track"),
    (re.compile(r"\bgo back\b", re.IGNORECASE), "previous_track"),
    (re.compile(r"\bvolume up\b", re.IGNORECASE), "volume_up"),
    (re.compile(r"\bvolume down\b", re.IGNORECASE), "volume_down"),

    (re.compile(r"\bplay (.+?) by (.+)", re.IGNORECASE), "play_song"),   # not yet supported
]

# Map string names to actual functions
COMMAND_FUNCTIONS = {
    "stop_music": commands.stop_music,
    "start_music": commands.start_music,
    "play_song": commands.play_song,
}


def match_command(text: str):
    for pattern, command in COMMAND_PATTERNS:
        match = pattern.search(text)
        if match:
            func = COMMAND_FUNCTIONS.get(command)
            if not func:
                return None
            if command == "play_song":
                groups = match.groups()
                title = groups[0].strip()
                artist = groups[1].strip() if len(groups) > 1 else None
                func(title, artist)
            else:
                func()
            return command
    return None


def main():
    parser = argparse.ArgumentParser(description="Match commands from transcript")
    parser.add_argument("--in", dest="infile", type=Path, required=True, help="Path to transcription .csv")
    args = parser.parse_args()

    activation_active = False

    with open(args.infile, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 3:
                continue  # Skip malformed rows
            start, end, text = row
            text = text.strip()

            if re.search(r"\bhey rex\b", text, re.IGNORECASE):
                activation_active = True
                print(f"[{start}-{end}s] → (activation detected): '{text}'")
                continue

            if activation_active:
                # Strip activation if lingering
                text = re.sub(r"\bhey rex\b[,:]?\s*", "", text, flags=re.IGNORECASE)
                command = match_command(text.strip())
                if command:
                    print(f"[{start}-{end}s] → matched: {command}")
                else:
                    print(f"[{start}-{end}s] → (no match)  '{text.strip()}'")
                activation_active = False  # Reset trigger
            else:
                print(f"[{start}-{end}s] → (ignored, no activation): '{text}'")


if __name__ == "__main__":
    main()