import tkinter as tk
from tkinter import scrolledtext
import subprocess
import os
import sys
import platform
import requests
import time
import shutil
import datetime
import getpass
from tkinter import messagebox
from colorama import Fore, Style  # if not already imported
import threading

class MintTerminalGUI:
    def __init__(self, root):
        self.version = "2.5.1"
        self.root = root
        self.root.title(f"PyTerminal v{self.version}")

        self.current_version = self.version
        self.GITHUB_URL = "https://raw.githubusercontent.com/SethJ152/PyTerminal/main/terminal.py"

        # Define color scheme (inspired by Linux Mint dark theme)
        self.bg_color = "#1B1D1E"
        self.fg_color = "#C7C7C7"
        self.prompt_color = "#87FF87"
        self.entry_bg = "#2E2F30"
        self.entry_fg = "#FFFFFF"
        self.output_bg = self.bg_color
        self.output_fg = self.fg_color
        self.highlight_color = "#00FFAF"
        self.error_color = "#FF5555"

        self.root.configure(bg=self.bg_color)
        self.root.geometry("960x640")

        try:
            self.user = os.getlogin()
        except:
            self.user = getpass.getuser()
        try:
            self.hostname = platform.node()
        except:
            self.hostname = "host"
        self.cwd = os.path.expanduser("~")

        # Frame for input
        self.top_frame = tk.Frame(self.root, bg=self.bg_color)
        self.top_frame.pack(fill=tk.X, padx=5, pady=10)

        self.command_label = tk.Label(
            self.top_frame,
            text="Command:",
            fg=self.highlight_color,
            bg=self.bg_color,
            font=("Monospace", 10)
        )
        self.command_label.pack(side=tk.LEFT, padx=(5, 0))

        self.command_entry = tk.Entry(
            self.top_frame,
            bg=self.entry_bg,
            fg=self.entry_fg,
            insertbackground=self.entry_fg,
            font=("Monospace", 11),
            relief="flat",
            borderwidth=2
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        self.command_entry.bind("<Return>", self.handle_enter)
        self.command_entry.focus()

        # Frame for output
        self.output_frame = tk.Frame(self.root, bg=self.bg_color)
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.terminal_output = scrolledtext.ScrolledText(
            self.output_frame,
            bg=self.output_bg,
            fg=self.output_fg,
            insertbackground=self.output_fg,
            font=("Monospace", 11),
            relief="flat",
            borderwidth=0,
            wrap=tk.WORD
        )
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.bind("<Key>", lambda e: "break")

        self.terminal_output.tag_config("error", foreground=self.error_color)
        self.terminal_output.tag_config("command", foreground=self.highlight_color)
        self.terminal_output.tag_config("prompt", foreground=self.prompt_color)

        self.commands = {
            "clear": self.clear_screen,
            "cd": self.change_directory,
            "ls": self.cmd_list,
            "cdir": self.cmd_currentdir,
            "see": self.cmd_showfile,
            "echo": self.cmd_print,
            "run": self.cmd_run,
            "create": self.cmd_makedir,
            "removef": self.cmd_removefile,
            "removed": self.cmd_removedir,
            "copy": self.cmd_copy,
            "move": self.cmd_move,
            "info": self.cmd_systeminfo,
            "user": self.cmd_currentuser,
            "time": self.cmd_currenttime,
            "ip": self.cmd_ip,
            "calc": self.cmd_calculate,
            "sl": self.cmd_pause,
            "shutdown": self.cmd_shutdown,
            "reboot": self.cmd_reboot,
            "ping": self.cmd_ping,
            "who": self.cmd_whois,
            "date": self.cmd_datetime,
            "host": self.cmd_hostname,
            "uh": self.cmd_userhome,
            "help": self.cmd_help,
            "exit": self.exit_app,
            "update": self.cmd_update,
            "version": self.cmd_version,
            "py": self.cmd_python
        }

        self.show_prompt()

    def show_prompt(self):
        prompt_str = f"{self.user.lower()}@{self.hostname.lower()}:~$ "
        self.terminal_output.insert(tk.END, prompt_str, "prompt")
        self.terminal_output.see(tk.END)

    def handle_enter(self, event):
        command_line = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)
        self.terminal_output.insert(tk.END, command_line + "\n", "command")

        if not command_line:
            self.show_prompt()
            return

        parts = command_line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                self.print_output(f"Error: {e}", "error")
        else:
            self.run_system_command(command_line)

        self.show_prompt()

    def print_output(self, text, tag=None):
        self.terminal_output.insert(tk.END, text + "\n", tag)
        self.terminal_output.see(tk.END)

    def clear_screen(self, args=None):
        self.terminal_output.delete(1.0, tk.END)

    def change_directory(self, args):
        if not args:
            self.print_output("Usage: cd [path]", "error")
            return
        try:
            os.chdir(args[0])
            self.cwd = os.getcwd()
        except Exception as e:
            self.print_output(f"Error: {e}", "error")
    def cmd_version(self, args=None):
        self.print_output(f"Version: {self.version}")

    def cmd_python(self, args):
        if not args:
            self.print_output("Usage: python [script.py] [args...]", "error")
            return
        try:
            cmd = f"python3 {' '.join(args)}.py"
            self.run_system_command(cmd)
        except:
            try:
                cmd = f"python3 {' '.join(args)}.py3"
                self.run_system_command(cmd)
            except:
                try:
                    cmd = f"python3 {' '.join(args)}.py3"
                    self.run_system_command(cmd)
                except:
                    self.print_output("Not found.")
    def cmd_list(self, args):
        path = args[0] if args else "."
        try:
            for item in os.listdir(path):
                self.print_output(item)
        except Exception as e:
            self.print_output(f"Error: {e}", "error")

    def cmd_currentdir(self, args=None):
        self.print_output(self.cwd)

    def cmd_showfile(self, args):
        if not args:
            self.print_output("Usage: showfile [filename]", "error")
            return
        try:
            with open(args[0], "r") as file:
                self.print_output(file.read())
        except Exception as e:
            self.print_output(f"Error: {e}", "error")

    def cmd_print(self, args):
        self.print_output(" ".join(args))

    def cmd_run(self, args):
        if not args:
            self.print_output("Usage: run [command]", "error")
            return
        self.run_system_command(" ".join(args))

    def cmd_makedir(self, args):
        if not args:
            self.print_output("Usage: makedir [dirname]", "error")
            return
        try:
            os.makedirs(args[0], exist_ok=True)
            self.print_output(f"Directory '{args[0]}' created.")
        except Exception as e:
            self.print_output(f"Error: {e}", "error")

    def cmd_removefile(self, args):
        if not args:
            self.print_output("Usage: removefile [filename]", "error")
            return
        try:
            os.remove(args[0])
            self.print_output(f"File '{args[0]}' removed.")
        except Exception as e:
            self.print_output(f"Error: {e}", "error")

    def cmd_removedir(self, args):
        if not args:
            self.print_output("Usage: removedir [dirname]", "error")
            return
        try:
            shutil.rmtree(args[0])
            self.print_output(f"Directory '{args[0]}' removed.")
        except Exception as e:
            self.print_output(f"Error: {e}", "error")

    def cmd_copy(self, args):
        if len(args) < 2:
            self.print_output("Usage: copy [src] [dst]", "error")
            return
        try:
            if os.path.isdir(args[0]):
                shutil.copytree(args[0], args[1])
            else:
                shutil.copy2(args[0], args[1])
            self.print_output("Copy successful.")
        except Exception as e:
            self.print_output(f"Error: {e}", "error")

    def cmd_move(self, args):
        if len(args) < 2:
            self.print_output("Usage: move [src] [dst]", "error")
            return
        try:
            shutil.move(args[0], args[1])
            self.print_output("Move successful.")
        except Exception as e:
            self.print_output(f"Error: {e}", "error")

    def cmd_systeminfo(self, args=None):
        info = [
            f"System: {platform.system()}",
            f"Node: {platform.node()}",
            f"Release: {platform.release()}",
            f"Version: {platform.version()}",
            f"Machine: {platform.machine()}",
            f"Processor: {platform.processor()}"
        ]
        self.print_output("\n".join(info))

    def cmd_currentuser(self, args=None):
        self.print_output(self.user)

    def cmd_currenttime(self, args=None):
        self.print_output(time.strftime("%Y-%m-%d %H:%M:%S"))

    def cmd_ip(self, args=None):
        try:
            info = requests.get("https://ipinfo.io/json").json()
            self.print_output(f"IP: {info.get('ip')}\nLocation: {info.get('city')}, {info.get('region')}, {info.get('country')}")
        except Exception as e:
            self.print_output(f"Error: {e}", "error")

    def cmd_calculate(self, args):
        try:
            result = eval(" ".join(args))
            self.print_output(f"Result: {result}")
        except Exception as e:
            self.print_output(f"Error: {e}", "error")

    def cmd_pause(self, args):
        try:
            time.sleep(int(args[0]))
        except:
            self.print_output("Usage: pause [seconds]", "error")

    def cmd_shutdown(self, args=None):
        cmd = "shutdown /s /f" if os.name == "nt" else "sudo shutdown now"
        subprocess.run(cmd, shell=True)

    def cmd_reboot(self, args=None):
        cmd = "shutdown /r /f" if os.name == "nt" else "sudo reboot"
        subprocess.run(cmd, shell=True)

    def cmd_ping(self, args):
        if not args:
            self.print_output("Usage: ping [host]", "error")
            return
        cmd = f"ping {'-n' if os.name == 'nt' else '-c'} 4 {args[0]}"
        self.run_system_command(cmd)

    def cmd_whois(self, args):
        if not args:
            self.print_output("Usage: whois [domain]", "error")
            return
        self.run_system_command(f"whois {args[0]}")

    def cmd_datetime(self, args=None):
        now = datetime.datetime.now()
        self.print_output(now.strftime("%A, %B %d, %Y %I:%M:%S %p"))

    def cmd_hostname(self, args=None):
        self.print_output(platform.node())

    def cmd_userhome(self, args=None):
        self.print_output(os.path.expanduser("~"))

    def cmd_update(self, _):
        """Download the latest terminal.py from GitHub and replace the current script."""
        self.print_output("Gathering update data...", "command")

        commit_url = "https://api.github.com/repos/SethJ152/PyTerminal/commits/main"
        try:
            commit_response = requests.get(commit_url)
            if commit_response.status_code == 200:
                commit_data = commit_response.json()
                latest_commit_name = commit_data['commit']['message']
            else:
                self.print_output("Error: Unable to fetch the latest commit from GitHub.", "error")
                return
        except Exception as e:
            self.print_output(f"Error: {e}", "error")
            return

        if self.current_version != latest_commit_name:
            self.print_output(f"Update available: {latest_commit_name}", "command")

            confirm = messagebox.askyesno("Update Available", f"Update to version '{latest_commit_name}'?\nThis will restart the terminal.")
            if not confirm:
                self.print_output("Update cancelled.")
                return

            try:
                response = requests.get(self.GITHUB_URL)
                if response.status_code == 200:
                    script_path = os.path.abspath(__file__)
                    with open(script_path, "w") as f:
                        f.write(response.text)
                    self.print_output("Terminal updated successfully!", "command")

                    python = sys.executable
                    if platform.system() == "Windows":
                        subprocess.Popen([python, script_path])
                    else:
                        os.execl(python, python, *sys.argv)

                else:
                    self.print_output("Error: Unable to fetch updated code.", "error")
            except requests.exceptions.RequestException as e:
                self.print_output(f"Error during update: {str(e)}", "error")
        else:
            self.print_output(f"Already up to date: {self.current_version}")


    def run_system_command(self, command):
        def run():
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                    universal_newlines=True,
                    cwd=self.cwd
                )
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.terminal_output.after(0, self.print_output, line.rstrip())
                process.stdout.close()
                process.wait()
            except Exception as e:
                self.terminal_output.after(0, self.print_output, str(e), "error")

        threading.Thread(target=run, daemon=True).start()

    def cmd_help(self, args=None):
        help_text = [
            "Available Commands:",
            "    clear      - Clear the terminal",
            "    cd         - Change directory",
            "    ls         - List contents of directory",
            "    cdir       - Show current working directory",
            "    see        - Show contents of a file",
            "    echo       - Print text",
            "    run        - Run system command",
            "    create     - Make a directory",
            "    removef    - Delete a file",
            "    removed    - Delete a directory",
            "    copy       - Copy file or directory",
            "    move       - Move file or directory",
            "    info       - Show system information",
            "    user       - Show username",
            "    time       - Show current time",
            "    ip         - Get public IP",
            "    calc       - Evaluate math expression",
            "    sl         - Pause for N seconds",
            "    shutdown   - Shutdown system",
            "    reboot     - Reboot system",
            "    ping       - Ping a host",
            "    who        - Whois lookup",
            "    date       - Show date and time",
            "    host       - Show hostname",
            "    uh         - Show user's home path",
            "    help       - Show this help message",
            "    py         - Run a Python script",
            "    update     - Update terminal",
            "    version    - Show version",
            "    exit       - Exit the application"
        ]
        self.print_output("\n".join(help_text))
        

    def exit_app(self, args=None):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MintTerminalGUI(root)
    root.mainloop()
