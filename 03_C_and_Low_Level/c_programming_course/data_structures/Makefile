CC = gcc
CFLAGS = -Wall -Wextra -Werror -pedantic -std=c11 -g
LDFLAGS = 
SRC = $(wildcard *.c)
OBJ = $(SRC:.c=.o)
EXEC = ds_test

all: $(EXEC)

$(EXEC): $(OBJ)
	$(CC) $(LDFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ) $(EXEC)

.PHONY: all clean
