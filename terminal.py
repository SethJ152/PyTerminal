import tkinter as tk
from tkinter import scrolledtext
import subprocess
import os
import sys
import platform
import requests
import time

# If needed, run 'pip install requests' to ensure the whois/ip commands work.
# This GUI aims to replicate the Linux Mint dark theme and incorporate most of the custom commands from the script.

class MintTerminalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyTerminal v2")
        # Dark background reminiscent of Linux Mint
        self.bg_color = "#1B1D1E"  # Adjust as desired for a deeper dark theme
        self.fg_color = "#FFFFFF"  # Foreground text color
        self.prompt_color = "#87FF87"  # A green color for the prompt to mimic Mint
        self.root.configure(bg=self.bg_color)
        self.root.geometry("900x600")
        self.GITHUB_URL = "https://raw.githubusercontent.com/SethJ152/PyTerminal/main/terminal.py"
        self.current_version = "2.0.0"

        # System info
        try:
            self.user = os.getlogin()
        except:
            self.user = "user"
        try:
            self.hostname = platform.node()
        except:
            self.hostname = "host"
        self.cwd = os.path.expanduser("~")

        # Create the scrolled text widget
        self.terminal_output = scrolledtext.ScrolledText(
            self.root,
            bg=self.bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            font=("Monospace", 11),
            relief="flat",
            borderwidth=0,
            wrap=tk.WORD
        )
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        self.terminal_output.config(state=tk.NORMAL)
        # Prevent user from editing output directly
        self.terminal_output.bind("<Key>", lambda e: "break")

        # Create the command entry
        self.command_entry = tk.Entry(
            self.root,
            bg=self.bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            font=("Monospace", 11),
            relief="flat",
            borderwidth=0
        )
        self.command_entry.pack(fill=tk.X)
        self.command_entry.bind("<Return>", self.handle_enter)
        self.command_entry.focus()

        # Display initial prompt
        self.show_prompt()

    def show_prompt(self):
        # Create a Linux Mint-like prompt
        prompt_str = f"{self.user}@{self.hostname}:~$ "
        # Insert the prompt in green-like color
        self.terminal_output.insert(tk.END, prompt_str)
        self.terminal_output.see(tk.END)

    def handle_enter(self, event):
        # Grab the entered command
        command = self.command_entry.get().strip()
        # Echo the command to the output
        self.terminal_output.insert(tk.END, command + "\n")
        self.terminal_output.see(tk.END)
        # Clear the entry widget
        self.command_entry.delete(0, tk.END)
        # Process the command
        self.process_command(command)
        # Show new prompt
        self.show_prompt()

    def process_command(self, command):
        if not command:
            return
        # Parse command and args
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        # Check custom commands
        if cmd == "exit":
            self.root.destroy()
        elif cmd == "clear":
            self.terminal_output.delete(1.0, tk.END)
        elif cmd == "cd":
            self.change_directory(args)
        elif cmd == "ping":
            self.cmd_ping(args)
        elif cmd == "whois":
            self.cmd_whois(args)
        elif cmd == "ip":
            self.cmd_ip()
        elif cmd == "calculate":
            self.cmd_calculate(args)
        elif cmd == "shutdown":
            self.cmd_shutdown()
        elif cmd == "reboot":
            self.cmd_reboot()
        elif cmd == "pause":
            self.cmd_pause(args)
        elif cmd == "diskspace":
            self.cmd_diskspace()
        elif cmd == "uptime":
            self.cmd_uptime()
        elif cmd == "processes":
            self.cmd_processes()
        elif cmd == "list":
            self.cmd_list(args)
        elif cmd == "changedir":
            self.change_directory(args)
        elif cmd == "currentdir":
            self.cmd_currentdir()
        elif cmd == "showfile":
            self.cmd_showfile(args)
        elif cmd == "print":
            self.cmd_print(args)
        elif cmd == "run":
            self.cmd_run(args)
        elif cmd == "makedir":
            self.cmd_makedir(args)
        elif cmd == "removefile":
            self.cmd_removefile(args)
        elif cmd == "removedir":
            self.cmd_removedir(args)
        elif cmd == "copy":
            self.cmd_copy(args)
        elif cmd == "move":
            self.cmd_move(args)
        elif cmd == "clearscreen":
            self.terminal_output.delete(1.0, tk.END)
        elif cmd == "systeminfo":
            self.cmd_systeminfo()
        elif cmd == "currentuser":
            self.cmd_currentuser()
        elif cmd == "currenttime":
            self.cmd_currenttime()
        elif cmd == "history":
            self.cmd_history()
        elif cmd == "help":
            self.cmd_help()
        elif cmd == "update":
            """Download the latest terminal.py from GitHub and replace the current script."""
            commit_url = "https://api.github.com/repos/SethJ152/PyTerminal/commits/main"
            commit_response = requests.get(commit_url)
            # Get the latest commit name from GitHub
            if commit_response.status_code == 200:
                commit_data = commit_response.json()
                latest_commit_name = commit_data['commit']['message']
            
            try:
                if not self.current_version == latest_commit_name:
                    pr = "y"
                    if pr.lower() == "y":
                        # Download the terminal.py file from GitHub
                        script_url = self.GITHUB_URL
                        response = requests.get(script_url)
                        if response.status_code == 200:
                            # Write the new code to terminal.py
                            script_path = os.path.abspath(__file__)  # Get the full path of the current script
                            with open(script_path, "w") as f:
                                f.write(response.text)

                            # Restart the terminal program with the updated code
                            python = sys.executable  # Get the Python executable path
                            if platform.system() == "Windows":
                                # Windows-specific restart method using subprocess to avoid terminal closing issues
                                subprocess.Popen([python, script_path])
                            else:
                                # For Unix-like systems (Linux/macOS), using os.execl to restart
                                os.execl(python, python, *sys.argv)
            

            except requests.exceptions.RequestException as e:
                pass
        else:
            # If it's not a recognized custom command, try to run it as a shell command.
            self.run_system_command(command)

    ########################################################################
    # Below are the command implementations replicating the old code.
    ########################################################################
    def change_directory(self, args):
        if not args:
            self.print_output("Error: Please specify a path.")
            return
        path = args[0]
        try:
            os.chdir(path)
            self.cwd = os.getcwd()
        except Exception as e:
            self.print_output(f"Error: {str(e)}")

    def cmd_ping(self, args):
        if not args:
            self.print_output("Error: Please specify a host to ping.")
            return
        host = args[0]
        # On Windows: ping -n 4, on *nix: ping -c 4
        cmd = ["ping", "-n" if os.name == "nt" else "-c", "4", host]
        self.run_system_command(" ".join(cmd))

    def cmd_whois(self, args):
        if not args:
            self.print_output("Error: Please specify a domain.")
            return
        domain = args[0]
        self.run_system_command(f"whois {domain}")

    def cmd_ip(self):
        try:
            response = requests.get("https://ipinfo.io/json").json()
            ip = response.get("ip", "Unknown")
            city = response.get("city", "Unknown")
            region = response.get("region", "Unknown")
            country = response.get("country", "Unknown")
            self.print_output(f"Public IP: {ip}, Location: {city}, {region}, {country}")
        except Exception as e:
            self.print_output(f"Error fetching IP details: {str(e)}")

    def cmd_calculate(self, args):
        if not args:
            self.print_output("Error: No expression provided.")
            return
        expression = " ".join(args)
        try:
            result = eval(expression)
            self.print_output(f"Result: {result}")
        except Exception as e:
            self.print_output(f"Error: {str(e)}")

    def cmd_shutdown(self):
        self.print_output("Shutting down the system...")
        if os.name == "nt":
            subprocess.run("shutdown /s /f", shell=True)
        else:
            subprocess.run("sudo shutdown now", shell=True)

    def cmd_reboot(self):
        self.print_output("Rebooting the system...")
        if os.name == "nt":
            subprocess.run("shutdown /r /f", shell=True)
        else:
            subprocess.run("reboot", shell=True)

    def cmd_pause(self, args):
        if not args:
            self.print_output("Error: Please specify the number of seconds to pause.")
            return
        try:
            t = int(args[0])
            self.print_output(f"Pausing for {t} seconds...")
            time.sleep(t)
        except ValueError:
            self.print_output("Error: Invalid time format.")

    def cmd_diskspace(self):
        if os.name == "nt":
            self.run_system_command("wmic logicaldisk get size,freespace,caption")
        else:
            self.run_system_command("df -h")

    def cmd_uptime(self):
        if os.name == "nt":
            # Windows doesn't have 'uptime' by default, approximate with 'net stats srv'
            self.run_system_command("net stats srv")
        else:
            output = subprocess.getoutput("uptime")
            self.print_output(output)

    def cmd_processes(self):
        if os.name == "nt":
            self.run_system_command("tasklist")
        else:
            self.run_system_command("ps aux")

    def cmd_list(self, args):
        path = args[0] if args else "."
        try:
            items = os.listdir(path)
            for item in items:
                self.print_output(item)
        except Exception as e:
            self.print_output(f"Error: {str(e)}")

    def cmd_currentdir(self):
        self.print_output(os.getcwd())

    def cmd_showfile(self, args):
        if not args:
            self.print_output("Error: Please specify a filename.")
            return
        filename = args[0]
        try:
            with open(filename, "r") as file:
                contents = file.read()
            self.print_output(contents)
        except FileNotFoundError:
            self.print_output(f"Error: No such file: {filename}")
        except Exception as e:
            self.print_output(f"Error: {str(e)}")

    def cmd_print(self, args):
        text = " ".join(args)
        self.print_output(text)

    def cmd_run(self, args):
        if not args:
            self.print_output("Error: Please specify a command to run.")
            return
        cmd = " ".join(args)
        self.run_system_command(cmd)

    def cmd_makedir(self, args):
        if not args:
            self.print_output("Error: Please specify a directory name.")
            return
        path = args[0]
        try:
            os.makedirs(path)
            self.print_output(f"Directory '{path}' created.")
        except Exception as e:
            self.print_output(f"Error: {str(e)}")

    def cmd_removefile(self, args):
        if not args:
            self.print_output("Error: Please specify a filename.")
            return
        filename = args[0]
        try:
            os.remove(filename)
            self.print_output(f"File '{filename}' removed.")
        except Exception as e:
            self.print_output(f"Error: {str(e)}")

    def cmd_removedir(self, args):
        import shutil
        if not args:
            self.print_output("Error: Please specify a directory.")
            return
        path = args[0]
        try:
            shutil.rmtree(path)
            self.print_output(f"Directory '{path}' removed.")
        except Exception as e:
            self.print_output(f"Error: {str(e)}")

    def cmd_copy(self, args):
        import shutil
        if len(args) < 2:
            self.print_output("Error: Please specify [source] [destination].")
            return
        source, destination = args
        try:
            if os.path.isdir(source):
                shutil.copytree(source, destination)
                self.print_output(f"Directory '{source}' copied to '{destination}'.")
            else:
                shutil.copy2(source, destination)
                self.print_output(f"File '{source}' copied to '{destination}'.")
        except Exception as e:
            self.print_output(f"Error: {str(e)}")

    def cmd_move(self, args):
        import shutil
        if len(args) < 2:
            self.print_output("Error: Please specify [source] [destination].")
            return
        source, destination = args
        try:
            shutil.move(source, destination)
            self.print_output(f"'{source}' moved to '{destination}'.")
        except Exception as e:
            self.print_output(f"Error: {str(e)}")

    def cmd_systeminfo(self):
        self.print_output(f"Hostname: {self.hostname}")
        self.print_output(f"User: {self.user}")
        self.print_output(f"OS: {platform.system()}")

    def cmd_currentuser(self):
        self.print_output(self.user)

    def cmd_currenttime(self):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        self.print_output(now)

    def cmd_history(self):
        # For this GUI version, we don't keep a persistent history; we can mimic by searching through the text.
        self.print_output("Command history not implemented for GUI.")

    def cmd_help(self):
        msg = [
            "Available commands:",
            "  exit            - Close the terminal.",
            "  clear           - Clear the screen.",
            "  cd [path]       - Change directory.",
            "  ping [host]     - Ping a host.",
            "  whois [domain]  - WHOIS lookup.",
            "  ip              - Fetch public IP info.",
            "  calculate <expr>- Evaluate a math expression.",
            "  shutdown        - Shutdown the system.",
            "  reboot          - Reboot the system.",
            "  pause <sec>     - Pause for <sec> seconds.",
            "  diskspace       - Show free disk space.",
            "  uptime          - Show system uptime.",
            "  processes       - List running processes.",
            "  list [path]     - List directory contents.",
            "  changedir [p]   - Change directory.",
            "  currentdir      - Show current directory.",
            "  showfile [file] - Display file contents.",
            "  print [text]    - Echo text.",
            "  run [cmd]       - Run a system command.",
            "  makedir [dir]   - Create a directory.",
            "  removefile [f]  - Remove a file.",
            "  removedir [dir] - Remove a directory.",
            "  copy src dst    - Copy file/dir.",
            "  move src dst    - Move file/dir.",
            "  clearscreen     - Clear the screen.",
            "  systeminfo      - Show system information.",
            "  currentuser     - Display current user.",
            "  currenttime     - Show date/time.",
            "  history         - Show command history (not persistent).",
            "  help            - Show this help.",
        ]
        self.print_output("\n".join(msg))

    ########################################################################
    # Utility methods
    ########################################################################
    def print_output(self, text):
        self.terminal_output.insert(tk.END, text + "\n")
        self.terminal_output.see(tk.END)

    def run_system_command(self, command):
        try:
            # Use the shell under Linux or Windows
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True,
                                             universal_newlines=True, cwd=self.cwd)
            self.print_output(output)
        except subprocess.CalledProcessError as e:
            self.print_output(e.output)
        except Exception as e:
            self.print_output(str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = MintTerminalGUI(root)
    root.mainloop()
