import cmd
import os
import subprocess
import time
import platform
import sys
import shutil
import requests
import readline
from colorama import init, Fore, Style

# Initialize colorama for colored text output
init(autoreset=True)

class Terminal(cmd.Cmd):
    intro = Fore.GREEN + "Welcome to Alpha:v2\nType 'help' to see available commands." + Style.RESET_ALL
    prompt = Fore.YELLOW + os.getlogin() + "@alpha:v2 > " + Style.RESET_ALL
    history_file = ".py_terminal_history"
    GITHUB_URL = "https://raw.githubusercontent.com/SethJ152/PyTerminal/main/terminal.py"  # GitHub URL of the terminal.py file

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
        os.system("shutdown /s /f" if os.name == "nt" else "sudo shutdown now")

    def do_reboot(self, _):
        """Reboot the system."""
        print(Fore.YELLOW + "Rebooting the system..." + Style.RESET_ALL)
        os.system("reboot" if os.name != "nt" else "shutdown /r /f")

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
        print(Fore.YELLOW + "Updating terminal... Fetching the latest code..." + Style.RESET_ALL)
        try:
            # Download the terminal.py file from GitHub
            response = requests.get(self.GITHUB_URL)
            if response.status_code == 200:
                # Write the new code to terminal.py
                with open("/home/seth/Desktop/Python/terminal.py", "w") as f:
                    f.write(response.text)
                print(Fore.GREEN + "Terminal updated successfully!" + Style.RESET_ALL)

                # Restart the terminal program with the updated code
                python = sys.executable
                os.execl(python, python, *sys.argv)
            else:
                print(Fore.RED + "Error: Unable to fetch the terminal code from GitHub." + Style.RESET_ALL)
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
        print(Fore.GREEN + str(platform.uname()) + Style.RESET_ALL)

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

    def print_help(self):
        """Display available commands and descriptions."""
        commands = [
            ("exit", "Exit the terminal"),
            ("hostname", "Display the system hostname"),
            ("shutdown", "Shutdown the system"),
            ("reboot", "Reboot the system"),
            ("pause [time]", "Pause execution for the specified time"),
            ("diskspace", "Show free disk space"),
            ("uptime", "Display system uptime"),
            ("processes", "Show the current running processes"),
            ("clearhistory", "Clear the terminal command history"),
            ("update", "Re-run the terminal program"),
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

if __name__ == '__main__':
    Terminal().cmdloop()
