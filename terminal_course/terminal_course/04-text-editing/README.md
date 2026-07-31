# Module 4: Text Editors in the Terminal

## Introduction

So far, you've created files with `touch` and `echo`, but what if you want to write a real document, edit code, or modify configuration files? You need a **text editor** that works in the terminal!

In this module, we'll cover:
- `nano` — The beginner-friendly editor
- `vim` — The powerful (but tricky) editor
- Basic editing concepts

> 🎯 **Goal**: By the end of this module, you'll be comfortable editing files directly in the terminal.

---

## Why Terminal Text Editors?

You might wonder: "Why not just use VS Code or Notepad?"

Great question! Here's why terminal editors matter:

1. **Remote servers** don't have GUIs — you MUST use terminal editors
2. **Quick edits** are faster in the terminal than opening a GUI editor
3. **Configuration files** are often edited in the terminal
4. **Scripts and code** can be edited right where you run them
5. **It's cool** — and impresses other developers! 😄

---

## Nano — The Friendly Editor

`nano` is the perfect editor for beginners. It shows you all the shortcuts at the bottom of the screen!

### Opening Nano

```bash
nano myfile.txt
```

If the file doesn't exist, nano creates it when you save.

### Nano Interface

```
  GNU nano 6.2                    myfile.txt                              
Hello, this is my file.
I'm typing in nano!












^G Help      ^O Write Out ^W Where Is  ^K Cut       ^T Execute   ^C Location
^X Exit      ^R Read File ^\ Replace   ^U Paste     ^J Justify   ^/ Go To Line
```

The `^` symbol means **Ctrl**. So `^X` means `Ctrl + X`.

### Basic Nano Commands

| Shortcut | Action |
|----------|--------|
| `Ctrl + O` | Save file ("Write Out") |
| `Ctrl + X` | Exit nano |
| `Ctrl + K` | Cut current line |
| `Ctrl + U` | Paste ("Uncut") |
| `Ctrl + W` | Search ("Where Is") |
| `Ctrl + G` | Help |
| `Ctrl + C` | Show cursor position |
| `Ctrl + V` | Next page |
| `Ctrl + Y` | Previous page |
| `Alt + U` | Undo |
| `Alt + E` | Redo |

### Your First Nano Session

1. Open nano: `nano practice.txt`
2. Type some text
3. Save: Press `Ctrl + O`, then Enter to confirm the filename
4. Exit: Press `Ctrl + X`

### Nano Tips

- Use arrow keys to move around
- `Home` / `End` go to start/end of line
- `Page Up` / `Page Down` scroll
- `Alt + /` or `Ctrl + W` then `Ctrl + T` to go to a specific line

---

## Vim — The Power Editor

`vim` (Vi IMproved) is incredibly powerful but has a steep learning curve. Many developers use it exclusively. Don't worry if it feels weird at first — everyone struggles with vim at the beginning!

### The Vim Philosophy

Vim has **modes**:
- **Normal mode** — for navigating and commands (default when you open vim)
- **Insert mode** — for typing text
- **Visual mode** — for selecting text
- **Command mode** — for running commands (type `:`)

This is different from most editors where you just start typing. In vim, you must **enter insert mode** first!

### Opening Vim

```bash
vim myfile.txt
```

### Vim Survival Guide

#### Getting In and Out

| Command | Action |
|---------|--------|
| `vim file.txt` | Open vim |
| `i` | Enter insert mode (start typing) |
| `Esc` | Return to normal mode |
| `:w` | Save (write) |
| `:q` | Quit |
| `:wq` or `ZZ` | Save and quit |
| `:q!` | Quit without saving (force) |
| `:wqa` | Save all files and quit |

> 😅 **The Classic Vim Joke**: "How do you exit vim?" Now you know: press `Esc`, then type `:q!` and press Enter!

#### Moving Around (Normal Mode)

| Key | Action |
|-----|--------|
| `h` | Left |
| `j` | Down |
| `k` | Up |
| `l` | Right |
| `w` | Next word |
| `b` | Previous word |
| `0` | Start of line |
| `$` | End of line |
| `gg` | Top of file |
| `G` | Bottom of file |
| `:5` | Go to line 5 |
| `Ctrl + D` | Half page down |
| `Ctrl + U` | Half page up |

> 💡 **Why h/j/k/l instead of arrows?** Vim was designed for keyboards where arrow keys weren't easily accessible. Many vim users still prefer them because you don't have to move your hands from the home row!

#### Editing (Normal Mode)

| Command | Action |
|---------|--------|
| `i` | Insert before cursor |
| `a` | Append after cursor |
| `o` | Open new line below |
| `O` | Open new line above |
| `x` | Delete character under cursor |
| `dd` | Delete (cut) entire line |
| `yy` | Yank (copy) entire line |
| `p` | Paste after cursor |
| `P` | Paste before cursor |
| `u` | Undo |
| `Ctrl + r` | Redo |
| `r` | Replace single character |
| `cw` | Change word |
| `cc` | Change entire line |

#### Searching

| Command | Action |
|---------|--------|
| `/word` | Search forward for "word" |
| `?word` | Search backward for "word" |
| `n` | Next search result |
| `N` | Previous search result |

#### Visual Mode (Selecting Text)

| Command | Action |
|---------|--------|
| `v` | Enter visual mode (character) |
| `V` | Enter visual line mode |
| `Ctrl + v` | Enter visual block mode |
| `y` | Yank (copy) selection |
| `d` | Delete selection |
| `>` | Indent selection |
| `<` | Unindent selection |

### Your First Vim Session

1. Open vim: `vim practice.txt`
2. Press `i` to enter insert mode
3. Type: "Hello from vim!"
4. Press `Esc` to return to normal mode
5. Type `:wq` and press Enter to save and quit

### Vim Practice Routine

Spend 10 minutes doing this:

1. Open a file with vim
2. Enter insert mode with `i`
3. Type a paragraph
4. Press `Esc`
5. Navigate with `h`, `j`, `k`, `l`
6. Delete a line with `dd`
7. Undo with `u`
8. Save and quit with `:wq`

---

## Which Editor Should You Use?

| Editor | Best For | Difficulty |
|--------|----------|------------|
| **nano** | Quick edits, beginners, learning | ⭐ Easy |
| **vim** | Power users, remote work, coding | ⭐⭐⭐⭐ Hard |
| **micro** | Modern alternative to nano | ⭐⭐ Medium |

> 🎯 **My Recommendation**: Start with **nano** for everyday use. Learn **vim basics** gradually. Many tutorials and server work require vim knowledge.

---

## Other Terminal Editors

### Micro
A modern, easy-to-use terminal editor with mouse support:
```bash
# Install micro
# Then: micro myfile.txt
```

### Emacs
Another powerful editor (some people prefer it over vim):
```bash
emacs myfile.txt
```

---

## Practice Exercises 🎯

### Exercise 1: Nano Mastery
1. Open nano: `nano my-story.txt`
2. Write a 5-line story about learning the terminal
3. Save with `Ctrl + O`, confirm with Enter
4. Exit with `Ctrl + X`
5. View the file with `cat`
6. Reopen in nano and add 2 more lines
7. Use `Ctrl + W` to search for a word
8. Save and exit

### Exercise 2: Vim Basics
1. Open vim: `vim vim-practice.txt`
2. Press `i` and type: "I am learning vim!"
3. Press `Esc`, then type `:w` and Enter (save)
4. Press `i` again, add another line
5. Press `Esc`, navigate with `h`, `j`, `k`, `l`
6. Delete a line with `dd`
7. Undo with `u`
8. Save and quit with `:wq`

### Exercise 3: Configuration File Edit
1. Look at your `.bashrc` file: `cat ~/.bashrc`
2. Make a backup: `cp ~/.bashrc ~/.bashrc.backup`
3. Open it in nano: `nano ~/.bashrc`
4. Scroll to the bottom
5. Add this line: `# I edited this file on $(date)`
6. Save and exit
7. View the change: `tail ~/.bashrc`
8. Restore the backup: `cp ~/.bashrc.backup ~/.bashrc`

---

## Key Takeaways

- ✅ `nano` is beginner-friendly with on-screen shortcuts
- ✅ `vim` is powerful but has modes: Normal, Insert, Visual, Command
- ✅ In vim, press `i` to insert, `Esc` to return to normal, `:wq` to save and quit
- ✅ `nano`: `Ctrl + O` to save, `Ctrl + X` to exit
- ✅ Always make backups before editing important files!

---

## Next Up

In **Module 5**, we'll dive into **file permissions** — understanding who can read, write, and execute files. This is crucial for security and understanding how Linux works!

> 📝 **Homework**: 
> 1. Edit your `hello.txt` from Module 3 using both nano and vim
> 2. Try to write a short note in vim without looking at the cheat sheet
> 3. Explore your `.bashrc` file in nano and read the comments
