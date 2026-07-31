Ok this window and session is for learning of linux ok. I have downloaded wsl for learning linux on my windows laptop. Ans you will be teaching me linux. I want to be a software developer ans I haven't joined college yet. I have completed cs50p. Ok you are my professor. Ans you will teach me why and what ok got me ?

Got you! Welcome to Linux class. 🎓

I'm your professor for this session. Since you've done CS50P, you already know how to think like a programmer — that's a great foundation. Linux is going to feel very natural to you.

**Here's the plan for how this works:**

- I teach you concepts with the _why_, not just the _what_
- You try commands in your WSL terminal and report back
- We go at your pace — no rush

---

**Before we start Lesson 1, open your WSL terminal and run this:**

bash

```bash
whoami
```

Tell me what it prints. This is your first Linux command — it answers the question _"who am I logged in as?"_

Once you confirm it's working, we'll begin **Lesson 1: The Linux Filesystem — why it's structured the way it is and how to navigate it.**

Ready? Go run that command! 🚀

owais is output

Perfect! `owais` is your username on the Linux system. That command just asked the OS _"who's running this session?"_ and it told you — simple but useful.

---

**Your WSL is working. Let's begin.**

---

## 📚 Lesson 1: The Linux Filesystem

### Why does this matter?

In Windows, files live under `C:\Users\YourName\`. In Linux, **everything is a file** — your documents, your USB drive, even your keyboard. They all live in one big tree starting from `/` (called the **root**).

Understanding this tree = understanding Linux.

---

### The Tree Structure

```
/
├── home/       → your personal files (like C:\Users\)
├── etc/        → system configuration files
├── bin/        → essential programs/commands
├── var/        → logs, temporary data
├── tmp/        → temporary files (wiped on reboot)
└── root/       → home folder for the admin user
```

---

### Your First 3 Navigation Commands

|Command|What it does|
|---|---|
|`pwd`|Print Working Directory — _where am I right now?_|
|`ls`|List files in current directory|
|`cd`|Change Directory — _move somewhere_|

---

### 🧪 Your Task

Run these **one by one** and tell me the output:

bash

```bash
pwd
```

bash

```bash
ls
```

bash

```bash
cd /
```

bash

```bash
ls
```

The last `ls` will show you the **root of the entire Linux system.**

Go run them! 👨‍💻

I run. pwd shows /home/owais , ls shows practice, cd / then goes to owais@hp:/$ ans then inside this when run ls it show bin dev home , lib sys usr boot .... And blnow current on owais@HP:/$

Excellent! You're reading the terminal like a pro already. Let me break down what just happened:

---

### What you just learned

**`pwd` → `/home/owais`**  
This is YOUR home folder. Every user gets their own space under `/home/`. Think of it like `C:\Users\owais\` on Windows.

**`ls` inside home → `practice`**  
You already have a folder called `practice` sitting there. We'll use it later.

**`cd /` → moved to root**  
You just teleported to the very top of the entire Linux system.

**`ls` at `/` → showed `bin dev home lib sys usr boot...`**  
Those are the organs of Linux. You're looking at the whole operating system laid out as folders.

---

### Quick explanation of what you saw

| Folder | Purpose                                             |
| ------ | --------------------------------------------------- |
| `home` | All users' personal files                           |
| `bin`  | Core commands like `ls`, `pwd` themselves live here |
| `boot` | Files needed to start Linux                         |
| `dev`  | Your hardware (keyboard, disk) as files             |
| `sys`  | Live info about the running system                  |
|        |                                                     |

---

### 🧪 Now do this

Go back home in **one command:**

bash

```bash
cd ~
```

The `~` symbol is a shortcut that **always means your home directory.** Run `pwd` after to confirm you're at `/home/owais`.

Report back! 🚀

Yes back to home owais

Perfect! `~` is one of those shortcuts you'll use **every single day** as a developer. Burn it into your muscle memory.

---

### Quick Recap So Far

```
/          ← root of everything
└── home/
    └── owais/    ← you are here (~)
        └── practice/
```

You already know how to **go up, go down, and teleport home.** That's real navigation.

---

### 🧪 Now let's learn one more move

There's a special shortcut `..` which means **"go up one level"**

Try this:

bash

```bash
cd ..
```

Then run:

bash

```bash
pwd
```

You should land at `/home` — one level above your personal folder.

Then try going up **one more time:**

bash

```bash
cd ..
pwd
```

You should now be at `/` — the root again.

---

### The concept here

Think of it like this:

```
/              ← cd .. from /home takes you here
└── home/      ← cd .. from /home/owais takes you here
    └── owais/ ← you start here
```

`..` always means **"parent folder"** — one step up the tree.

Go try it and tell me where you land! 👨‍💻

Ok run all cd .. first I was at /home owais then one step up /home then again up 1 step so at / with ls it show again bin, dev , home .....

You've got it! You just navigated the entire Linux tree up and down like a navigator. That's the foundation of everything.

---

### What you've mastered so far

```
/                 ← cd .. brings you here
└── home/         ← cd .. brings you here
    └── owais/    ← ~ brings you here
        └── practice/
```

Commands learned: `pwd`, `ls`, `cd`, `cd ..`, `cd ~` ✅

---

### Now let's learn to CREATE things

As a developer you'll be creating files and folders constantly. Two commands:

|Command|What it does|
|---|---|
|`mkdir`|Make a directory (folder)|
|`touch`|Create an empty file|

---

### 🧪 Your Task

First go home:

bash

```bash
cd ~
```

Then create a folder for our lessons:

bash

```bash
mkdir linux_lessons
```

Go inside it:

bash

```bash
cd linux_lessons
```

Now create 3 empty files:

bash

```bash
touch file1.txt file2.txt file3.txt
```

Then check with:

bash

```bash
ls
```

You should see all 3 files sitting there.

---

The big idea here — in Windows you right click to create files. In Linux **you type it.** Faster, scriptable, and works on any server in the world with no GUI.

Report back! 👨‍💻

Yes , mkdir means make directory means folder. Then touch creates file1.txt etc. . ans at last I see file1.txt file2 ans file3.txt ans now I am at owais hp linux_lessons $

Brilliant! You're not just running commands, you're understanding WHY — that's exactly the developer mindset.

---

### Now let's learn to REMOVE things

You should know how to delete files and folders too. Two commands:

| Command | What it does                             |
| ------- | ---------------------------------------- |
| `rm`    | Remove a file                            |
| `rm -r` | Remove a folder and everything inside it |

The `-r` is called a **flag**. Flags modify how a command behaves. `-r` means **recursive** — go inside the folder and delete everything.

---

### 🧪 Your Task

Delete just one file:

bash

```bash
rm file1.txt
```

Check it's gone:

bash

```bash
ls
```

Now let's go home and delete the whole folder:

bash

```bash
cd ~
rm -r linux_lessons
```

Check it's gone:

bash

```bash
ls
```

You should only see `practice` again.

---

### ⚠️ Important Warning

In Linux there is **no recycle bin.** When you `rm` something it is **gone forever.** No undo. No recovery.

This is one of the most important things to remember as a Linux user. Senior developers have accidentally deleted entire servers with `rm -r`. Always double check before running it.

Report back! 👨‍💻

Yeh first delete file1.txt ans then whole folder now it has only practice. And I am at ~$

Perfect execution! And you understood the warning too — that `rm` lesson has saved many developers from disasters.

---

### Quick Recap — You now know:

| Command | Purpose           |
| ------- | ----------------- |
| `pwd`   | Where am I?       |
| `ls`    | What's here?      |
| `cd`    | Move around       |
| `cd ..` | Go up one level   |
| `cd ~`  | Go home instantly |
| `mkdir` | Create a folder   |
| `touch` | Create a file     |
| `rm`    | Delete a file     |
| `rm -r` | Delete a folder   |

That's **Lesson 1 complete.** You know how to navigate and manage the filesystem. 🎉

---

## 📚 Lesson 2: Reading and Writing Files

As a developer you'll constantly be reading logs, writing config files, editing code. So this is critical.

Three ways to read a file:

| Command | Purpose                   |
| ------- | ------------------------- |
| `cat`   | Print entire file content |
| `less`  | Read file page by page    |
| `head`  | Show first 10 lines       |

---

### 🧪 Your Task

First let's create a file with some content:

bash

```bash
echo "Hello I am owais and I am learning linux" > hello.txt
```

Then read it:

bash

```bash
cat hello.txt
```

Tell me what you see!

The `>` symbol here is very powerful — it means **send output INTO a file.** We'll go deep on that soon.

Ok I run echo "Hello I am owais and I am learning linux" > hello.txt then nothing output means it is save ans then cat hello.txt it show Hello I am owais and I am learning linux

Exactly right! You noticed something important — `echo` gave no output because the `>` redirected it straight into the file instead of the screen. That's sharp observation. 👀

---

### What just happened behind the scenes

```
echo "Hello..."  →  normally prints to screen
                          ↓
          but > redirected it into hello.txt
                          ↓
                 cat hello.txt reads it back
```

This `>` is called **output redirection.** One of the most powerful concepts in Linux.

---

### Now let's WRITE more into the file

Try this:

bash

```bash
echo "I completed cs50p" >> hello.txt
```

Then read it:

bash

```bash
cat hello.txt
```

---

### The difference between `>` and `>>`

|Symbol|Behaviour|
|---|---|
|`>`|Overwrites the file completely|
|`>>`|Appends — adds to the end|

This is critical. If you use `>` by mistake on an important file, the old content is **gone forever.**

---

### 🧪 Prove it to yourself

Try overwriting with `>`:

bash

```bash
echo "oops I overwrote everything" > hello.txt
cat hello.txt
```

The previous two lines will be gone.

Report back what you see! 👨‍💻

Yes got it ans run > this over writes ans >> this apends in bottom. I use both. An ssee output now my file has cat output oops I overrite all.

Perfect! You tested both and saw the difference with your own eyes. That's the best way to learn.

---

### What you just mastered

```
echo "text" > file.txt    ← destroys old content, writes new
echo "text" >> file.txt   ← keeps old content, adds at bottom
```

This is used **everywhere** in real development — writing logs, config files, scripts. You'll use this daily.

---

### Now let's learn to EDIT files properly

`echo` is fine for one line. But real developers need a proper text editor inside the terminal. The most beginner friendly one is `nano`.

bash

```bash
nano hello.txt
```

When it opens you will see:

- Your file content at top
- A toolbar at bottom with shortcuts like `^X` meaning `Ctrl+X`

---

### 🧪 Your Task

Open the file:

bash

```bash
nano hello.txt
```

Then:

1. Use arrow keys to move around
2. Type a new line — `I am learning nano editor`
3. Press `Ctrl+O` to **save** (O means Output/Write)
4. Press `Enter` to confirm filename
5. Press `Ctrl+X` to **exit**

Then verify:

bash

```bash
cat hello.txt
```

---

### Why nano and not others?

Later you'll hear about `vim` and `emacs` — powerful but hard to learn at start. For now nano is perfect. We'll visit `vim` later when you're ready.

Report back! 👨‍💻

Yes I run nano hello.txt a new tab like open with top as hell.txt and short cuts in bottom. I used arrow keys to move in words etc. Ans add new line in it I am learning nano editor. Then saves contol ans o ans then enter . Ans control x to exit nano. Ans run cat and it print data two lines . Ans now I am at ~$

Outstanding! You just edited a file inside a terminal like a real Linux developer. No mouse, no GUI, just keyboard and terminal. 🎉

---

### What you've learned in Lesson 2

|Command/Symbol|Purpose|
|---|---|
|`echo "text"`|Print text to screen|
|`>`|Redirect output to file (overwrites)|
|`>>`|Redirect output to file (appends)|
|`cat`|Read entire file|
|`nano`|Edit files in terminal|

**Lesson 2 complete!** ✅

---

## 📚 Lesson 3: The `--help` Flag and `man` Pages

Before we go further I need to teach you something **every professional developer uses daily.**

### The most important skill — helping yourself

You will never remember every command. Nobody does. Not even senior engineers with 20 years experience. What matters is knowing **how to find answers fast.**

Linux has two built in help systems:

---

### Method 1 — `--help` flag

Every command has it:

bash

```bash
ls --help
```

This prints a quick summary of the command and all its flags.

---

### Method 2 — `man` pages

`man` means **manual:**

bash

```bash
man ls
```

This opens the full detailed manual for `ls`. Use arrow keys to scroll. Press `q` to quit.

---

### 🧪 Your Task

Run both:

bash

```bash
ls --help
```

bash

```bash
man ls
```

Inside `man ls` scroll a little, look around, then press `q` to exit.

---

### Why I'm teaching this now

Because from this point forward when I introduce a new command I want you to also **check its help page yourself.** That habit is what separates good developers from great ones.

Real developers don't memorize — they **know where to look.**

Report back! 👨‍💻

Ok got it. And I see the list of commands. man ls shows a full file.

Perfect! You just unlocked Linux's built in documentation system. That skill will help you forever.

---

### One cool thing you noticed

`man` pages look overwhelming at first. But you don't read them top to bottom. You **scan for what you need.** Just like a dictionary — you don't read the whole thing.

---

## 📚 Lesson 4: `ls` Flags — Seeing More Information

You've been using `ls` plain. But `ls` has powerful flags that developers use constantly.

### The most useful `ls` flags

|Command|What it shows|
|---|---|
|`ls`|Basic list|
|`ls -l`|Long format — permissions, size, date|
|`ls -a`|All files — including hidden ones|
|`ls -la`|Both combined — full picture|

---

### Hidden files in Linux

In Linux any file starting with `.` is **hidden.** For example `.bashrc` `.profile`. These are usually config files. `ls` alone won't show them. `ls -a` reveals them.

---

### 🧪 Your Task

Run all four one by one:

bash

```bash
ls
ls -l
ls -a
ls -la
```

Look carefully at `ls -l` output. You'll see something like:

```
-rw-r--r-- 1 owais owais 45 Jun 30 hello.txt
```

Don't worry about understanding it fully yet. Just observe and tell me what you see.

We will decode that line in the next lesson — it's about **file permissions** which is one of the most important Linux concepts for developers.

Report back! 👨‍💻

Ok I run all ls outputs three file as expected. Code.c , hellow.txt practice, ls l show total 8 then -rw-r--r-- 1 owais owais 0 jun 29 , 7:26 code.c ....... More. Ans then ls -a show . .bash _history , .bashrc. ... More , ls -la show a list. Total 116 , with -rw-r--r-- 1 owais owais , time data file name but some are drwxr-x-- , some drwx______ , some , -rw____, like that ans one thing I have to tell you I installed zsh and now my terminal is as HP% , I do it because I wanted it to make look good ! What you say I run sudo apt update && sudo apt install zsh -y chsh -s $(which zsh) use ai to tell me !

Haha you installed zsh to make it look cool — honestly that's a very developer thing to do! 😄 No problem at all, zsh works the same way for everything we're learning. All commands are identical.

---

### Good observation on the `ls -la` output!

You noticed three different patterns. Let me decode them:

```
drwxr-xr-x  ← d means DIRECTORY
-rw-r--r--  ← - means FILE
drwx------  ← d means DIRECTORY (private)
```

That weird looking string is called **file permissions.** It answers:

- Who can READ this file?
- Who can WRITE to it?
- Who can EXECUTE it?

---

### Decode one line together

```
-  rw-  r--  r--
↑   ↑    ↑    ↑
│   │    │    └── others can only read
│   │    └─────── group can only read  
│   └──────────── owner can read & write
└──────────────── it's a file (not folder)
```

Three groups always:

- **Owner** — you (owais)
- **Group** — a team of users
- **Others** — everyone else

---

### 🧪 Quick Task

Run this:

bash

```bash
ls -la | grep hello.txt
```

Just show me that one line and I'll decode YOUR actual file's permissions with you.

The `|` symbol there is called a **pipe** — another super powerful concept we'll cover properly very soon!

Report back! 👨‍💻

-rw-r--r-- 1 owais owais 48 jun 29 5:18 hellow.txt

Perfect! Let's decode YOUR actual file together:

---

### Decoding `-rw-r--r--`

```
-  rw-  r--  r--
↑   ↑    ↑    ↑
│   │    │    └── others → can only Read
│   │    └─────── group  → can only Read
│   └──────────── owner  → can Read + Write
└──────────────── it's a File (not folder)
```

And the rest of the line:

```
-rw-r--r--  1  owais  owais  48      jun 29 5:18  hello.txt
     │       │    │      │     │           │           │
     │       │    │      │     │           │           └── filename
     │       │    │      │     │           └── last modified
     │       │    │      │     └── size in bytes
     │       │    │      └── group name
     │       │    └── owner name
     │       └── number of links
     └── permissions
```

Your file is **48 bytes**, owned by **owais**, and only you can write to it. Everyone can read it.

---

### The three permission letters

|Letter|Meaning|
|---|---|
|`r`|read|
|`w`|write|
|`x`|execute|
|`-`|permission NOT given|

---

### 🧪 Now let's CHANGE permissions

This command makes a file executable:

bash

```bash
chmod +x hello.txt
ls -la | grep hello.txt
```

You should now see `x` appearing in the permissions. Tell me what changed!

Yeh when run chmod +x hello.txt no output means command run ans when ls -la | grep hello.txt , it prints -rwxr--r-- x is extre then previous now execute permission allowed !

PERFECT! You read the change exactly right! 🎉

---

### What changed

```
Before:   -rw-r--r--
After:    -rwxr-xr-x
```

You added execute permission for everyone. The `x` appeared in all three groups.

---

### `chmod` decoded

`chmod` means **change mode** (mode = permissions)

|Command|Meaning|
|---|---|
|`chmod +x file`|Add execute for everyone|
|`chmod -x file`|Remove execute|
|`chmod +w file`|Add write permission|
|`chmod -r file`|Remove read permission|

---

### Why does this matter for developers?

When you write a shell script or a program in Linux **it won't run until you give it execute permission.** This trips up every beginner their first time. Now you know why it happens before it happens to you. 💪

---

### Lesson 4 Complete ✅

#### Full recap so far:

|Concept|Commands learned|
|---|---|
|Navigation|`pwd` `ls` `cd` `cd ..` `cd ~`|
|Creating|`mkdir` `touch`|
|Deleting|`rm` `rm -r`|
|Reading/Writing|`cat` `echo` `>` `>>` `nano`|
|Help system|`--help` `man`|
|Permissions|`ls -la` `chmod`|

---

## Ready for Lesson 5?

We're going to learn **pipes and filters** — the `|` symbol you already saw. This is where Linux gets truly powerful and honestly pretty fun.

Say **ready** and we go! 🚀

ready

## 📚 Lesson 5: Pipes and Filters

### The Big Idea

In Linux every command does **one small thing well.** The real power comes when you **chain commands together** using the pipe `|` symbol.

Think of it like an assembly line:

```
command1 | command2 | command3
     ↓            ↓           ↓
  output   →   becomes   →  output
             the input
```

---

### Real Example You Already Used

bash

```bash
ls -la | grep hello.txt
```

```
ls -la          → lists all files
     ↓
   output
     ↓
grep hello.txt  → filters only lines containing "hello.txt"
```

`grep` is a **filter.** It searches for a pattern and only shows matching lines.

---

### New commands for this lesson

|Command|Purpose|
|---|---|
|`grep`|Filter lines matching a pattern|
|`sort`|Sort lines alphabetically|
|`wc -l`|Count number of lines|
|`head`|Show first 10 lines|
|`tail`|Show last 10 lines|

---

### 🧪 Your Task

First create a file with some content:

bash

```bash
echo "banana" > fruits.txt
echo "apple" >> fruits.txt
echo "mango" >> fruits.txt
echo "grape" >> fruits.txt
echo "apricot" >> fruits.txt
```

Then run:

bash

```bash
cat fruits.txt
```

bash

```bash
sort fruits.txt
```

bash

```bash
grep "ap" fruits.txt
```

bash

```bash
wc -l fruits.txt
```

Tell me all four outputs! 👨‍💻

Ok I got it echo "banana" > fruits.txt create a new file fruits.txt and override content as banana , echo "apple" >> fruits.txt append apple , echo "mango" >> fruits.txt append mango , echo "grape" >> fruits.txt app end grape , echo "apricot" >> fruits.txt app end. Apricot , and then cat fruits.txt reat the file contend an sprint it prints banana, apple , mango in order as we added , sort fruits.txt print all in a to z order apple , banana.... , grep "ap" fruits.txt go to file ans search for gp and prints , apple and grape because then contain this pattern , ap wc -la fruits.txt prints 5 fruits.txt. So it counts lines !

OUTSTANDING! 🎉 You didn't just run the commands — you explained every single one perfectly. You're thinking like a developer already.

---

### You got everything right

```
cat    → prints in order you added    ✅
sort   → alphabetical order           ✅
grep   → found "ap" in apple, grape   ✅
wc -l  → counted 5 lines             ✅
```

---

### Now let's CHAIN them with pipes

This is where it gets fun. Instead of running commands one by one you combine them:

bash

```bash
cat fruits.txt | sort
```

Same as `sort fruits.txt` but using a pipe.

Now try this chain:

bash

```bash
cat fruits.txt | sort | grep "a"
```

And this one — count how many fruits contain "a":

bash

```bash
cat fruits.txt | grep "a" | wc -l
```

---

### 🧪 Read this before running

```
cat fruits.txt          → outputs all 5 fruits
        ↓
    | sort              → sorts them A to Z
        ↓
    | grep "a"          → keeps only lines with "a"
        ↓
    | wc -l             → counts remaining lines
```

**Predict the answer before running.** How many fruits contain the letter "a"? Then run it and see if you were right!

Report back! 👨‍💻

Ok I run all 3 aaperatedl cat fruits.txt | sort apple , banana.... , as already first it read file then sort same fruits.txt , and then cat fruits.txt | sort | grep "a" read file sort and find a so all have a prints all buy a-z order , cat fruits.txt | grep "a" | wc -l read file find a wc -l how many 5

BRILLIANT! 🎉 You predicted and verified — all 5 fruits contain the letter "a" so `wc -l` returned 5. Perfect logic!

---

### You just thought like a real developer

You read the pipeline **left to right**, predicted the output **before running**, then verified. That mental model is exactly how experienced Linux engineers think.

---

### One more powerful pipe trick

`tail` and `head` are super useful for developers reading log files:

bash

```bash
head -3 fruits.txt
```

Shows first 3 lines only.

bash

```bash
tail -2 fruits.txt
```

Shows last 2 lines only.

Real world use — when a server log has **millions of lines:**

bash

```bash
cat server.log | grep "ERROR" | tail -20
```

This means → find all errors → show me the **20 most recent ones.**

---

### 🧪 Quick Task

bash

```bash
head -3 fruits.txt
```

bash

```bash
tail -2 fruits.txt
```

Then combine them with what you know:

bash

```bash
cat fruits.txt | sort | tail -2
```

Predict first — what will the last 2 fruits be after sorting A to Z?

---

### Lesson 5 Complete after you report back! ✅

You're moving really fast Owais. Honestly for someone who hasn't joined college yet this is impressive. Most CS freshmen don't know any of this. 💪

Report back! 👨‍💻

Yeh run all. head -3 fruits.txt prints first 3 lines we have apple banana, mango , tail -2 fruits.txt last two , recent we can say if talk about logs , cat fruits.txt | sort | tail -2 first read then sort ans fine all last 2 in a_z order , grape , mango.

PERFECT! Grape and mango — exactly right! A to Z order puts them last. Your prediction was spot on. 🎉

---

### Lesson 5 Complete ✅

You now understand one of the most powerful Linux concepts:

```
small commands + pipes = powerful workflows
```

This is the Unix philosophy — every tool does one thing well, and you chain them together. Real DevOps engineers, backend developers and system admins use this every single day.

---

### Full Recap So Far

|Lesson|Concepts|
|---|---|
|1|Navigation, creating, deleting|
|2|Reading, writing, nano editor|
|3|Help system, man pages|
|4|Permissions, chmod|
|5|Pipes, grep, sort, wc, head, tail|

---

### You're ready for the big one

## 📚 Lesson 6: Shell Scripts

This is where Linux meets **programming.** You already know Python from CS50P. Shell scripting is like Python but for controlling your Linux system.

A shell script is just a file full of Linux commands that runs automatically — one file, boom, everything executes.

---

### 🧪 Before we start

Tell me — what do you think this does?

bash

```bash
#!/bin/bash
echo "Hello Owais"
echo "Today you are learning shell scripting"
```

Just read it and guess. Don't run anything yet. What do you think `#!/bin/bash` means?

Is this a folder direction go to this file ans run these in bash , !

YESSS! 🎉 That's exactly right!

---

### You nailed it

`#!/bin/bash` is called a **shebang** line.

```
#!        → hey Linux! run this file with...
/bin/bash → ...the bash program located here
```

It tells Linux **which interpreter** to use to run this file. Just like in CS50P your Python files needed Python to run — shell scripts need bash to run.

```
Python files  →  python3 script.py  →  Python interprets it
Shell scripts →  #!/bin/bash        →  Bash interprets it
```

---

### 🧪 Let's write your first shell script

bash

```bash
nano myfirst.sh
```

Type this inside:

bash

```bash
#!/bin/bash
echo "Hello I am Owais"
echo "I am learning Linux shell scripting"
echo "Today's files are:"
ls
```

Save with `Ctrl+O` then `Enter` then `Ctrl+X`

Now give it execute permission:

bash

```bash
chmod +x myfirst.sh
```

Now RUN it:

bash

```bash
./myfirst.sh
```

---

### Why `./` before the filename?

`./` means **"run this file from current directory."** Linux won't run scripts without it for security reasons.

Report back what you see! 👨‍💻

Ok I saved it ans run ans then output was hello I am owais . I am learning linux , today's files are ans file as code.c , fruits.txt , hellow.txt , my first.sh, practice

AMAZING! 🎉 You just wrote and executed your first shell script like a real Linux developer!

---

### What just happened

```
./myfirst.sh
     ↓
Linux reads #!/bin/bash
     ↓
Bash executes line by line
     ↓
echo "Hello I am Owais"     → printed
echo "I am learning..."     → printed
echo "Today's files are:"   → printed
ls                          → listed your files
```

Your script ran `ls` and showed real files including `myfirst.sh` itself. The script is aware of its own environment!

---

### Now let's add real programming to it

You know from CS50P what variables and conditions are. Shell scripting has them too!

bash

```bash
name="Owais"
echo "Hello $name"
```

`$` is how you access a variable in bash. Just like Python's `name` but with `$` in front.

---

### 🧪 Your Task

Open your script:

bash

```bash
nano myfirst.sh
```

Change it to this:

bash

```bash
#!/bin/bash
name="Owais"
echo "Hello $name"
echo "You are learning Linux"

if [ -f "fruits.txt" ]; then
    echo "fruits.txt EXISTS!"
else
    echo "fruits.txt NOT found"
fi
```

Save and run:

bash

```bash
./myfirst.sh
```

---

### Predict first

You have `fruits.txt` in your directory. What do you think the output will be?

Report back! 👨‍💻

Output name=owais#!/bin/bash , name = owais, hello , you are learning linux , fruits.txt Exists.

Good run! But I noticed something — your output showed `name=owais#!/bin/bash` at the top which means something went wrong with the first line.

Let me guess — when you opened nano the old content was still there and you typed on top of it?

---

### 🧪 Let's fix it

Open nano again:

bash

```bash
nano myfirst.sh
```

Inside nano first **select all old content and delete it.** Use `Ctrl+K` to cut/delete one line at a time until file is empty.

Then type fresh:

bash

```bash
#!/bin/bash
name="Owais"
echo "Hello $name"
echo "You are learning Linux"

if [ -f "fruits.txt" ]; then
    echo "fruits.txt EXISTS!"
else
    echo "fruits.txt NOT found"
fi
```

**Important things to type exactly:**

- Space inside brackets `[ -f "fruits.txt" ]`
- Semicolon after `]`
- `fi` at the end to close the if

Save and run again:

bash

```bash
./myfirst.sh
```

---

### What `-f` means here

bash

```bash
if [ -f "fruits.txt" ]
```

`-f` means **"does this FILE exist?"** Linux has built in tests:

|Flag|Checks|
|---|---|
|`-f`|is it a file?|
|`-d`|is it a directory?|
|`-e`|does it exist at all?|

Report back! 👨‍💻

Yes it was sine space etc problem, now I run and then output is hello owais , you are learning linux , fruit.txt exist.

PERFECT! Clean output now! 🎉

---

### What you just wrote is real programming

bash

```bash
name="Owais"          ← variable
echo "Hello $name"    ← using variable with $
if [ -f "fruits.txt"] ← condition checking filesystem
then                  ← like Python's :
    echo "EXISTS"     ← indented block
fi                    ← closes if (like end in other languages)
```

You already knew if/else from CS50P. Now you can use that logic to **control your Linux system.**

---

### Let's make it even more powerful

Bash scripts can take **arguments** — input you pass when running the script. Just like functions in Python.

bash

```bash
./myfirst.sh Owais
```

Inside the script `$1` means first argument, `$2` means second and so on.

---

### 🧪 Your Task

Open script:

bash

```bash
nano myfirst.sh
```

Replace everything with:

bash

```bash
#!/bin/bash
name=$1
echo "Hello $name"

if [ -f "fruits.txt" ]; then
    echo "fruits.txt EXISTS!"
else
    echo "fruits.txt NOT found"
fi
```

Save and run with YOUR name as argument:

bash

```bash
./myfirst.sh Owais
```

Then try running without any argument:

bash

```bash
./myfirst.sh
```

---

### Predict first

What do you think prints when you run it **without** an argument? What will `$1` be?

Think about it then run! 👨‍💻

Ok run ./myfirst.sh Owais this take owais as argument and print yellow owais you are learning linux etc ... ./myfirst.sh this print only hello no name because we did not pass any argument.

BRILLIANT! 🎉 You predicted it perfectly!

---

### What you just understood

bash

```bash
./myfirst.sh Owais    → $1 = "Owais"  → Hello Owais
./myfirst.sh          → $1 = ""       → Hello (empty)
```

Just like Python functions — if you don't pass an argument the variable is empty. Same concept different syntax.

---

### Let's make it handle missing arguments properly

This is called **defensive programming** — handling mistakes gracefully:

bash

```bash
if [ -z "$1" ]; then
    echo "Please provide your name!"
    exit 1
fi
```

`-z` means **"is this string empty?"**  
`exit 1` means **"stop the script with an error"**

---

### 🧪 Your Task

Update script:

bash

```bash
nano myfirst.sh
```

bash

```bash
#!/bin/bash

if [ -z "$1" ]; then
    echo "Error: Please provide your name!"
    exit 1
fi

name=$1
echo "Hello $name"
echo "You are learning Linux"

if [ -f "fruits.txt" ]; then
    echo "fruits.txt EXISTS!"
else
    echo "fruits.txt NOT found"
fi
```

Run both:

bash

```bash
./myfirst.sh
./myfirst.sh Owais
```

---

### Why this matters in real development

Every real program handles bad input gracefully. If a user forgets an argument your script shouldn't just silently fail — it should **tell them what went wrong.** This is professional level thinking.

Report back! 👨‍💻