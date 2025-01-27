import time
import requests
from datetime import datetime, timedelta
import os
from aho_corasick import AhoCorasick

# Put Discord webhook URL to post in channel here
DISCORD_WEBHOOK_URL = '' 

# Path to the latest log files
MINECRAFT_LOGS = ''

"""
Setup the keyword tree. Each log line will be checked against these to see if the line matches any of these. If a match is found and the mapped
value is an empty string, the matched line will be printed out as is. If the mapped value is not an empty string, we will instead print the
provided message
"""
KEYWORDS = AhoCorasick()
KEYWORDS.add_word("joined the game", "")
KEYWORDS.add_word("left the game", "")
KEYWORDS.add_word("server empty for 60 seconds", "")
KEYWORDS.add_word("starting backup", "Starting Backup")
KEYWORDS.add_word("backup complete", "Backup Complete") 

# DEATHS
KEYWORDS.add_word("fell from a high place", "")
KEYWORDS.add_word("fell out of the world", "")
KEYWORDS.add_word("hit the ground too hard", "")
KEYWORDS.add_word("was squished too much", "")
KEYWORDS.add_word("went up in flames", "")
KEYWORDS.add_word("burned to death", "")
KEYWORDS.add_word("tried to swim in lava", "")
KEYWORDS.add_word("drowned", "")
KEYWORDS.add_word("starved to death", "")

# COMBAT DEATHS
KEYWORDS.add_word("was slain by", "")
KEYWORDS.add_word("was frozen to death by", "")
KEYWORDS.add_word("was shot by", "")
KEYWORDS.add_word("blew up", "")
KEYWORDS.add_word("was blown up by", "")
KEYWORDS.add_word("was killed by", "")
KEYWORDS.add_word("was killed trying to hurt", "")

# Environmental Deaths
KEYWORDS.add_word("fell into a patch of", "")
KEYWORDS.add_word("fell into the void", "")
KEYWORDS.add_word("was impaled on a stalagmite", "")
KEYWORDS.add_word("walked into fire whilst fighting", "")
KEYWORDS.add_word("went up in flames", "")
KEYWORDS.add_word("tried to swim in lava to escape", "")
KEYWORDS.add_word("drowned whilst trying to escape", "")
KEYWORDS.add_word("froze to death", "")
KEYWORDS.add_word("suffocated in a wall", "")
KEYWORDS.add_word("was pricked to death", "")
KEYWORDS.add_word("froze to death", "")
KEYWORDS.add_word("was struck by lightning", "")
KEYWORDS.add_word("discovered the floor was lava", "")
KEYWORDS.add_word("was obliterated by a sonically charged shriek", "")
KEYWORDS.add_word("was stung to death by bees", "")
KEYWORDS.add_word("was rammed by a goat", "")
#KEYWORDS.add_word(" died", "")


KEYWORDS.build()

def send_discord_message(content):
  data = {
    "content": content
  }
  try:
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    response.raise_for_status()
  except requests.RequestException as e:
    print(f"Failed to send Discord message: {str(e)}")

class LogTailer:
  def __init__(self, log_file):
    self.log_file = log_file
    self.file_handle = None
    self.current_inode = None

  def _open_file(self):
    """Open the log file and initialize tracking."""
    if not os.path.exists(self.log_file):
      print(f"Log file {self.log_file} does not exist. Waiting for it to be created...")
      self.file_handle = None
      return

    self.file_handle = open(self.log_file, "r")
    self.current_inode = os.fstat(self.file_handle.fileno()).st_ino
    print(f"Started tailing {self.log_file}")
    self.file_handle.seek(0, os.SEEK_END)

  def _close_file(self):
    """Close the log file."""
    if self.file_handle:
      self.file_handle.close()
      self.file_handle = None

  def _check_reopen(self):
    """
    Check if the file has been recreated (e.g., log rotation).
    If yes, reopen the file.
    """
    if self.file_handle is None:
      self._open_file()
      return

    try:
      # Compare inodes to detect file recreation
      current_inode = os.stat(self.log_file).st_ino
      if self.current_inode != current_inode:
        print(f"Log file {self.log_file} was recreated. Reopening...")
        self._close_file()
        self._open_file()
    except FileNotFoundError:
      print(f"Log file {self.log_file} was deleted. Waiting for it to be recreated...")
      self._close_file()

  def _on_line(self, line):
    matches = KEYWORDS.search(line.lower())
    if len(matches) == 0:
      return
    match = matches[0]
    if len(match) == 0:
      send_discord_message(line)
    else:
      send_discord_message(match)

  def tail(self):
    """Continuously tail the log file."""
    self._open_file()
    try:
      while True:
        self._check_reopen()
        if self.file_handle:
          line = self.file_handle.readline()
          if line:
            self._on_line(line.strip())
          else:
            time.sleep(15)
        else:
          time.sleep(1)
    except KeyboardInterrupt:
      print("\nStopping log tailer...")
    finally:
      self._close_file()


if __name__ == '__main__': 
  try:
    tailer = LogTailer(MINECRAFT_LOGS)
    tailer.tail()
  except Exception as error:
    error_message = f'❗️ An error occurred ERROR: \n{str(error)}'
    print(error_message)
