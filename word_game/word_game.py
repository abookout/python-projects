import sys
import os
import curses
from curses import wrapper
from anagram_generator import get_anagrams

"""
This is a word-guessing game, where you must guess all of the words that can be
    made from a specified number of characters, with one "special" character
    that is guaranteed to be in every word.
"""

def _addstr_center_h(scr, line, text):
    """
    Add horizontally-centered text.
    """
    scr.addstr(line, scr.getmaxyx()[1]//2 - len(text)//2, text)


def _draw_box(scr, y, x, h, w):
    """
    Draw an ascii box with width w and height h.
    """
    # top left corner, top, top right corner,
    scr.addch(y, x, curses.ACS_ULCORNER)
    scr.hline(y, x+1, curses.ACS_HLINE, w-2)
    scr.addch(y, x+w-1, curses.ACS_URCORNER)

    scr.vline(y+1, x, curses.ACS_VLINE, h-2)
    scr.vline(y+1, x+w-1, curses.ACS_VLINE, h-2) 
    
    scr.addch(y+h-1, x, curses.ACS_LLCORNER)
    scr.hline(y+h-1, x+1, curses.ACS_HLINE, w-2)
    scr.addch(y+h-1, x+w-1, curses.ACS_LRCORNER)


def main(stdscr):
    filename = ""
    chars = ""
    if len(sys.argv) == 3:
        # User passed both filename and chars as params
        filename = sys.argv[1]
        chars = sys.argv[2]
    elif len(sys.argv) == 1:
        # Get json file and chars from user; anagram generator handles errors
        filename = input("Please enter the file location of a json-formatted "
                         "word dictionary.\n")

        chars = input("Please enter some characters. The first character is "
                      "guaranteed to appear in every word.\n")
    else:
        print("Bad arguments. Use with either 'python3 {} <json file> <chars>'"
              "or just 'python3 {}'.".format(sys.argv[0], sys.argv[0]))
        exit()
        
    # Get dictionary file and specified characters from user
    #print("Loading...", end="")

    # Set up window lookin' nice (curses)
    stdscr.clear()
    stdscr.border(0)

    _addstr_center_h(stdscr, 1, "Adam's Word Game")
    stdscr.hline(2, 1, curses.ACS_HLINE, curses.COLS-2)
    stdscr.addstr(3, 1, "Loading...")
    stdscr.refresh()
    words = get_anagrams(filename, chars)
    term_size = stdscr.getmaxyx()       # Get window size

    _draw_box(stdscr, 5, 5, 3, 10)
    stdscr.refresh()

    while True:
        # Game loop: 
        # Blocking wait for user to type a word (and hit enter)

        # Check if we recognize that word
        pass

if __name__ == "__main__":
    # Curses wrapper to make things a little easier on myself
    wrapper(main)
