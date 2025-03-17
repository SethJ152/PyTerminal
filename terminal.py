import os
import subprocess
required_dependencies = ['cmd', 'time', 'platform', 'sys', 'shutil', 'requests', 'readline', 'colorama']
def install_dependencies():
    # Check and install missing dependencies
    for dep in required_dependencies:
        try:
            # Try importing the module to see if it's installed
            __import__(dep)
        except ImportError:
            # If not installed, install the package using pip
            print(f"{dep} not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

# Install dependencies before running the main script
install_dependencies()
import cmd
import time
import platform
import sys
import shutil
import requests
import readline
from colorama import init, Fore, Style

# Initialize colorama for colored text output (ensure Windows compatibility)
init(autoreset=True)

class Terminal(cmd.Cmd):
    intro = Fore.GREEN + "Welcome to PyTerminal for " + platform.system() + "\nType 'help' to see available commands." + Style.RESET_ALL
    prompt = Fore.YELLOW + os.getlogin().lower() + "@" + platform.node().lower() + "~> " + Style.RESET_ALL
    history_file = os.path.join(os.path.expanduser("~"), ".py_terminal_history")
    GITHUB_URL = "https://raw.githubusercontent.com/SethJ152/PyTerminal/main/terminal.py"  # GitHub URL of the terminal.py file
    current_version = "1.5.5"
    def do_version(self, _):
        
        """Download the latest terminal.py from GitHub and replace the current script."""
        try:
            # Get the latest commit name from GitHub
            commit_url = "https://api.github.com/repos/SethJ152/PyTerminal/commits/main"
            commit_response = requests.get(commit_url)
            
            if commit_response.status_code == 200:
                commit_data = commit_response.json()
                latest_commit_name = commit_data['commit']['message']
                print(Fore.CYAN + f"Latest Version: {latest_commit_name}" + Style.RESET_ALL)
                print(Fore.CYAN + f"Current Version: {self.current_version}" + Style.RESET_ALL)
            else:
                print(Fore.RED + "Error: Unable to fetch the latest commit from GitHub." + Style.RESET_ALL)

        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"Error fetching data: {str(e)}" + Style.RESET_ALL)
    def do_ping(self, host):
        """Ping a host: ping [hostname or IP]"""
        if not host:
            print(Fore.RED + "Error: Please specify a host to ping." + Style.RESET_ALL)
            return
        command = ["ping", "-c", "4", host] if os.name != "nt" else ["ping", "-n", "4", host]
        self._execute_command(" ".join(command))
    def do_whois(self, domain):
        """Perform WHOIS lookup: whois [domain]"""
        if not domain:
            print(Fore.RED + "Error: Please specify a domain." + Style.RESET_ALL)
            return
        self._execute_command(f"whois {domain}")

    def do_ip(self, _):
        """Fetch public IP and location: iplookup"""
        try:
            response = requests.get("https://ipinfo.io/json").json()
            ip = response.get("ip", "Unknown")
            city = response.get("city", "Unknown")
            region = response.get("region", "Unknown")
            country = response.get("country", "Unknown")
            print(Fore.YELLOW + f"Public IP: {ip}, Location: {city}, {region}, {country}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error fetching IP details: {str(e)}" + Style.RESET_ALL)

    def do_calculate(self, expression):
        """Perform a simple calculation: calculate [expression]"""
        try:
            result = eval(expression)
            print(Fore.GREEN + f"Result: {result}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error: {str(e)}" + Style.RESET_ALL)

    def preloop(self):
        """Load command history if available."""
        if os.path.exists(self.history_file):
            readline.read_history_file(self.history_file)

    def postloop(self):
        """Save command history."""
        readline.write_history_file(self.history_file)

    def do_exit(self, _):
        """Exit the terminal."""
        print(Fore.RED + "Goodbye!" + Style.RESET_ALL)
        return True

    def do_hostname(self, _):
        """Display the system hostname."""
        print(Fore.GREEN + platform.node() + Style.RESET_ALL)

    def do_shutdown(self, _):
        """Shutdown the system."""
        print(Fore.RED + "Shutting down the system..." + Style.RESET_ALL)
        if os.name == "nt":
            subprocess.run("shutdown /s /f", shell=True)
        else:
            subprocess.run("sudo shutdown now", shell=True)

    def do_reboot(self, _):
        """Reboot the system."""
        print(Fore.YELLOW + "Rebooting the system..." + Style.RESET_ALL)
        if os.name != "nt":
            subprocess.run("reboot", shell=True)
        else:
            subprocess.run("shutdown /r /f", shell=True)
                
    def do_pause(self, time_to_sleep):
        """Pause execution for a given number of seconds."""
        try:
            time_to_sleep = int(time_to_sleep)
            print(Fore.MAGENTA + f"Pausing for {time_to_sleep} seconds..." + Style.RESET_ALL)
            time.sleep(time_to_sleep)
        except ValueError:
            print(Fore.RED + "Error: Invalid time format. Please provide an integer value." + Style.RESET_ALL)

    def do_diskspace(self, _):
        """Display free disk space."""
        if os.name == "nt":
            subprocess.run("wmic logicaldisk get size,freespace,caption", shell=True)
        else:
            subprocess.run("df -h", shell=True)

    def do_uptime(self, _):
        """Display the system uptime."""
        print(Fore.GREEN + subprocess.check_output("uptime", shell=True).decode() + Style.RESET_ALL)

    def do_processes(self, _):
        """Show the current running processes."""
        if os.name == "nt":
            subprocess.run("tasklist", shell=True)
        else:
            subprocess.run("ps aux", shell=True)

    def do_clearhistory(self, _):
        """Clear the terminal command history."""
        try:
            readline.clear_history()
            print(Fore.GREEN + "Command history cleared." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error clearing history: {str(e)}" + Style.RESET_ALL)

    def do_update(self, _):
        """Download the latest terminal.py from GitHub and replace the current script."""
        print(Fore.YELLOW + "Gathering Data..." + Style.RESET_ALL)
        try:
            
            if not self.current_version == latest_commit_name:
                # Get the latest commit name from GitHub
                commit_url = "https://api.github.com/repos/SethJ152/PyTerminal/commits/main"
                commit_response = requests.get(commit_url)
            
                if commit_response.status_code == 200:
                    commit_data = commit_response.json()
                    latest_commit_name = commit_data['commit']['message']
                    print(Fore.CYAN + f"Fetching Version: {latest_commit_name}" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "Error: Unable to fetch the latest commit from GitHub." + Style.RESET_ALL)
                print(f"Upgrading from {self.current_version} to {latest_commit_name}...")
                pr = str(input("Are you sure? (y/n): "))
                if pr.lower() == "y":
                    # Download the terminal.py file from GitHub
                    script_url = self.GITHUB_URL
                    response = requests.get(script_url)
                    if response.status_code == 200:
                        # Write the new code to terminal.py
                        script_path = os.path.abspath(__file__)  # Get the full path of the current script
                        with open(script_path, "w") as f:
                            f.write(response.text)
                        print(Fore.GREEN + "Terminal updated successfully!" + Style.RESET_ALL)

                        # Restart the terminal program with the updated code
                        python = sys.executable  # Get the Python executable path
                        if platform.system() == "Windows":
                            # Windows-specific restart method using subprocess to avoid terminal closing issues
                            subprocess.Popen([python, script_path])
                        else:
                            # For Unix-like systems (Linux/macOS), using os.execl to restart
                            os.execl(python, python, *sys.argv)

                    else:
                        print(Fore.RED + "Error: Unable to fetch the terminal code from GitHub." + Style.RESET_ALL)
                else:
                    print("Cancelled.")
            else:
                print(Fore.GREEN + "Already up to date." + Style.RESET_ALL)

        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"Error during update: {str(e)}" + Style.RESET_ALL)


    # Other previously implemented commands...

    def do_list(self, path="."):
        """List directory contents: list [path]"""
        self._handle_action(os.listdir, path, success_msg=f"Listed contents of {path}")

    def do_changedir(self, path=None):
        """Change current directory: changedir [path]"""
        path = path or os.getcwd()
        self._handle_action(os.chdir, path, success_msg=f"Changed to {path}")

    def do_currentdir(self, _):
        """Display current directory."""
        print(Fore.CYAN + os.getcwd() + Style.RESET_ALL)

    def do_showfile(self, filename):
        """Display file contents: showfile [filename]"""
        self._handle_action(self._print_file, filename)

    def do_print(self, text):
        """Print text: print [text]"""
        print(Fore.MAGENTA + text + Style.RESET_ALL)

    def do_run(self, command):
        """Run a system command: run [command]"""
        self._execute_command(command)

    def do_makedir(self, path):
        """Create a directory: makedir [directory]"""
        self._handle_action(os.makedirs, path, success_msg=f"Directory '{path}' created.")

    def do_removefile(self, filename):
        """Delete a file: removefile [filename]"""
        self._handle_action(os.remove, filename, success_msg=f"File '{filename}' removed.")

    def do_removedir(self, path):
        """Delete a directory: removedir [directory]"""
        self._handle_action(shutil.rmtree, path, success_msg=f"Directory '{path}' removed.")

    def do_copy(self, args):
        """Copy files or directories: copy [source] [destination]"""
        self._handle_file_operation(shutil.copy2, shutil.copytree, args)

    def do_move(self, args):
        """Move files or directories: move [source] [destination]"""
        self._handle_file_operation(shutil.move, shutil.move, args)

    def do_clearscreen(self, _):
        """Clear the terminal screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def do_systeminfo(self, _):
        """Show system information."""
        print("Hostname: " + platform.node())
        print("User:     " + os.getlogin())
        print("OS:       " + platform.system())

    def do_currentuser(self, _):
        """Display the current user."""
        print(Fore.GREEN + os.getlogin() + Style.RESET_ALL)

    def do_currenttime(self, _):
        """Show the current date and time."""
        print(Fore.YELLOW + time.strftime("%Y-%m-%d %H:%M:%S") + Style.RESET_ALL)

    def do_commandhistory(self, _):
        """Show command history."""
        history_length = readline.get_current_history_length()
        if history_length == 0:
            print(Fore.RED + "No command history available." + Style.RESET_ALL)
        else:
            for i in range(1, history_length + 1):
                print(Fore.WHITE + f"{i}: {readline.get_history_item(i)}" + Style.RESET_ALL)

    def do_help(self, command=None):
        """List available commands or show help for a specific command."""
        if command:
            cmd.Cmd.do_help(self, command)
        else:
            self.print_help()
    def do_server(self, _):
        """Run server-related commands if the user is seth and hostname is alpha on Linux Mint."""
        if os.getlogin().lower() == "seth" and platform.node().lower() == "alpha" and platform.system().lower() == "linux":
            try:
                print(Fore.GREEN + "Running cloudflared tunnel and starting Server.py..." + Style.RESET_ALL)
                
                # Start cloudflared tunnel in the background
                cloudflared_process = subprocess.Popen(["cloudflared", "tunnel", "run", "sdjdrive"])
                
                # Start Server.py in the background
                server_process = subprocess.Popen(["python3", "/home/seth/Desktop/Server.py"])
                
                # Optionally, wait for the processes to end (if you want to handle it further)
                cloudflared_process.wait()
                server_process.wait()
                
            except Exception as e:
                print(Fore.RED + f"Error: {str(e)}" + Style.RESET_ALL)
        else:
            print(Fore.RED + "Error: This command can only be run by 'seth' on the 'alpha' machine in Linux Mint." + Style.RESET_ALL)

    def print_help(self):
        """Display available commands and descriptions."""
        commands = [
            ("update", "Updates the terminal code"),
            ("version", "Shows the current and latest version"),
            ("exit", "Exit the terminal"),
            ("hostname", "Display the system hostname"),
            ("shutdown", "Shutdown the system"),
            ("reboot", "Reboot the system"),
            ("pause [time]", "Pause execution for the specified time"),
            ("diskspace", "Show free disk space"),
            ("uptime", "Display system uptime"),
            ("processes", "Show the current running processes"),
            ("clearhistory", "Clear the terminal command history"),
            ("list [path]", "List directory contents"),
            ("changedir [path]", "Change directory"),
            ("currentdir", "Print current working directory"),
            ("showfile [file]", "Print file contents"),
            ("print [text]", "Echo the input arguments"),
            ("run [command]", "Execute a system command"),
            ("makedir [directory]", "Create a new directory"),
            ("removefile [file]", "Remove a file"),
            ("removedir [directory]", "Remove a directory"),
            ("copy [source] [destination]", "Copy a file or directory"),
            ("move [source] [destination]", "Move or rename a file or directory"),
            ("clearscreen", "Clear the terminal screen"),
            ("systeminfo", "Display system information"),
            ("currentuser", "Display current user"),
            ("currenttime", "Display the current date and time"),
            ("commandhistory", "Display command history"),
            ("ip", "Shows the ip and location of the user"),
            ("ping", "Pings a server"),
            ("whosi", "Domain lookup"),
            ("help", "List available commands"),
        ]
        print(Fore.CYAN + "Available commands:" + Style.RESET_ALL)
        for cmd, desc in commands:
            print(Fore.YELLOW + f"  {cmd:<20} {desc}" + Style.RESET_ALL)

    # Helper Methods
    def _handle_action(self, func, target, success_msg=None):
        """Handle actions with error handling for both files and directories."""
        try:
            func(target)
            if success_msg:
                print(Fore.GREEN + success_msg + Style.RESET_ALL)
        except FileNotFoundError:
            print(Fore.RED + f"Error: No such file or directory: '{target}'" + Style.RESET_ALL)
        except PermissionError:
            print(Fore.RED + f"Error: Permission denied: '{target}'" + Style.RESET_ALL)
        except OSError as e:
            print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)

    def _print_file(self, filename):
        """Print file contents."""
        try:
            with open(filename, "r") as file:
                print(Fore.WHITE + file.read() + Style.RESET_ALL)
        except FileNotFoundError:
            print(Fore.RED + f"Error: No such file: '{filename}'" + Style.RESET_ALL)

    def _execute_command(self, command):
        """Execute a system command."""
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError:
            print(Fore.RED + f"Error: Command '{command}' failed" + Style.RESET_ALL)

    def _handle_file_operation(self, copy_func, move_func, args):
        """Helper method to handle copy and move operations."""
        try:
            source, destination = args.split()
            if os.path.isdir(source):
                move_func(source, destination)
                print(Fore.GREEN + f"Directory moved from {source} to {destination}" + Style.RESET_ALL)
            else:
                copy_func(source, destination)
                print(Fore.GREEN + f"File copied from {source} to {destination}" + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "Error: Please provide both source and destination" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)

while True:
    try:
        if __name__ == '__main__':
            Terminal().cmdloop()
    except Exception as e:
        print(f"A major error occured and we are restarting the system... {e}")
