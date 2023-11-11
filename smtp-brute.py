import asyncio
import sys
import os

# Text colors for the console (may vary depending on the system)
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Global list to store all successful responses
successful_responses = []

async def telnet_connect(ip, port, usernames, start_index=0):
  global successful_responses

  try:
    # Create a Telnet connection
    reader, writer = await asyncio.open_connection(ip, port)

    # Display successful connection message
    print(f"Successful connection to {ip}:{port}")

    # Wait for the initial server response
    print(BLUE + "Waiting for banner" + RESET)
    response = await reader.readuntil(b'\n')
    print(BLUE + response.decode('utf-8').strip() + RESET)

    # Check if the response is a code 220 or 252
    if response.startswith(b'220') or response.startswith(b'252'):
      total_entries = len(usernames)
      # Display the total number of entries in the dictionary
      print(f"Number of entries: {total_entries}")

      # Loop to check each username
      for i, username in enumerate(usernames[start_index:], start=start_index):
        print(f"Verifying {i + 1}/{total_entries} - {username}")

        # Send the VRFY command for the current username
        writer.write(f"VRFY {username}\n".encode('utf-8'))

        # Read the server response
        response = await reader.readuntil(b'\n')
        response_str = response.decode('utf-8').strip()

        # Check the response code
        if response_str.startswith("421"):
          save_last_index(i)
          print(YELLOW + "Closing the connection. Reconnecting, please wait..." + RESET)
          writer.close()
          await asyncio.sleep(5)
          return await telnet_connect(ip, port, usernames, start_index=i)
        elif response_str.startswith(("220", "252")):
          print(GREEN + response_str + RESET)
          successful_responses.append(response_str)
        elif not response_str.startswith("550"):
          print(response_str)

      # Close the connection
      writer.close()

  except Exception as e:
    print(f"Error attempting to connect to {ip}:{port}")
    print(f"Error: {e}")

def save_last_index(index):
  with open("last_index.txt", "w") as file:
    file.write(str(index + 1))  # Increment by 1 to continue with the next username

def read_last_index():
  try:
    with open("last_index.txt", "r") as file:
      return int(file.read().strip())
  except FileNotFoundError:
    return 0

def read_usernames_from_file(filename):
  try:
    with open(filename, 'r') as file:
      return [line.strip() for line in file.readlines()]
  except FileNotFoundError:
    print(f"Error: File {filename} not found.")
    sys.exit(1)

def show_successful_responses():
  global successful_responses
  if successful_responses:
    print(GREEN + "Mailboxes found:" + RESET)
    for response in successful_responses:
      print(GREEN + f"  {response}" + RESET)

def print_banner():
    # Display ASCII banner
    ascii_banner = """
 :'######::'##::::'##:'########:'########:::::::::::'########::'########::'##::::'##:'########:'########:
'##... ##: ###::'###:... ##..:: ##.... ##:::::::::: ##.... ##: ##.... ##: ##:::: ##:... ##..:: ##.....::
 ##:::..:: ####'####:::: ##:::: ##:::: ##:::::::::: ##:::: ##: ##:::: ##: ##:::: ##:::: ##:::: ##:::::::
. ######:: ## ### ##:::: ##:::: ########::'#######: ########:: ########:: ##:::: ##:::: ##:::: ######:::
:..... ##: ##. #: ##:::: ##:::: ##.....:::........: ##.... ##: ##.. ##::: ##:::: ##:::: ##:::: ##...::::
'##::: ##: ##:.:: ##:::: ##:::: ##::::::::::::::::: ##:::: ##: ##::. ##:: ##:::: ##:::: ##:::: ##:::::::
. ######:: ##:::: ##:::: ##:::: ##::::::::::::::::: ########:: ##:::. ##:. #######::::: ##:::: ########:
:......:::..:::::..:::::..:::::..::::::::::::::::::........:::..:::::..:::.......::::::..:::::........::
                                Coded by Fernando García (Incuerd0)
    
    Description: This script performs a brute-force attack on an SMTP server by verifying
    the existence of user mailboxes using the VRFY command.

    GitHub Repository: https://github.com/fernandoG494/SMTP-Brute

Usage: python script.py [IP] [PORT] [DICTIONARY.TXT]
Example: python script.py 10.0.0.1 25 usernames.txt
"""
    print(ascii_banner)

if __name__ == "__main__":
    # Display the banner
    print_banner()

    if len(sys.argv) != 4:
        print("Usage: python script.py [IP] [PORT] [DICTIONARY.TXT]")
        sys.exit(1)

    ip, port, filename = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    usernames, last_index = read_usernames_from_file(filename), read_last_index()

    asyncio.run(telnet_connect(ip, port, usernames, start_index=last_index))
    show_successful_responses()

    try:
        os.remove("last_index.txt")
    except FileNotFoundError:
        pass

