import sys
import os
import random

"""
Print n randomly-selected lines from the given file, where n is decided
    from user input.
"""

ERR = "Bad arguments: run with ./printlines <filename> <num lines>"
FNF = "Error: file \'{}\' not found."


#Source: https://stackoverflow.com/a/56973905
def get_random_line(f, file_size: int) -> str:
    #file_size = os.path.getsize(filepath)
    while True:
        pos = random.randint(0, file_size)
        if not pos:  # the first line is chosen
            return f.readline().decode()  # return str
        f.seek(pos)  # seek to random position
        f.readline()  # skip possibly incomplete line
        line = f.readline()  # read next (full) line
        if line:
            return line#.decode()  
        # else: line is empty -> EOF -> try another position in next iteration


def main():
    # Check arguments 
    argc = len(sys.argv)
    if argc != 3 or not sys.argv[2].isdigit():
        print(ERR)
        exit()

    # Read file
    filename = sys.argv[1]
    numlines = int(sys.argv[2])
    lines = list()
    try:
        with open(filename) as f:
            file_size = os.path.getsize(filename)
            lines = [get_random_line(f, file_size) for x in range(numlines)]
    except IOError:
        print(FNF)
        exit()

    [print(line) for line in lines]

if __name__ == "__main__":
    main()






