# Module 1: Getting Started with the Terminal

## Welcome! 🎉

Hey there! I'm so glad you're here. At 18, you're at the perfect age to learn the terminal — it's a skill that will serve you for your entire tech career (and even beyond!). Don't worry if you've never used a terminal before. We'll go slow, step by step, and by the end of this course, you'll be a terminal wizard. 🧙‍♂️

---

## What Is a Terminal?

Think of your computer like a house. You already know how to use the **graphical user interface (GUI)** — clicking icons, opening folders with your mouse, dragging and dropping files. That's like walking through rooms with lights on.

The **terminal** (also called the command line, command prompt, shell, or console) is like having a direct conversation with your computer. Instead of pointing and clicking, you **type commands** in text, and the computer responds with text.

### Why Learn the Terminal?

| Reason | Why It Matters |
|--------|---------------|
| **Speed** | Many tasks are faster with a few keystrokes than multiple clicks |
| **Power** | You can do things that GUIs simply can't do |
| **Remote Work** | Servers don't have GUIs — you control them via terminal |
| **Automation** | Write scripts to do repetitive tasks automatically |
| **Programming** | Most development tools are terminal-based |
| **Respect** | Other developers will take you seriously |
| **Problem Solving** | Understanding the terminal means understanding your computer |

---

## What Is a Shell?

The **shell** is the program that takes your typed commands and translates them into instructions for the computer.

The most common shell is **Bash** (Bourne Again Shell). Others include:
- **Zsh** (popular on macOS now)
- **Fish** (user-friendly)
- **PowerShell** (Windows)
- **cmd.exe** (old Windows)

For this course, we'll focus on **Bash** since it's the standard on Linux and widely used everywhere.

---

## Opening Your Terminal

### On macOS
1. Press `Cmd + Space` to open Spotlight
2. Type "Terminal" and press Enter
3. OR: Go to Applications → Utilities → Terminal

### On Linux (Ubuntu, Debian, etc.)
1. Press `Ctrl + Alt + T`
2. OR: Search for "Terminal" in your applications menu

### On Windows
Windows is a bit different. You have options:
- **Windows Terminal** (recommended — install from Microsoft Store)
- **Git Bash** (install Git for Windows)
- **WSL** (Windows Subsystem for Linux — the best option!)

> 💡 **Pro Tip**: If you're on Windows, I highly recommend setting up **WSL2** (Windows Subsystem for Linux). It gives you a real Linux environment inside Windows. Search "WSL install" and follow Microsoft's guide.

---

## Your First Look at the Terminal

When you open a terminal, you'll see something like this:

```
username@hostname:~$
```

Let's break this down:

| Part | Meaning |
|------|---------|
| `username` | Your user account name |
| `@` | Just a separator |
| `hostname` | Your computer's name |
| `:` | Another separator |
| `~` | Your current location (home directory) |
| `$` | You're a normal user (not admin) |

If you see `#` instead of `$`, that means you're running as the **root** (admin) user. Be careful with root!

---

## Your First Commands

Let's type some commands! After each command, press **Enter**.

### 1. `whoami` — Who Am I?

```bash
whoami
```

This tells you your username. Simple, but useful!

### 2. `date` — What Time Is It?

```bash
date
```

Shows the current date and time.

### 3. `cal` — Show a Calendar

```bash
cal
```

Shows a nice calendar for the current month.

### 4. `clear` — Clean the Screen

```bash
clear
```

Clears all the text and gives you a fresh screen. You can also press `Ctrl + L` as a shortcut.

### 5. `exit` — Close the Terminal

```bash
exit
```

Closes your terminal session. You can also just close the window.

---

## Terminal Anatomy

```
┌─────────────────────────────────────┐
│  Terminal Window                    │
│  ┌─────────────────────────────┐   │
│  │  Prompt: user@pc:~$         │   │
│  │  Command you type here      │   │
│  │  Output appears below       │   │
│  │  New prompt appears         │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## Basic Terminal Etiquette

### 1. The Prompt Waits for You
After you type a command and press Enter, the terminal shows output, then shows a new prompt. **Don't type while a command is running!**

### 2. Case Matters!
In the terminal, `Hello` and `hello` are **completely different**. Everything is case-sensitive.

### 3. Spaces Matter Too!
`cd my folder` is different from `cdmyfolder`. The space separates the command from its arguments.

### 4. Use Tab for Auto-Completion
Start typing a file or folder name, then press **Tab**. The terminal will try to complete it for you. Press Tab twice to see all options.

### 5. Up Arrow for History
Press the **Up Arrow** key to see previous commands you've typed. Down Arrow goes forward. This saves SO much time!

### 6. Ctrl+C to Stop a Running Command
If something is running and you want to stop it, press `Ctrl + C`. This sends an "interrupt" signal.

### 7. Ctrl+D to Exit
Press `Ctrl + D` to signal "end of input" — it often exits programs or the terminal itself.

---

## Common Terminal Shortcuts

| Shortcut | What It Does |
|----------|-------------|
| `Tab` | Auto-complete file/folder names |
| `↑` / `↓` | Browse command history |
| `Ctrl + C` | Stop the current command |
| `Ctrl + D` | Exit / send EOF |
| `Ctrl + L` | Clear screen |
| `Ctrl + A` | Move cursor to start of line |
| `Ctrl + E` | Move cursor to end of line |
| `Ctrl + U` | Clear everything before cursor |
| `Ctrl + K` | Clear everything after cursor |
| `Ctrl + W` | Delete the word before cursor |
| `Ctrl + R` | Search command history |
| `!!` | Run the last command again |
| `!n` | Run the nth command from history |

---

## Practice Time! 🎯

Try these exercises:

1. Open your terminal
2. Run `whoami` — what's your username?
3. Run `date` — what day of the week is it?
4. Run `cal` — find your birthday on the calendar
5. Run `clear` to clean up
6. Press Up Arrow — do you see previous commands?
7. Type `exit` to close, then reopen the terminal

---

## Key Takeaways

- ✅ The terminal is a text-based way to control your computer
- ✅ The shell (usually Bash) interprets your commands
- ✅ The prompt shows your username, computer name, and current location
- ✅ Commands are case-sensitive and space-sensitive
- ✅ Use Tab for auto-completion and Up Arrow for history
- ✅ `Ctrl + C` stops running commands

---

## Next Up

In **Module 2**, we'll learn how to **navigate the file system** — moving between folders, seeing what's inside them, and understanding the directory structure. This is where the real fun begins!

> 📝 **Homework**: Open your terminal 3 times today and run `whoami`, `date`, and `cal`. Get comfortable with the interface!
