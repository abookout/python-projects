import sys
import os
import curses
from curses import wrapper, ascii
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
    Draw an ascii box (a hollow rectangle) with width w and height h.
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


def _fill_rect(scr, y, x, h, w, char):
    """
    Fill a rectangular area with a given character.
    """
    for _y in range(h-y):
        for _x in range(w-x):
            scr.addch(_y + y, _x + x, char)

def _get_input(scr, y, x, in_len):
    """
    Allow the user to type in the input box. Return the string they typed.
    x and y are the location that the input will appear (on a single line)
    and in_len is maximum input length.
    """
    result = list()     # list of chars
    #curses.echo()
    cx = 0
    tx = 0
    while True:
        c = scr.getch(y, x+cx)
        if c == curses.ascii.NL:
            break
        elif c == curses.KEY_BACKSPACE and cx > 0:
            del result[cx-1]
            cx = max(cx-1, 0)
            tx = max(tx-1, 0)
        elif c == curses.KEY_LEFT:
            cx = max(cx-1, 0)
        elif c == curses.KEY_RIGHT:
            cx = min(cx+1, tx)
        elif curses.ascii.isalpha(c) and cx < in_len:
            result.insert(cx, chr(c))
            tx += 1
            cx = min(cx+1, tx)
        scr.addstr(y, x, " "*(in_len))
        scr.addstr(y, x, "".join(result))
        #_debug_print(scr, "cx: {}, tx: {}, in_len: {}".format(cx, tx, in_len))
        scr.refresh()
        

    scr.addstr(y, x, " "*tx)
    scr.refresh()
    #curses.noecho()
    return "".join(result)


def _print_in_rect(scr, y, x, h, w, words):
    """
    Print a list of strings in the given rect area, wrapping words nicely.
    If a word is too long to fit in the box (width), it's cut short to fit.
    If there are too many words so that they would run off the bottom,
        they're just not printed.
    """
    # Position to print next word
    cx = 0
    cy = 0
    import time
    for word in words:
        # Check if printing this would run off the bottom
        if cy >= h:
            return
        if len(word) >= w:
            # Word is longer than box can handle. Print shortened on next line
            if cy+1 >= h:
                # No next line to print on (but maybe can fit more on cur line)
                continue
            # Go to next line for upcoming words
            scr.addstr(y+cy+1, x, word[:x+w-1-4]+".., ")
            cy += 2
            cx = 0

        elif cx + len(word) >= w-2:  # room for ', '
            # Printing this word here would run off the right side so go to
            #   next line before printing
            if cy+1 >= h:
                # No next line to print on. We're done here.
                return
            scr.addstr(y+cy, x+cx, " "*(w-2-cx))    # print over leftovers
            cx = 0
            cy += 1
            scr.addstr(y+cy, x+cx, word+", ")
            cx += len(word)+2

        else:
            # Print as usual
            scr.addstr(y+cy, x+cx, word+", ")
            cx += len(word)+2

        #42x24 aeiosu
        #_debug_print(scr,"cx: {}, cy: {}, x: {}, y: {}, w: {}, h: {}"\
        #        .format(cx, cy, x, y, w, h))

        #time.sleep(1)
        #scr.refresh()


def _debug_print(scr, string):
    scr.addstr(0,0, "("+string+")")


def main(stdscr):
    # Make sure terminal is big enough (curses is fussy)
    # Wrapper disabled our output so turn that back on for now
    curses.echo()
    term_size = os.get_terminal_size()
    if term_size[0] < 36 or term_size[1] < 22:
        sys.exit("I'm feeling a little claustrophobic...\n"
              "Curses needs a bigger terminal window to display properly.\n")

    filename = ""
    chars = ""
    min_chars = 4
    if len(sys.argv) == 2:
        # Pick some random chars
        iwhjdiojqfoiqjdoiqjo
    elif len(sys.argv) == 3:
        # User passed both filename and chars as params
        filename = sys.argv[1]
        chars = sys.argv[2]
    elif len(sys.argv) == 4:
        filename = sys.argv[1]
        chars = sys.argv[2]
        try:
            min_chars = int(sys.argv[3])
        except ValueError:
            sys.exit("Need a number for min_chars: found {}".format(min_chars))
    else:
        sys.exit("Hi! Thanks for trying my game. Run it with either: \n"
              "  'python3 {} <json file> <chars>', or\n"
              "  'python3 {} <json file> <chars> <min word size>'.\n"
              .format(sys.argv[0], sys.argv[0]))
    
    curses.noecho()

    require_char = chars[0]
    chars = ''.join(sorted(list(set(chars))))

    # Set up window lookin' nice (curses)
    stdscr.clear()
    stdscr.border(0)

    _addstr_center_h(stdscr, 1, "Adam's Word Game")
    stdscr.hline(2, 1, curses.ACS_HLINE, curses.COLS-2)
    stdscr.addstr(3, 1, "Loading...")
    stdscr.refresh()
    words = get_anagrams(filename, chars)

    # Just take out any words that are shorter than min chars
    words = [word for word in words if len(word) >= min_chars]

    stdscr.addstr(3, 1, " "*10) # clear loading

    #TEST
    #stdscr.addstr(3, curses.COLS//4, "|")
    #stdscr.addstr(3, curses.COLS*3//4, "|")

    # Calculate positions of avail. letter box and required letter box
    avail_size = len(chars) + 2
    avail_pos_x = curses.COLS // 4 - avail_size // 2
    avail_pos_y = 4
    _draw_box(stdscr, avail_pos_y, avail_pos_x, 3, avail_size)
    a_l = "Available letters"
    stdscr.addstr(avail_pos_y+3, curses.COLS//4 - len(a_l)//2, a_l)

    req_size = 3
    req_pos_x = curses.COLS * 3 // 4 - req_size//2
    req_pos_y = 4
    _draw_box(stdscr, req_pos_y, req_pos_x, 3, req_size)
    r_l = "Required letter"
    stdscr.addstr(req_pos_y+3, curses.COLS*3//4 - len(r_l)//2, r_l)

    stdscr.addstr(avail_pos_y+1, avail_pos_x+1, chars)
    stdscr.addch(req_pos_y+1, req_pos_x+1, require_char)

    # Get positions for user input, found word total, and found words box
    progress_y = curses.LINES - 1
    progress_x = 3

    input_box_y = avail_pos_y  + 6   # Down from "Available letters" w/ pad
    input_box_x = 3
    stdscr.addstr(input_box_y-1, input_box_x, "Input")
    input_box_h = 3
    input_box_w = curses.COLS - input_box_x * 2
    _draw_box(stdscr, input_box_y, input_box_x, input_box_h, input_box_w)

    found_words_box_y = input_box_y + 6
    found_words_box_x = input_box_x
    stdscr.addstr(found_words_box_y-1, found_words_box_x, "Found words")
    found_words_box_h = progress_y-1 - found_words_box_y
    found_words_box_w = input_box_w
    _draw_box(stdscr, found_words_box_y, found_words_box_x, found_words_box_h,\
              found_words_box_w)

    stdscr.refresh()

    # Get pos of message for user
    message_x = input_box_x + 5
    message_y = input_box_y + input_box_h + 1
    message_w = input_box_w-6

    progress_str = "Found {} out of {} total words."
    found_words = list()
    guess = True
    user_input = ""
    while True:
        # Game loop: 
        if guess:
            # Update user's progress
            stdscr.addstr(progress_y, progress_x,\
                          progress_str.format(len(found_words), len(words)))
            # Update found words box
            _fill_rect(stdscr, found_words_box_y+1, found_words_box_x+1,\
                       found_words_box_h-2, found_words_box_w-2,\
                       curses.ascii.SP)
            _print_in_rect(stdscr, found_words_box_y+1, found_words_box_x+1,\
                           found_words_box_h-2, found_words_box_w-2,\
                           found_words)
            stdscr.refresh()

        # Blocking wait for user to type a word (and hit enter)
        user_input = _get_input(stdscr, input_box_y+1,\
                                input_box_x+1, input_box_w-2)

        # Check if user used bad letters
        bad_letters = set([x for x in user_input if x not in chars])

        # Check if we recognize that word
        if user_input in words and user_input not in found_words:
            found_words.append(user_input)
            found_words.sort()
            stdscr.addstr(message_y, message_x, " " * message_w)
            stdscr.addstr(message_y, message_x, "Good job!")
            stdscr.refresh()
            guess = True
        elif user_input in found_words:
            stdscr.addstr(message_y, message_x, " " * message_w)
            stdscr.addstr(message_y, message_x, "You already got that one!")
            stdscr.refresh()
            guess = False
        elif bad_letters:
            stdscr.addstr(message_y, message_x, " " * message_w)
            stdscr.addstr(message_y, message_x, "Bad letters: {}"\
                          .format("".join(bad_letters)))
            stdscr.refresh()
            guess = False
        else:
            stdscr.addstr(message_y, message_x, " " * message_w)
            stdscr.addstr(message_y, message_x, "Wrong: {}".format(user_input))
            stdscr.refresh()
            guess = False


if __name__ == "__main__":
    # Curses wrapper to make things a little easier on myself
    print("test")
    wrapper(main)

