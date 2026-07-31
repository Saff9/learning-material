# Bash Scripting Cheatsheet

## Shebang

```bash
#!/bin/bash
```

## Variables

```bash
NAME="Alice"          # Set variable
echo $NAME            # Access variable
echo ${NAME}          # With braces
readonly PI=3.14      # Read-only variable
```

## Special Variables

| Variable | Meaning |
|----------|---------|
| `$0` | Script name |
| `$1-$9` | Arguments |
| `$#` | Number of arguments |
| `$@` | All arguments |
| `$?` | Exit status |
| `$$` | Process ID |

## Conditionals

```bash
if [ "$VAR" == "value" ]; then
    echo "Match"
elif [ "$VAR" == "other" ]; then
    echo "Other"
else
    echo "No match"
fi
```

## Loops

```bash
# For loop
for i in 1 2 3; do
    echo $i
done

# Range
for i in {1..10}; do
    echo $i
done

# While loop
while [ $COUNTER -lt 10 ]; do
    echo $COUNTER
    COUNTER=$((COUNTER + 1))
done

# Read file
while read line; do
    echo $line
done < file.txt
```

## Functions

```bash
myfunc() {
    echo "Hello, $1!"
}

myfunc "Alice"
```

## Arrays

```bash
ARR=("a" "b" "c")
echo ${ARR[0]}        # First element
echo ${ARR[@]}        # All elements
echo ${#ARR[@]}       # Length
ARR+=("d")            # Append
```

## Case Statement

```bash
case $VAR in
    start)
        echo "Starting..."
        ;;
    stop)
        echo "Stopping..."
        ;;
    *)
        echo "Unknown"
        ;;
esac
```

## Arithmetic

```bash
A=5
B=3
SUM=$((A + B))
let RESULT=A+B
```

## Input

```bash
read -p "Enter name: " NAME
read -sp "Enter password: " PASSWORD
```

## Safety Options

```bash
set -e          # Exit on error
set -u          # Exit on undefined variable
set -x          # Debug mode
set -o pipefail # Pipeline fails on any error
```
