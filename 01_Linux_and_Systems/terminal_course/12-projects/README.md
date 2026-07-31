# Module 12: Real-World Projects

## Introduction

You've learned all the tools — now let's put them to work! 🛠️

In this module, we'll build practical projects that combine everything from the previous modules. These are the kinds of scripts and workflows you'll use in real life.

---

## Project 1: System Information Dashboard

Create a script that displays a beautiful system overview.

### `sysinfo.sh`

```bash
#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  ${YELLOW}SYSTEM INFORMATION DASHBOARD${NC}          ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo

echo -e "${GREEN}┌─ User & Host ──────────────────────────┐${NC}"
echo -e "  User:     $(whoami)"
echo -e "  Host:     $(hostname)"
echo -e "  Uptime:   $(uptime -p 2>/dev/null || uptime | awk -F',' '{print $1}' | sed 's/^ *//')"
echo

echo -e "${GREEN}┌─ Operating System ───────────────────────┐${NC}"
if [ -f /etc/os-release ]; then
    source /etc/os-release
    echo -e "  OS:       $PRETTY_NAME"
else
    echo -e "  OS:       $(uname -s)"
fi
echo -e "  Kernel:   $(uname -r)"
echo -e "  Arch:     $(uname -m)"
echo

echo -e "${GREEN}┌─ Hardware ───────────────────────────────┐${NC}"
echo -e "  CPU:      $(grep 'model name' /proc/cpuinfo 2>/dev/null | head -1 | cut -d':' -f2 | sed 's/^ *//' || echo 'N/A')"
echo -e "  Cores:    $(nproc 2>/dev/null || echo 'N/A')"
if command -v free &> /dev/null; then
    echo -e "  Memory:   $(free -h | awk '/^Mem:/ {print $3 " / " $2}')"
fi
echo

echo -e "${GREEN}┌─ Disk Usage ─────────────────────────────┐${NC}"
df -h | grep -E '^/dev/' | while read line; do
    echo -e "  $line"
done
echo

echo -e "${GREEN}┌─ Network ────────────────────────────────┐${NC}"
echo -e "  IP:       $(hostname -I 2>/dev/null | awk '{print $1}' || echo 'N/A')"
echo -e "  Gateway:  $(ip route 2>/dev/null | grep default | awk '{print $3}' || echo 'N/A')"
echo

echo -e "${GREEN}┌─ Top Processes ──────────────────────────┐${NC}"
ps aux --sort=-%cpu | head -n 6 | tail -n 5 | awk '{printf "  %-8s %6s %5s %s\n", $1, $2, $3, $11}'
echo

echo -e "${BLUE}══════════════════════════════════════════${NC}"
```

**Usage:**
```bash
chmod +x sysinfo.sh
./sysinfo.sh
```

---

## Project 2: Automated Backup Script

A robust backup script with error handling and logging.

### `backup.sh`

```bash
#!/bin/bash
set -euo pipefail

# Configuration
BACKUP_DIR="$HOME/backups"
SOURCE_DIR="${1:-$HOME/Documents}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_$(basename "$SOURCE_DIR")_${DATE}.tar.gz"
LOG_FILE="$BACKUP_DIR/backup.log"
RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging function
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Cleanup function
cleanup() {
    if [ -n "${TEMP_DIR:-}" ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi
}
trap cleanup EXIT

# Main script
main() {
    echo -e "${GREEN}=== Backup Script ===${NC}"

    # Check if source exists
    if [ ! -d "$SOURCE_DIR" ]; then
        log "ERROR" "Source directory does not exist: $SOURCE_DIR"
        echo -e "${RED}Error: Source directory does not exist${NC}"
        exit 1
    fi

    # Create backup directory
    mkdir -p "$BACKUP_DIR"

    # Calculate size before backup
    local size=$(du -sh "$SOURCE_DIR" | cut -f1)
    log "INFO" "Starting backup of $SOURCE_DIR (Size: $size)"

    # Create backup
    local backup_path="$BACKUP_DIR/$BACKUP_FILE"
    log "INFO" "Creating archive: $BACKUP_FILE"

    if tar -czf "$backup_path" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")"; then
        local backup_size=$(du -sh "$backup_path" | cut -f1)
        log "SUCCESS" "Backup completed: $BACKUP_FILE (Size: $backup_size)"
        echo -e "${GREEN}✓ Backup successful!${NC}"
        echo -e "  File: $backup_path"
        echo -e "  Size: $backup_size"
    else
        log "ERROR" "Backup failed"
        echo -e "${RED}✗ Backup failed!${NC}"
        exit 1
    fi

    # Clean old backups
    log "INFO" "Cleaning backups older than $RETENTION_DAYS days"
    local deleted=$(find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
    log "INFO" "Deleted $deleted old backup(s)"

    # Show backup summary
    echo
    echo -e "${YELLOW}Backup Summary:${NC}"
    echo "  Total backups: $(ls -1 $BACKUP_DIR/backup_*.tar.gz 2>/dev/null | wc -l)"
    echo "  Latest backup: $BACKUP_FILE"
    echo "  Backup location: $BACKUP_DIR"

    log "INFO" "Backup process completed"
}

main "$@"
```

**Usage:**
```bash
chmod +x backup.sh
./backup.sh                    # Backup ~/Documents
./backup.sh ~/Pictures         # Backup ~/Pictures
./backup.sh /path/to/folder    # Backup any folder
```

---

## Project 3: File Organizer

Automatically organize files in a directory by type.

### `organize.sh`

```bash
#!/bin/bash

# File organizer - sorts files into folders by extension

TARGET_DIR="${1:-.}"
DRY_RUN=false

# Check for dry run flag
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    TARGET_DIR="${2:-.}"
fi

# Define file type mappings
declare -A EXTENSIONS=(
    ["Images"]="jpg jpeg png gif bmp svg webp ico"
    ["Documents"]="pdf doc docx txt rtf odt md tex"
    ["Spreadsheets"]="xls xlsx csv ods"
    ["Presentations"]="ppt pptx odp"
    ["Archives"]="zip tar gz bz2 rar 7z xz"
    ["Audio"]="mp3 wav flac aac ogg wma m4a"
    ["Video"]="mp4 avi mkv mov wmv flv webm m4v"
    ["Code"]="py js html css java cpp c h php rb go rs sh"
    ["Data"]="json xml yaml yml sql db sqlite"
    ["Executables"]="exe dmg pkg deb rpm appimage"
)

# Function to get category for extension
get_category() {
    local ext="${1,,}"  # lowercase
    for category in "${!EXTENSIONS[@]}"; do
        if [[ " ${EXTENSIONS[$category]} " =~ " $ext " ]]; then
            echo "$category"
            return
        fi
    done
    echo "Other"
}

# Main function
main() {
    echo "=== File Organizer ==="
    echo "Target directory: $(realpath "$TARGET_DIR")"
    echo "Mode: $([ "$DRY_RUN" = true ] && echo "DRY RUN (no changes)" || echo "LIVE")"
    echo

    # Statistics
    declare -A stats
    local total=0
    local moved=0

    # Process files
    for file in "$TARGET_DIR"/*; do
        # Skip if not a regular file
        [ -f "$file" ] || continue

        # Skip hidden files
        local basename=$(basename "$file")
        [[ "$basename" == .* ]] && continue

        # Skip the script itself
        [[ "$basename" == "organize.sh" ]] && continue

        # Get extension
        local ext="${basename##*.}"
        [ "$ext" = "$basename" ] && ext="no_extension"

        local category=$(get_category "$ext")
        local dest_dir="$TARGET_DIR/$category"

        total=$((total + 1))
        stats[$category]=$((stats[$category] + 1))

        if [ "$DRY_RUN" = true ]; then
            echo "[DRY RUN] Would move: $basename → $category/"
        else
            mkdir -p "$dest_dir"
            if mv "$file" "$dest_dir/"; then
                echo "✓ Moved: $basename → $category/"
                moved=$((moved + 1))
            else
                echo "✗ Failed: $basename"
            fi
        fi
    done

    # Summary
    echo
    echo "=== Summary ==="
    echo "Total files found: $total"
    [ "$DRY_RUN" = false ] && echo "Files moved: $moved"
    echo
    echo "Files by category:"
    for category in "${!stats[@]}"; do
        echo "  $category: ${stats[$category]}"
    done
}

main "$@"
```

**Usage:**
```bash
chmod +x organize.sh
./organize.sh --dry-run ~/Downloads    # Preview what would happen
./organize.sh ~/Downloads              # Actually organize
```

---

## Project 4: Git Repository Helper

A helper script for common Git operations.

### `git-helper.sh`

```bash
#!/bin/bash

# Git helper script for common operations

show_menu() {
    echo "=== Git Helper ==="
    echo
    echo "Current repository: $(git remote get-url origin 2>/dev/null || echo 'No remote')"
    echo "Current branch: $(git branch --show-current 2>/dev/null || echo 'Not a git repo')"
    echo
    echo "1) Status"
    echo "2) Add all and commit"
    echo "3) Push to origin"
    echo "4) Pull from origin"
    echo "5) Create and switch to new branch"
    echo "6) View log (pretty)"
    echo "7) View diff"
    echo "8) Clean untracked files"
    echo "9) Stash changes"
    echo "10) Pop stash"
    echo "0) Exit"
    echo
}

git_status() {
    echo "=== Git Status ==="
    git status
}

git_commit() {
    read -p "Enter commit message: " msg
    if [ -z "$msg" ]; then
        echo "Error: Commit message cannot be empty"
        return
    fi
    git add -A
    git commit -m "$msg"
    echo "✓ Committed: $msg"
}

git_push() {
    local branch=$(git branch --show-current)
    echo "Pushing to origin/$branch..."
    git push origin "$branch"
}

git_pull() {
    echo "Pulling from origin..."
    git pull
}

git_new_branch() {
    read -p "Enter new branch name: " branch
    if [ -z "$branch" ]; then
        echo "Error: Branch name cannot be empty"
        return
    fi
    git checkout -b "$branch"
    echo "✓ Created and switched to branch: $branch"
}

git_log() {
    echo "=== Git Log ==="
    git log --oneline --graph --decorate --all -20
}

git_diff() {
    echo "=== Git Diff ==="
    git diff --stat
    echo
    read -p "Show full diff? (y/n): " answer
    if [ "$answer" = "y" ]; then
        git diff
    fi
}

git_clean() {
    echo "This will delete untracked files!"
    read -p "Are you sure? (y/n): " answer
    if [ "$answer" = "y" ]; then
        git clean -fd
        echo "✓ Cleaned untracked files"
    fi
}

git_stash() {
    read -p "Enter stash message (optional): " msg
    if [ -n "$msg" ]; then
        git stash push -m "$msg"
    else
        git stash push
    fi
    echo "✓ Changes stashed"
}

git_stash_pop() {
    echo "=== Stash List ==="
    git stash list
    echo
    read -p "Pop latest stash? (y/n): " answer
    if [ "$answer" = "y" ]; then
        git stash pop
        echo "✓ Stash popped"
    fi
}

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not a git repository"
    exit 1
fi

# Main loop
while true; do
    show_menu
    read -p "Select option: " choice

    case $choice in
        1) git_status ;;
        2) git_commit ;;
        3) git_push ;;
        4) git_pull ;;
        5) git_new_branch ;;
        6) git_log ;;
        7) git_diff ;;
        8) git_clean ;;
        9) git_stash ;;
        10) git_stash_pop ;;
        0) echo "Goodbye!"; exit 0 ;;
        *) echo "Invalid option" ;;
    esac

    echo
    read -p "Press Enter to continue..."
    clear
done
```

**Usage:**
```bash
chmod +x git-helper.sh
cd /path/to/your/git/repo
../git-helper.sh
```

---

## Project 5: Development Environment Setup

A script to set up a new development machine.

### `dev-setup.sh`

```bash
#!/bin/bash
set -e

# Development Environment Setup Script
# Run this on a fresh machine to install common tools

echo "=== Development Environment Setup ==="
echo

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "Unsupported OS"
    exit 1
fi

echo "Detected OS: $OS"
echo

# Install function
install_package() {
    local pkg="$1"
    echo "Installing $pkg..."
    case $OS in
        ubuntu|debian)
            sudo apt install -y "$pkg"
            ;;
        fedora)
            sudo dnf install -y "$pkg"
            ;;
        arch)
            sudo pacman -S --noconfirm "$pkg"
            ;;
        macos)
            brew install "$pkg"
            ;;
    esac
}

# Update package lists
echo "Updating package lists..."
case $OS in
    ubuntu|debian)
        sudo apt update
        ;;
    fedora)
        sudo dnf update -y
        ;;
    arch)
        sudo pacman -Sy
        ;;
    macos)
        if ! command -v brew &> /dev/null; then
            echo "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew update
        ;;
esac

# Install essential tools
echo
echo "Installing essential tools..."
ESSENTIALS=(git curl wget vim nano tree htop jq)
for pkg in "${ESSENTIALS[@]}"; do
    if ! command -v "$pkg" &> /dev/null; then
        install_package "$pkg"
    else
        echo "$pkg already installed ✓"
    fi
done

# Install development tools
echo
echo "Installing development tools..."
DEV_TOOLS=(python3 python3-pip nodejs npm)
for pkg in "${DEV_TOOLS[@]}"; do
    if ! command -v "$pkg" &> /dev/null 2>&1; then
        install_package "$pkg" || echo "Warning: Could not install $pkg"
    else
        echo "$pkg already installed ✓"
    fi
done

# Configure Git
echo
read -p "Configure Git? (y/n): " configure_git
if [ "$configure_git" = "y" ]; then
    read -p "Git name: " git_name
    read -p "Git email: " git_email
    git config --global user.name "$git_name"
    git config --global user.email "$git_email"
    git config --global init.defaultBranch main
    git config --global core.editor nano
    echo "Git configured ✓"
fi

# Create common directories
echo
echo "Creating common directories..."
mkdir -p ~/projects
mkdir -p ~/scripts
mkdir -p ~/.config

# Add scripts to PATH
echo
echo "Adding ~/scripts to PATH..."
if ! grep -q 'export PATH="$PATH:$HOME/scripts"' ~/.bashrc; then
    echo 'export PATH="$PATH:$HOME/scripts"' >> ~/.bashrc
    echo "Added to ~/.bashrc ✓"
fi

# Create some useful aliases
echo
echo "Adding useful aliases..."
ALIASES=$(cat << 'EOF'

# Custom aliases
alias ll='ls -la'
alias ..='cd ..'
alias ...='cd ../..'
alias mkdirp='mkdir -p'
alias update='sudo apt update && sudo apt upgrade'
alias gs='git status'
alias gp='git pull'
alias gl='git log --oneline -10'
alias projects='cd ~/projects'
alias scripts='cd ~/scripts'
EOF
)

if ! grep -q "Custom aliases" ~/.bashrc; then
    echo "$ALIASES" >> ~/.bashrc
    echo "Aliases added ✓"
fi

echo
echo "=== Setup Complete! ==="
echo
echo "Next steps:"
echo "1. Restart your terminal or run: source ~/.bashrc"
echo "2. Create your first project in ~/projects/"
echo "3. Add your scripts to ~/scripts/"
echo
echo "Happy coding! 🚀"
```

**Usage:**
```bash
chmod +x dev-setup.sh
./dev-setup.sh
```

---

## Project 6: Log Analyzer

Analyze web server logs to find useful information.

### `log-analyzer.sh`

```bash
#!/bin/bash

LOG_FILE="${1:-access.log}"

if [ ! -f "$LOG_FILE" ]; then
    echo "Error: File not found: $LOG_FILE"
    echo "Usage: $0 [logfile]"
    exit 1
fi

echo "=== Log Analysis: $LOG_FILE ==="
echo

# Total requests
echo "Total requests: $(wc -l < "$LOG_FILE")"
echo

# Top 10 IP addresses
echo "Top 10 IP addresses:"
awk '{print $1}' "$LOG_FILE" | sort | uniq -c | sort -rn | head -n 10 | awk '{printf "  %6s %s\n", $1, $2}'
echo

# Top 10 requested URLs
echo "Top 10 requested URLs:"
awk '{print $7}' "$LOG_FILE" | sort | uniq -c | sort -rn | head -n 10 | awk '{printf "  %6s %s\n", $1, $2}'
echo

# HTTP status codes
echo "HTTP status codes:"
awk '{print $9}' "$LOG_FILE" | sort | uniq -c | sort -rn | awk '{printf "  %6s %s\n", $1, $2}'
echo

# 404 errors (Not Found)
echo "404 Errors (Top 10):"
awk '$9 == 404 {print $7}' "$LOG_FILE" | sort | uniq -c | sort -rn | head -n 10 | awk '{printf "  %6s %s\n", $1, $2}'
echo

# Requests by hour
echo "Requests by hour:"
awk -F':' '{print $2}' "$LOG_FILE" | sort | uniq -c | sort -n | awk '{printf "  %2s:00 - %6s requests\n", $2, $1}'
```

**Usage:**
```bash
chmod +x log-analyzer.sh
./log-analyzer.sh /var/log/nginx/access.log
./log-analyzer.sh ~/my-logs/apache.log
```

---

## Project 7: Password Generator

Generate secure random passwords.

### `password-gen.sh`

```bash
#!/bin/bash

# Default settings
LENGTH=16
COUNT=5
USE_SPECIAL=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--length)
            LENGTH="$2"
            shift 2
            ;;
        -c|--count)
            COUNT="$2"
            shift 2
            ;;
        --no-special)
            USE_SPECIAL=false
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -l, --length N     Password length (default: 16)"
            echo "  -c, --count N      Number of passwords (default: 5)"
            echo "  --no-special       Exclude special characters"
            echo "  -h, --help         Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Character sets
LOWER='abcdefghijklmnopqrstuvwxyz'
UPPER='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUMBERS='0123456789'
SPECIAL='!@#$%^&*()_+-=[]{}|;:,.<>?'

if [ "$USE_SPECIAL" = true ]; then
    ALL="$LOWER$UPPER$NUMBERS$SPECIAL"
else
    ALL="$LOWER$UPPER$NUMBERS"
fi

echo "=== Password Generator ==="
echo "Length: $LENGTH"
echo "Count: $COUNT"
echo "Special characters: $USE_SPECIAL"
echo

for i in $(seq 1 $COUNT); do
    # Generate password using openssl
    PASSWORD=$(openssl rand -base64 48 | tr -dc "$ALL" | head -c "$LENGTH")

    # Ensure at least one of each type
    if [ "$USE_SPECIAL" = true ]; then
        L=$(echo "$LOWER" | fold -w1 | shuf | head -1)
        U=$(echo "$UPPER" | fold -w1 | shuf | head -1)
        N=$(echo "$NUMBERS" | fold -w1 | shuf | head -1)
        S=$(echo "$SPECIAL" | fold -w1 | shuf | head -1)
        REST=$(openssl rand -base64 48 | tr -dc "$ALL" | head -c $((LENGTH - 4)))
        PASSWORD="$L$U$N$S$REST"
        PASSWORD=$(echo "$PASSWORD" | fold -w1 | shuf | tr -d '\n')
    fi

    echo "  $i) $PASSWORD"
done

echo
echo "Tip: Use a password manager to store these securely!"
```

**Usage:**
```bash
chmod +x password-gen.sh
./password-gen.sh
./password-gen.sh -l 20 -c 3
./password-gen.sh --no-special -l 12
```

---

## Practice: Build Your Own Script

Now it's your turn! Create a script that does something useful for YOU. Here are some ideas:

1. **Movie/Show Renamer**: Rename downloaded files to a consistent format
2. **Photo Organizer**: Sort photos by date taken (using EXIF data)
3. **Music Playlist Generator**: Create playlists from a music directory
4. **Note Taker**: Quick command-line note-taking with timestamps
5. **Weather Checker**: Fetch and display weather from an API
6. **Todo List Manager**: Simple CLI todo list with add/remove/list
7. **Website Monitor**: Check if a website is up and alert if down
8. **Directory Size Reporter**: Show which folders are taking up space

### Template to Get Started

```bash
#!/bin/bash
set -euo pipefail

# Your script here
# Start simple, then add features!

echo "Hello, this is my custom script!"
```

---

## Key Takeaways

- ✅ Real scripts combine multiple tools and techniques
- ✅ Always use `set -euo pipefail` for safer scripts
- ✅ Use functions to organize code
- ✅ Add logging for easier debugging
- ✅ Use `trap` for cleanup
- ✅ Parse command-line arguments for flexibility
- ✅ Test with `--dry-run` before making destructive changes
- ✅ Make scripts executable and add them to your PATH

---

## Congratulations! 🎓

You've completed the entire terminal course! You now know:
- ✅ How to navigate the file system
- ✅ How to manage files and directories
- ✅ How to edit text in the terminal
- ✅ How permissions work
- ✅ How to manage processes
- ✅ How to use pipes and redirection
- ✅ How to search and find files
- ✅ How to work with networks
- ✅ How to write shell scripts
- ✅ How to customize your environment
- ✅ How to build real-world tools

**Keep practicing!** The terminal is a skill that improves with use. Try to use the terminal for everyday tasks instead of the GUI. Before you know it, you'll be faster with the terminal than with a mouse!

> 📝 **Final Homework**: 
> 1. Build one of the projects above and customize it
> 2. Create your own utility script for something you do regularly
> 3. Share your scripts with friends or on GitHub
> 4. Keep exploring — the terminal has infinite depth!

**Happy terminal-ing! 🐧**
