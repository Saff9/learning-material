# Module 11: Advanced Terminal Topics

## Introduction

Congratulations! You've made it to the advanced section! 🎉

By now, you know how to navigate, manage files, edit text, control permissions, manage processes, use pipes, search, network, and write scripts. In this module, we'll cover the finishing touches that separate beginners from power users.

---

## Environment Variables

Environment variables are settings that affect how your shell and programs behave.

### Viewing Variables

```bash
env                    # Show all environment variables
printenv               # Same as env
printenv PATH          # Show specific variable
echo $PATH             # Same thing
echo $HOME             # Your home directory
echo $USER             # Your username
echo $SHELL            # Your current shell
echo $PWD              # Current directory
echo $OLDPWD           # Previous directory
echo $LANG             # Language/locale settings
```

### Common Environment Variables

| Variable | Purpose |
|----------|---------|
| `PATH` | Directories to search for executables |
| `HOME` | Your home directory |
| `USER` | Your username |
| `SHELL` | Your login shell |
| `EDITOR` | Default text editor |
| `LANG` | Language and character encoding |
| `PS1` | Your prompt format |
| `HISTSIZE` | Number of commands to remember |
| `TERM` | Terminal type |

### Setting Variables

```bash
# Set for current session only
export MY_VAR="hello"

# Set and make available to child processes
export PATH="$PATH:/new/directory"

# Remove a variable
unset MY_VAR
```

### Making Variables Permanent

Add them to your shell's configuration file:

```bash
# For Bash
nano ~/.bashrc

# Add this line:
export MY_VAR="hello"
export PATH="$PATH:$HOME/scripts"

# Reload the file:
source ~/.bashrc
```

---

## The `PATH` Variable

`PATH` tells the shell where to look for executable programs.

```bash
echo $PATH
# Output: /usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
```

Each directory is separated by `:` (on Linux/macOS) or `;` (on Windows).

### Adding to PATH

```bash
# Temporarily (current session)
export PATH="$PATH:$HOME/bin"

# Permanently (add to ~/.bashrc)
echo 'export PATH="$PATH:$HOME/bin"' >> ~/.bashrc
source ~/.bashrc
```

> 💡 **Best Practice**: Create a `~/bin` or `~/.local/bin` directory for your personal scripts and add it to PATH.

---

## Aliases

Aliases are shortcuts for commands.

### Creating Aliases

```bash
alias ll='ls -la'              # Create alias
alias ..='cd ..'               # Go up one directory
alias ...='cd ../..'           # Go up two directories
alias mkdirp='mkdir -p'        # Create parent directories
alias gs='git status'          # Git shortcut
alias gp='git pull'            # Git shortcut
alias update='sudo apt update && sudo apt upgrade'  # System update
```

### Viewing Aliases

```bash
alias              # Show all aliases
alias ll           # Show specific alias
```

### Removing Aliases

```bash
unalias ll
```

### Making Aliases Permanent

Add them to `~/.bashrc`:

```bash
cat >> ~/.bashrc << 'EOF'
# My custom aliases
alias ll='ls -la'
alias ..='cd ..'
alias gs='git status'
EOF

source ~/.bashrc
```

---

## Customizing Your Prompt (`PS1`)

Your prompt is controlled by the `PS1` variable.

### Prompt Escape Codes

| Code | Meaning |
|------|---------|
| `\u` | Username |
| `\h` | Hostname (short) |
| `\H` | Hostname (full) |
| `\w` | Current directory (full path) |
| `\W` | Current directory (basename only) |
| `\d` | Date |
| `\t` | Time (24-hour) |
| `\T` | Time (12-hour) |
| `\$` | `$` for normal user, `#` for root |
| `\n` | New line |
| `\[` / `\]` | Non-printing characters (for colors) |

### Color Codes

| Code | Color |
|------|-------|
| `\033[0;30m` | Black |
| `\033[0;31m` | Red |
| `\033[0;32m` | Green |
| `\033[0;33m` | Yellow |
| `\033[0;34m` | Blue |
| `\033[0;35m` | Purple |
| `\033[0;36m` | Cyan |
| `\033[0;37m` | White |
| `\033[0m` | Reset |

### Example Custom Prompts

```bash
# Simple colored prompt
export PS1="\[\033[0;32m\]\u@\h\[\033[0m\]:\[\033[0;34m\]\W\[\033[0m\]\$ "

# Two-line prompt with git branch
export PS1="\[\033[0;32m\]\u@\h\[\033[0m\]:\[\033[0;34m\]\w\[\033[0m\]\n\$ "

# Minimal prompt
export PS1="\W \$ "
```

---

## History

### Viewing History

```bash
history              # Show all previous commands
history | tail -n 20  # Show last 20 commands
history | grep "ssh" # Find ssh commands in history
```

### Using History

| Shortcut | Action |
|----------|--------|
| `↑` / `↓` | Browse history |
| `Ctrl + R` | Reverse search history |
| `!!` | Run last command |
| `!n` | Run command number n |
| `!-n` | Run nth command from end |
| `!string` | Run last command starting with "string" |
| `!?string` | Run last command containing "string" |
| `!!:p` | Print last command without running |
| `!$` | Last argument of previous command |
| `!*` | All arguments of previous command |

### History Expansion Examples

```bash
!!                   # Run last command again
sudo !!              # Run last command with sudo
!ls                  # Run last command starting with "ls"
!-2                  # Run second-to-last command
!$                   # Use last argument
mkdir newfolder && cd !$   # Create folder and cd into it
```

### History Settings

```bash
# Add to ~/.bashrc
export HISTSIZE=10000           # Remember 10,000 commands
export HISTFILESIZE=20000       # History file size
export HISTCONTROL=ignoredups   # Don't save duplicate commands
export HISTTIMEFORMAT="%Y-%m-%d %H:%M:%S "  # Show timestamps
shopt -s histappend             # Append to history, don't overwrite
```

---

## Tab Completion

Tab completion is one of the biggest time-savers in the terminal!

### Basic Completion

- Press `Tab` once to complete if there's only one option
- Press `Tab` twice to see all options

### Advanced Completion

```bash
# Complete commands
fir<Tab>          # Completes to "firefox" if installed

# Complete file paths
cd /usr/sh<Tab>   # Completes to /usr/share/

# Complete variables
echo $HO<Tab>     # Completes to $HOME

# Complete usernames (after ~)
cd ~ro<Tab>       # Completes to ~root/

# Complete hostnames (after @)
ssh user@ser<Tab> # Completes if in known_hosts
```

### Bash Completion Package

Install for even better completion:

```bash
sudo apt install bash-completion    # Ubuntu/Debian
brew install bash-completion         # macOS
```

---

## Package Management

### Ubuntu/Debian (`apt`)

```bash
sudo apt update                    # Update package lists
sudo apt upgrade                   # Upgrade installed packages
sudo apt install package-name      # Install a package
sudo apt remove package-name       # Remove a package
sudo apt purge package-name        # Remove package and config files
sudo apt autoremove                # Remove unused dependencies
sudo apt search keyword            # Search for packages
sudo apt show package-name         # Show package details
sudo apt list --installed          # List installed packages
```

### macOS (`brew`)

```bash
brew update                        # Update brew itself
brew upgrade                       # Upgrade all packages
brew install package-name          # Install a package
brew uninstall package-name        # Remove a package
brew search keyword                # Search for packages
brew list                          # List installed packages
brew info package-name             # Show package info
```

### CentOS/RHEL/Fedora (`dnf`/`yum`)

```bash
sudo dnf update                    # Update packages
sudo dnf install package-name      # Install
sudo dnf remove package-name       # Remove
sudo dnf search keyword            # Search
```

---

## Useful One-Liners

```bash
# Create multiple files at once
touch file{1..10}.txt

# Create a directory tree
mkdir -p project/{src,docs,tests}/{2024,2025}

# Find and replace in all files
find . -name "*.txt" -exec sed -i 's/old/new/g' {} +

# Monitor a log file in real-time
tail -f /var/log/syslog

# Generate a random password
openssl rand -base64 16

# Find your public IP
curl ifconfig.me

# Quick HTTP server in current directory
python3 -m http.server 8000

# Convert line endings (DOS to Unix)
sed -i 's/\r$//' file.txt

# Extract a column from CSV
cut -d',' -f3 data.csv

# Count unique lines
sort file.txt | uniq -c | sort -nr

# Find largest files
du -ah . | sort -rh | head -n 10

# Backup with timestamp
tar -czf backup_$(date +%Y%m%d).tar.gz folder/

# Run command every 5 seconds
while true; do clear; date; df -h; sleep 5; done
```

---

## Terminal Multiplexers: `tmux` and `screen`

### `tmux` Basics

```bash
tmux new -s mysession            # Create new session
tmux ls                          # List sessions
tmux attach -t mysession         # Attach to session
tmux detach                      # Detach (keep running)
tmux kill-session -t mysession   # Kill session
```

**Inside tmux:**

| Shortcut | Action |
|----------|--------|
| `Ctrl + B, C` | Create new window |
| `Ctrl + B, N` | Next window |
| `Ctrl + B, P` | Previous window |
| `Ctrl + B, D` | Detach |
| `Ctrl + B, %` | Split vertically |
| `Ctrl + B, "` | Split horizontally |
| `Ctrl + B, Arrow` | Move between panes |
| `Ctrl + B, ?` | Show all shortcuts |

---

## Dotfiles

**Dotfiles** are configuration files that start with a dot (`.`). They're hidden by default.

### Common Dotfiles

| File | Purpose |
|------|---------|
| `~/.bashrc` | Bash configuration (runs for interactive shells) |
| `~/.bash_profile` | Bash login configuration |
| `~/.profile` | Generic shell configuration |
| `~/.bash_logout` | Runs when you exit bash |
| `~/.vimrc` | Vim configuration |
| `~/.nanorc` | Nano configuration |
| `~/.ssh/config` | SSH configuration |
| `~/.gitconfig` | Git configuration |

### Managing Dotfiles

Many people keep their dotfiles in a Git repository:

```bash
# Create a dotfiles repo
mkdir ~/dotfiles
cd ~/dotfiles
git init

# Copy important dotfiles
cp ~/.bashrc .
cp ~/.vimrc .

# Create symlinks
ln -s ~/dotfiles/.bashrc ~/.bashrc
ln -s ~/dotfiles/.vimrc ~/.vimrc

# Commit and push
git add .
git commit -m "Initial dotfiles"
```

---

## Practice Exercises 🎯

### Exercise 1: Customize Your Environment
1. Add these aliases to your `~/.bashrc`:
   - `ll='ls -la'`
   - `..='cd ..'`
   - `update='sudo apt update'`
2. Add `~/bin` to your PATH
3. Create a custom colored prompt
4. Reload your configuration

### Exercise 2: History Mastery
1. Run 5 different commands
2. Use `!!` to repeat the last one
3. Use `!-3` to run the 3rd-to-last command
4. Use `Ctrl + R` to search for a previous command
5. Use `!$` to use the last argument of the previous command

### Exercise 3: Package Management
1. Update your package lists
2. Search for a package (e.g., `htop`, `tree`, `neofetch`)
3. Install it
4. Verify it's installed
5. Check its details with `apt show` or `brew info`

### Exercise 4: tmux Session
1. Start a tmux session
2. Create 2 windows
3. Split one window into panes
4. Detach and reattach
5. Kill the session

---

## Key Takeaways

- ✅ Environment variables control shell behavior; `export` makes them available to child processes
- ✅ `PATH` determines where the shell looks for executables
- ✅ Aliases create command shortcuts; add them to `~/.bashrc`
- ✅ `PS1` controls your prompt appearance
- ✅ History shortcuts (`!!`, `!$`, `Ctrl+R`) save massive amounts of time
- ✅ Tab completion is your best friend — use it constantly!
- ✅ Package managers (`apt`, `brew`, `dnf`) install and manage software
- ✅ `tmux` and `screen` keep sessions alive after disconnecting
- ✅ Dotfiles store your personal configuration

---

## Next Up

In **Module 12**, we'll put everything together with **real-world projects** — practical scripts and workflows that use everything you've learned!

> 📝 **Homework**: 
> 1. Customize your `~/.bashrc` with aliases and a colored prompt
> 2. Create a `~/bin` directory and add it to PATH
> 3. Install 3 new packages you find interesting
> 4. Try `tmux` and create a session with multiple windows
