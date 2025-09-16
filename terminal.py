#!/usr/bin/env python3
"""
PyTerminal improved version with original update command restored.
- Cross platform
- More Linux-like commands
- Tab completion, history, toolbar, nicer UI
- No finance vocabulary
- Includes 'update' command that fetches from GitHub and restarts
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, font, messagebox
import os
import sys
import platform
import threading
import subprocess
import shlex
import shutil
from pathlib import Path
import time
import datetime
import glob
import getpass
import json
import fnmatch
import random
import requests

HISTORY_FILE = Path.home() / ".pyterminal_history"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/SethJ152/PyTerminal/main/terminal.py"
GITHUB_COMMIT_API = "https://api.github.com/repos/SethJ152/PyTerminal/commits/main"

class PyTerminal(tk.Tk):
    def __init__(self, version="3.0.1"):
        super().__init__()
        self.version = version
        self.title(f"PyTerminal v{self.version}")
        self.configure(bg="#111214")
        self.geometry("980x640")
        self.minsize(700, 400)

        try:
            self.user = os.getlogin()
        except Exception:
            self.user = getpass.getuser()
        self.hostname = platform.node() or "host"
        self.cwd = Path.home()

        self.mono = font.Font(family="Courier", size=11)
        self.small_mono = font.Font(family="Courier", size=10)
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        self._build_toolbar()
        self._build_output_area()
        self._build_entry_area()
        self._build_statusbar()

        self.history = self._load_history()
        self.history_index = None

        self.commands = {
            "clear": self._cmd_clear,
            "cls": self._cmd_clear,
            "cd": self._cmd_cd,
            "pwd": self._cmd_pwd,
            "ls": self._cmd_ls,
            "ll": lambda args: self._cmd_ls(["-l"] + args),
            "cat": self._cmd_cat,
            "see": self._cmd_cat,
            "grep": self._cmd_grep,
            "touch": self._cmd_touch,
            "mkdir": self._cmd_mkdir,
            "rmdir": self._cmd_rmdir,
            "rm": self._cmd_rm,
            "cp": self._cmd_cp,
            "mv": self._cmd_mv,
            "whoami": self._cmd_whoami,
            "user": self._cmd_whoami,
            "open": self._cmd_open,
            "history": self._cmd_history,
            "tail": self._cmd_tail,
            "head": self._cmd_head,
            "find": self._cmd_find,
            "run": self._cmd_run,
            "ping": self._cmd_ping,
            "time": self._cmd_time,
            "date": self._cmd_time,
            "info": self._cmd_info,
            "help": self._cmd_help,
            "exit": self._cmd_exit,
            "quit": self._cmd_exit,
            "shutdown": self._cmd_shutdown,
            "reboot": self._cmd_reboot,
            "update": self._cmd_update,    # original update command restored
            "version": self._cmd_version,
            "py": self._cmd_py,           # run python scripts
            "why": self._cmd_why,         # optional project blurb
        }

        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Tab>", self._on_tab_complete)
        self.entry.bind("<Up>", self._history_up)
        self.entry.bind("<Down>", self._history_down)
        self.entry.bind("<Control-l>", lambda e: (self._cmd_clear([]), "break"))
        self.entry.bind("<Control-q>", lambda e: (self.destroy(), "break"))
        self.output.bind("<Control-c>", lambda e: self._copy_selection())
        self.output.bind("<Button-3>", self._show_context_menu)

        self._write_prompt()

    # UI builders
    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg="#0f1112", pady=6)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_home = ttk.Button(toolbar, text="Home", command=self._go_home)
        btn_up = ttk.Button(toolbar, text="Up", command=self._go_up)
        btn_clear = ttk.Button(toolbar, text="Clear", command=lambda: self._cmd_clear([]))
        btn_open = ttk.Button(toolbar, text="Open Folder", command=self._open_folder)

        for w in (btn_home, btn_up, btn_clear, btn_open):
            w.pack(side=tk.LEFT, padx=6)

        title = tk.Label(toolbar, text=f"{self.user}@{self.hostname}", bg="#0f1112", fg="#8ef0a8", font=self.small_mono)
        title.pack(side=tk.RIGHT, padx=8)

    def _build_output_area(self):
        frame = tk.Frame(self, bg="#111214")
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(6, 0))

        self.output = scrolledtext.ScrolledText(
            frame,
            bg="#0b0c0d",
            fg="#d9d9d9",
            insertbackground="#d9d9d9",
            font=self.mono,
            wrap=tk.NONE,
            relief=tk.FLAT
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        self.output.config(state=tk.DISABLED)

        self._tag_config("prompt", "#87FF87")
        self._tag_config("command", "#00FFAF")
        self._tag_config("error", "#FF6B6B")
        self._tag_config("info", "#9EE1FF")
        self._tag_config("success", "#A8FFA8")

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self._copy_selection)
        self.context_menu.add_command(label="Paste", command=self._paste_into_entry)
        self.context_menu.add_command(label="Select All", command=lambda: (self.output.tag_add("sel", "1.0", "end")))

    def _build_entry_area(self):
        bottom = tk.Frame(self, bg="#0b0c0d", padx=6, pady=6)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)

        self.prompt_label = tk.Label(bottom, text="", bg="#0b0c0d", fg="#87FF87", font=self.mono)
        self.prompt_label.pack(side=tk.LEFT)

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(bottom, textvariable=self.entry_var, bg="#1b1b1b", fg="#eaeaea",
                              insertbackground="#eaeaea", font=self.mono, relief=tk.FLAT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 6))
        self.entry.focus_set()

        run_btn = ttk.Button(bottom, text="Run", command=lambda: self._on_enter(None))
        run_btn.pack(side=tk.RIGHT)

    def _build_statusbar(self):
        self.status = tk.Label(self, text=str(self.cwd), bg="#0e0f10", fg="#bfbfbf", font=self.small_mono, anchor="w")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def _tag_config(self, name, color):
        self.output.tag_config(name, foreground=color)

    # helpers
    def _write(self, text, tag=None, newline=True):
        if newline:
            text = text + ("\n" if not text.endswith("\n") else "")
        self.output.config(state=tk.NORMAL)
        if tag:
            self.output.insert("end", text, tag)
        else:
            self.output.insert("end", text)
        self.output.see("end")
        self.output.config(state=tk.DISABLED)

    def _write_prompt(self):
        prompt = f"{self.user}@{self.hostname}:{self.cwd}$ "
        self.prompt_label.config(text=prompt)
        self._write(prompt, "prompt", newline=False)

    def _update_status(self):
        self.status.config(text=str(self.cwd))

    def _save_history(self):
        try:
            HISTORY_FILE.write_text("\n".join(self.history[-1000:]), encoding="utf-8")
        except Exception:
            pass

    def _load_history(self):
        try:
            if HISTORY_FILE.exists():
                lines = HISTORY_FILE.read_text(encoding="utf-8").splitlines()
                return [line for line in lines if line.strip()]
        except Exception:
            pass
        return []

    def _add_to_history(self, command_line):
        if command_line.strip():
            if not self.history or self.history[-1] != command_line:
                self.history.append(command_line)
            self._save_history()
        self.history_index = None

    def _show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _copy_selection(self):
        try:
            selected = self.output.selection_get()
            self.clipboard_clear()
            self.clipboard_append(selected)
        except Exception:
            pass

    def _paste_into_entry(self):
        try:
            txt = self.clipboard_get()
            self.entry.insert(tk.INSERT, txt)
        except Exception:
            pass

    # navigation
    def _go_home(self):
        self.cwd = Path.home()
        os.chdir(self.cwd)
        self._update_status()
        self._write(f"Changed to home: {self.cwd}", "info")
        self._write_prompt()

    def _go_up(self):
        self.cwd = self.cwd.parent
        os.chdir(self.cwd)
        self._update_status()
        self._write_prompt()

    def _open_folder(self):
        try:
            if sys.platform.startswith("win"):
                os.startfile(self.cwd)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(self.cwd)])
            else:
                subprocess.Popen(["xdg-open", str(self.cwd)])
            self._write(f"Opened folder {self.cwd}", "info")
        except Exception as e:
            self._write(f"Error opening folder: {e}", "error")

    # input / completion / history
    def _on_enter(self, event):
        cmdline = self.entry_var.get().strip()
        if not cmdline:
            self._write_prompt()
            self.entry_var.set("")
            return

        self._write(cmdline, "command")
        self._add_to_history(cmdline)
        self.entry_var.set("")

        parts = shlex.split(cmdline)
        if not parts:
            self._write_prompt()
            return

        cmd = parts[0]
        args = parts[1:]

        if cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                self._write(f"Error executing builtin {cmd}: {e}", "error")
                self._write_prompt()
        else:
            self._run_system_command(cmdline)

    def _on_tab_complete(self, event):
        current = self.entry_var.get()
        tokens = shlex.split(current) if current.strip() else []
        if not tokens:
            prefix = ""
            last = current
        else:
            last = current.split()[-1]
            prefix = " ".join(current.split()[:-1])
            if prefix:
                prefix += " "

        matches = glob.glob(last + "*")
        if not matches:
            matches = [c for c in list(self.commands.keys()) + self._binaries_in_path() if c.startswith(last)]

        if not matches:
            return "break"

        if len(matches) == 1:
            completion = matches[0]
            if os.path.isdir(completion):
                completion = completion + os.sep
            self.entry_var.set(prefix + completion + " ")
        else:
            self._write("\n" + "  ".join(matches))
            self._write_prompt()
        return "break"

    def _binaries_in_path(self):
        paths = os.environ.get("PATH", "").split(os.pathsep)
        bins = set()
        for p in paths:
            try:
                for f in os.listdir(p):
                    bins.add(f)
            except Exception:
                pass
        return sorted(bins)

    def _history_up(self, event):
        if not self.history:
            return "break"
        if self.history_index is None:
            self.history_index = len(self.history) - 1
        else:
            self.history_index = max(0, self.history_index - 1)
        self.entry_var.set(self.history[self.history_index])
        return "break"

    def _history_down(self, event):
        if self.history_index is None:
            return "break"
        self.history_index = min(len(self.history) - 1, self.history_index + 1)
        self.entry_var.set(self.history[self.history_index] if self.history_index < len(self.history) else "")
        if self.history_index == len(self.history) - 1:
            self.history_index = None
        return "break"

    # run system commands
    def _run_system_command(self, command_line):
        def target():
            try:
                process = subprocess.Popen(
                    command_line,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                    cwd=str(self.cwd),
                    universal_newlines=True,
                )
                for line in iter(process.stdout.readline, ""):
                    if line:
                        self._write(line.rstrip())
                process.stdout.close()
                process.wait()
            except Exception as e:
                self._write(f"Error running command: {e}", "error")
            finally:
                self._write_prompt()

        threading.Thread(target=target, daemon=True).start()

    # built-in commands
    def _cmd_clear(self, args):
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.config(state=tk.DISABLED)
        self._write_prompt()

    def _cmd_cd(self, args):
        target = args[0] if args else str(Path.home())
        try:
            new = (self.cwd / target) if not os.path.isabs(target) else Path(target)
            new = new.expanduser().resolve()
            if new.is_dir():
                self.cwd = new
                os.chdir(self.cwd)
                self._update_status()
                self._write_prompt()
            else:
                self._write(f"cd: {target}: No such directory", "error")
                self._write_prompt()
        except Exception as e:
            self._write(f"cd error: {e}", "error")
            self._write_prompt()

    def _cmd_pwd(self, args):
        self._write(str(self.cwd))
        self._write_prompt()

    def _cmd_ls(self, args):
        long = False
        path = self.cwd
        flags = [a for a in args if a.startswith("-")]
        for f in flags:
            if "l" in f:
                long = True
        nonflags = [a for a in args if not a.startswith("-")]
        if nonflags:
            path = Path(nonflags[0]).expanduser()
            if not path.is_absolute():
                path = (self.cwd / path).resolve()

        try:
            entries = list(path.iterdir())
            if long:
                for e in sorted(entries, key=lambda x: x.name):
                    stat = e.stat()
                    size = stat.st_size
                    mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    typ = "d" if e.is_dir() else "-"
                    self._write(f"{typ} {size:>8} {mtime} {e.name}")
            else:
                chunk = []
                for e in sorted(entries, key=lambda x: x.name):
                    chunk.append(e.name + (os.sep if e.is_dir() else ""))
                self._write("  ".join(chunk))
        except Exception as ex:
            self._write(f"ls error: {ex}", "error")
        self._write_prompt()

    def _cmd_cat(self, args):
        if not args:
            self._write("Usage: cat [file]", "error")
            self._write_prompt()
            return
        target = Path(args[0]).expanduser()
        if not target.is_absolute():
            target = (self.cwd / target).resolve()
        try:
            with target.open("r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    self._write(line.rstrip())
        except Exception as e:
            self._write(f"cat error: {e}", "error")
        self._write_prompt()

    def _cmd_grep(self, args):
        if not args:
            self._write("Usage: grep [pattern] [file(optional)]", "error")
            self._write_prompt()
            return
        pattern = args[0]
        files = args[1:] or ["*"]
        for pat in files:
            paths = list(self.cwd.glob(pat))
            if not paths:
                self._write(f"grep: {pat}: No match", "error")
            for p in paths:
                if p.is_file():
                    try:
                        with p.open("r", encoding="utf-8", errors="replace") as fh:
                            for i, line in enumerate(fh, 1):
                                if pattern in line:
                                    self._write(f"{p}:{i}:{line.rstrip()}")
                    except Exception as e:
                        self._write(f"grep error reading {p}: {e}", "error")
        self._write_prompt()

    def _cmd_touch(self, args):
        if not args:
            self._write("Usage: touch [file]", "error")
            self._write_prompt()
            return
        for fname in args:
            p = (self.cwd / fname).expanduser()
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.touch()
                self._write(f"touched {p}")
            except Exception as e:
                self._write(f"touch error: {e}", "error")
        self._write_prompt()

    def _cmd_mkdir(self, args):
        if not args:
            self._write("Usage: mkdir [dir]", "error")
            self._write_prompt()
            return
        for d in args:
            p = (self.cwd / d).expanduser()
            try:
                p.mkdir(parents=True, exist_ok=True)
                self._write(f"created {p}")
            except Exception as e:
                self._write(f"mkdir error: {e}", "error")
        self._write_prompt()

    def _cmd_rmdir(self, args):
        if not args:
            self._write("Usage: rmdir [dir]", "error")
            self._write_prompt()
            return
        for d in args:
            p = (self.cwd / d).expanduser()
            try:
                p.rmdir()
                self._write(f"removed {p}")
            except Exception as e:
                self._write(f"rmdir error: {e}", "error")
        self._write_prompt()

    def _cmd_rm(self, args):
        if not args:
            self._write("Usage: rm [file or dir]", "error")
            self._write_prompt()
            return
        for t in args:
            p = (self.cwd / t).expanduser()
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
                self._write(f"removed {p}")
            except Exception as e:
                self._write(f"rm error: {e}", "error")
        self._write_prompt()

    def _cmd_cp(self, args):
        if len(args) < 2:
            self._write("Usage: cp [src] [dst]", "error")
            self._write_prompt()
            return
        src = (self.cwd / args[0]).expanduser()
        dst = (self.cwd / args[1]).expanduser()
        try:
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            self._write("copy successful")
        except Exception as e:
            self._write(f"cp error: {e}", "error")
        self._write_prompt()

    def _cmd_mv(self, args):
        if len(args) < 2:
            self._write("Usage: mv [src] [dst]", "error")
            self._write_prompt()
            return
        src = (self.cwd / args[0]).expanduser()
        dst = (self.cwd / args[1]).expanduser()
        try:
            shutil.move(str(src), str(dst))
            self._write("move successful")
        except Exception as e:
            self._write(f"mv error: {e}", "error")
        self._write_prompt()

    def _cmd_whoami(self, args):
        self._write(self.user)
        self._write_prompt()

    def _cmd_open(self, args):
        target = self.cwd if not args else (self.cwd / args[0]).expanduser()
        if not target.exists():
            self._write(f"open: {target}: No such file or directory", "error")
            self._write_prompt()
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(target))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(target)])
            else:
                subprocess.Popen(["xdg-open", str(target)])
            self._write(f"Opened {target}")
        except Exception as e:
            self._write(f"open error: {e}", "error")
        self._write_prompt()

    def _cmd_history(self, args):
        for i, entry in enumerate(self.history[-200:], start=max(0, len(self.history)-200)):
            self._write(f"{i}: {entry}")
        self._write_prompt()

    def _cmd_tail(self, args):
        if not args:
            self._write("Usage: tail [-n lines] file", "error")
            self._write_prompt()
            return
        lines = 10
        path = args[-1]
        if args[0].startswith("-n"):
            try:
                lines = int(args[0][2:])
                path = args[1]
            except Exception:
                pass
        p = (self.cwd / path).expanduser()
        if not p.exists():
            self._write("tail: file not found", "error")
            self._write_prompt()
            return
        try:
            with p.open("r", encoding="utf-8", errors="replace") as f:
                content = f.read().splitlines()
                for line in content[-lines:]:
                    self._write(line)
        except Exception as e:
            self._write(f"tail error: {e}", "error")
        self._write_prompt()

    def _cmd_head(self, args):
        if not args:
            self._write("Usage: head [-n lines] file", "error")
            self._write_prompt()
            return
        lines = 10
        path = args[-1]
        if args[0].startswith("-n"):
            try:
                lines = int(args[0][2:])
                path = args[1]
            except Exception:
                pass
        p = (self.cwd / path).expanduser()
        if not p.exists():
            self._write("head: file not found", "error")
            self._write_prompt()
            return
        try:
            with p.open("r", encoding="utf-8", errors="replace") as f:
                for i, line in enumerate(f):
                    if i >= lines:
                        break
                    self._write(line.rstrip())
        except Exception as e:
            self._write(f"head error: {e}", "error")
        self._write_prompt()

    def _cmd_find(self, args):
        if not args:
            self._write("Usage: find [pattern]", "error")
            self._write_prompt()
            return
        pattern = args[0]
        matches = []
        for root, dirs, files in os.walk(self.cwd):
            for name in files + dirs:
                if fnmatch.fnmatch(name, pattern):
                    matches.append(os.path.join(root, name))
        if matches:
            for m in matches:
                self._write(m)
        else:
            self._write("No matches")
        self._write_prompt()

    def _cmd_run(self, args):
        if not args:
            self._write("Usage: run [command]", "error")
            self._write_prompt()
            return
        self._run_system_command(" ".join(args))

    def _cmd_ping(self, args):
        if not args:
            self._write("Usage: ping [host]", "error")
            self._write_prompt()
            return
        host = args[0]
        count_flag = "-n" if sys.platform.startswith("win") else "-c"
        self._run_system_command(f"ping {count_flag} 4 {host}")

    def _cmd_time(self, args):
        now = datetime.datetime.now()
        self._write(now.strftime("%A, %B %d, %Y %I:%M:%S %p"))
        self._write_prompt()

    def _cmd_info(self, args):
        info = [
            f"System: {platform.system()} {platform.release()}",
            f"Machine: {platform.machine()}",
            f"Processor: {platform.processor()}",
            f"Python: {platform.python_version()}",
            f"CWD: {self.cwd}",
        ]
        self._write("\n".join(info))
        self._write_prompt()

    def _cmd_help(self, args):
        items = sorted(self.commands.keys())
        self._write("Built-in commands:")
        cols = 4
        for i in range(0, len(items), cols):
            self._write("  ".join(items[i:i+cols]))
        self._write("You can also run any system command.")
        self._write_prompt()

    def _cmd_exit(self, args):
        self.destroy()

    def _confirm(self, message):
        return messagebox.askyesno("Confirm", message)

    def _cmd_shutdown(self, args):
        if not self._confirm("Shutdown the machine? This requires appropriate privileges. Continue?"):
            self._write("Shutdown cancelled.")
            self._write_prompt()
            return
        try:
            if sys.platform.startswith("win"):
                subprocess.Popen("shutdown /s /t 0", shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["sudo", "shutdown", "-h", "now"])
            else:
                subprocess.Popen(["sudo", "shutdown", "now"])
            self._write("Shutdown initiated.")
        except Exception as e:
            self._write(f"shutdown error: {e}", "error")
        self._write_prompt()

    def _cmd_reboot(self, args):
        if not self._confirm("Reboot the machine? This requires appropriate privileges. Continue?"):
            self._write("Reboot cancelled.")
            self._write_prompt()
            return
        try:
            if sys.platform.startswith("win"):
                subprocess.Popen("shutdown /r /t 0", shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["sudo", "shutdown", "-r", "now"])
            else:
                subprocess.Popen(["sudo", "reboot"])
            self._write("Reboot initiated.")
        except Exception as e:
            self._write(f"reboot error: {e}", "error")
        self._write_prompt()

    # original update command restored, adapted to GUI
    def _cmd_update(self, args):
        self._write("Gathering update data...", "command")
        try:
            commit_response = requests.get(GITHUB_COMMIT_API, timeout=10)
            if commit_response.status_code == 200:
                commit_data = commit_response.json()
                latest_commit_name = commit_data.get("commit", {}).get("message", "")
            else:
                self._write("Error: Unable to fetch the latest commit from GitHub.", "error")
                self._write_prompt()
                return
        except Exception as e:
            self._write(f"Error: {e}", "error")
            self._write_prompt()
            return

        if self.version != latest_commit_name:
            self._write(f"Update available: {latest_commit_name}", "info")
            confirm = messagebox.askyesno("Update Available", f"Update to version '{latest_commit_name}'?\nThis will restart the terminal.")
            if not confirm:
                self._write("Update cancelled.")
                self._write_prompt()
                return

            try:
                response = requests.get(GITHUB_RAW_URL, timeout=20)
                if response.status_code == 200:
                    script_path = os.path.abspath(__file__)
                    # backup current script
                    try:
                        backup = script_path + ".backup"
                        shutil.copy2(script_path, backup)
                    except Exception:
                        pass
                    with open(script_path, "w", encoding="utf-8") as f:
                        f.write(response.text)
                    self._write("Terminal updated successfully!", "success")
                    python = sys.executable
                    if platform.system().lower().startswith("win"):
                        try:
                            subprocess.Popen([python, script_path])
                        except Exception as e:
                            self._write(f"Could not relaunch on Windows: {e}", "error")
                    else:
                        try:
                            os.execl(python, python, *sys.argv)
                        except Exception as e:
                            self._write(f"Could not relaunch: {e}", "error")
                else:
                    self._write("Error: Unable to fetch updated code.", "error")
            except requests.exceptions.RequestException as e:
                self._write(f"Error during update: {str(e)}", "error")
        else:
            self._write(f"Already up to date: {self.version}")
        self._write_prompt()

    def _cmd_version(self, args):
        self._write(f"Version: {self.version}")
        self._write_prompt()

    def _cmd_py(self, args):
        if not args:
            self._write("Usage: py [script.py] [args...]", "error")
            self._write_prompt()
            return
        script = args[0]
        rest_args = args[1:]
        if not script.endswith(".py"):
            script = script + ".py"
        cmd = f"{sys.executable} {shlex.quote(script)} {' '.join(shlex.quote(a) for a in rest_args)}"
        self._run_system_command(cmd)

    def _cmd_why(self, args):
        self._write("This project is a cross-platform terminal emulator designed to be simple, user-friendly, and fully open-source. Built with accessibility and customization in mind, it offers an intuitive interface for executing commands while remaining lightweight and efficient. Contributions and feature suggestions are welcome.")
        self._write_prompt()

# run app
def main():
    app = PyTerminal()
    app.mainloop()

if __name__ == "__main__":
    main()
