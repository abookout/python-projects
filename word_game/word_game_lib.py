import curses
from curses import ascii
import string   # string and random for generating random chars
import random

class OptionBox:
    """
    Store data for a rect box with a string header, as well as one type
        of data entry from the user. It's always centered horizontally
        because I don't ever need it to not be. Also it always has a height
        of 6.
    """

    def __init__(self, y, header_str, input_object):
        """
        Create a new option box. You need to pass the curses window, the 
            y position of the top left corner, the header string to display
            at the box's top, and the input object.
        """
        self.header_str = header_str
        self.input_object = input_object

        # Calculate x position of box left edge
        self.w = max(input_object.w, len(header_str))+2

        self.y = y
        self.x = curses.COLS//2 - (self.w)//2
        self.h = 6

    def draw(self, scr, box_type=0):
        """
        Draw both this option box and its input object.
        box_type:
            if 0, don't draw a box around it
            if 1, draw a bracket-type box
            if 2, draw a full box
        """
        # header
        scr.addstr(self.y+1, curses.COLS//2-(len(self.header_str)+1)//2, self.header_str)
        #scr.addstr(10, 2, "Header xpos: {}".format(curses.COLS//2-len(self.header_str)//2))

        # Also draw the input object
        self.input_object.draw(scr)

        if box_type == 1:
            self.draw_brackets(scr)
        elif box_type == 2:
            self.draw_box(scr)

    def draw_box(self, scr):
        """
        Draw a box around it
        """
        self.clear(scr)
        draw_box(scr, self.y, self.x, self.h, self.w)
        self.draw(scr)

    def draw_brackets(self, scr):
        """
        Draw a box around it except for a bit on the top and bottom lines
        """
        self.clear(scr)
        draw_box_brackets(scr, self.y, self.x, self.h, self.w)
        self.draw(scr)

    def clear(self, scr):
        """
        Clear everything drawn by draw()
        """
        fill_rect(scr, self.y, self.x, self.h, self.w, curses.ascii.SP)


class MultipleSelection:
    """
    Store current selection and handle cycling through possible selections.
    A selection is an item that the user can select with their arrow keys.
    Only can handle selections of height 3 (2 for the box, 1 for a char).
    If there are two selections in the group, it displays them with 
        " or " between.
    Also, it's always horizontally centered.
    """

    def __init__(self, y, selections, default_index=0):
        """
        Create a new selection group, where each selection is a (minimally 3x3)
            box with at least one character in it. The box is made visible
            iff its selection is active.

        selections should be a list of strings.

        y is the position of the top left of the selection area (the top-left
            corner of the leftmost selection item's box).

        default_index is an optional parameter. Use to pick a default selected
            item other than the first one.

        After constructor done, selections becomes list of tuples containing
            positions as well as contents of selections like (y, x, str)
            where y,x is the position of the box's top left.
        """
        if len(selections) < 2:
            sys.exit("Bad selection group: {}".format(selections))

        selections = [str(s) for s in selections]

        self.w = sum(len(s)+2 for s in selections)
        if len(selections) == 2:
            self.w += 4

        x = curses.COLS//2 - (self.w)//2

        # Calculate pos and dims for each selection's box
        y_positions = [y]*len(selections)
        x_positions = list()
        x_p = x
        for s in selections:
            x_positions.append(x_p)
            x_p += len(s)+2

        if len(selections) == 2:
            x_positions[1] += 4  # make room for " or " in x pos

        self.selections = list(zip(y_positions, x_positions, selections))

        self.y = y
        self.x = x
        self.h = 3
        self.curr_selection_i = default_index

    def draw(self, scr):
        """
        Repaint this selection group.
        """
        for s in self.selections:
            scr.addstr(s[0]+1, s[1]+1, s[2])

        #import pdb; pdb.set_trace()
        if len(self.selections) == 2:
            first_sel = self.selections[0]
            scr.addstr(first_sel[0]+1, first_sel[1]+len(first_sel[2])+2, " or ")
        selected = self.selections[self.curr_selection_i]
        draw_box(scr, selected[0], selected[1], 3, len(selected[2])+2)

    def clear(self, scr):
        """
        Clear everything drawn by draw()
        """
        fill_rect(scr, self.y, self.x, self.h, self.w, curses.ascii.SP)


    def get_selection_index(self):
        """
        Return index of currently selected selection.  Index corresponds to the
            same items that were passed into init, and also what appears on
            screen left to right.
        """
        return self.curr_selection_i


    def get_selection_val(self):
        """
        Return currently selected selection as the string that was passed when
            this MultipleSelection was created. 
        """
        return self.selections[self.curr_selection_i][2]

    def change_selection(self, scr, keypress):
        """
        Change selection within the active selection group. Handles drawing
            box and changing internal selection state.
        """
        if len(self.selections) > 1 and \
                (keypress == curses.KEY_LEFT or keypress == curses.KEY_RIGHT):
            
            # Clear old selection box
            old_sel = self.selections[self.curr_selection_i]
            old_sel_w = len(old_sel[2])+2   # Length of word + 2 for box
            clear_box(scr, old_sel[0], old_sel[1], 3, old_sel_w)

            if keypress == curses.KEY_LEFT:
                self.curr_selection_i -= 1
                self.curr_selection_i %= len(self.selections)
            elif keypress == curses.KEY_RIGHT:
                self.curr_selection_i += 1
                self.curr_selection_i %= len(self.selections)

            # Setup new selection
            new_sel = self.selections[self.curr_selection_i]
            new_sel_w = len(new_sel[2])+2

class InputField:
    """
    Allow the user to type into an input field. You can get what they typed
        from get_result(). The input field can only be of height 1.
    """
    def __init__(self, y, in_len):
        """
        y is y-pos of top-left corner of box, in_len is the maximum 
            input length allowed (can't enter anything longer than this)
        """
        self.result = list()
        self.in_len = in_len
        self.w = in_len+2
        self.y = y
        self.x = curses.COLS//2 - self.w//2

        # Keeping track of cursor position
        self.cx = 0
        self.tx = 0

    def handle_input(self, scr, c):
        """
        Pass a char from the keyboard to register it as input. Includes stuff
            like curses.KEY_LEFT for navigating. Does not handle the enter
            key (curses.ascii.NL).
        """
        cx = self.cx
        tx = self.tx
        if c == curses.KEY_BACKSPACE and cx > 0:
            del self.result[cx-1]
            cx = max(cx-1, 0)
            tx = max(tx-1, 0)
        elif c == curses.KEY_LEFT:
            cx = max(cx-1, 0)
        elif c == curses.KEY_RIGHT:
            cx = min(cx+1, tx)
        elif curses.ascii.isalpha(c) and cx < self.in_len:
            self.result.insert(cx, chr(c))
            tx += 1
            cx = min(cx+1, tx)

        self.cx = cx
        self.tx = tx
    
    def get_result(self):
        return "".join(self.result)

    def clear_result(self):
        self.result = list()
        self.cx = self.tx = 0

    def get_cursor_pos(self):
        return (self.y+1, self.x+self.cx+1)

    def draw(self, scr):
        """
        Draw the box around the input field as well as the string that the
            user typed (or is typing).
        """ 
        draw_box(scr, self.y, self.x, 3, self.w)
        result = self.get_result()
        if len(result) < self.in_len:
            result += " "*(self.in_len-len(result))
        scr.addstr(self.y+1, self.x+1, result)


def draw_box(scr, y, x, h, w):
    """
    Draw an ascii box (a hollow rectangle) with width w and height h.
    """
    scr.hline(y, x+1, curses.ACS_HLINE, w-2)
    scr.vline(y+1, x, curses.ACS_VLINE, h-2)
    scr.vline(y+1, x+w-1, curses.ACS_VLINE, h-2) 
    scr.hline(y+h-1, x+1, curses.ACS_HLINE, w-2)

    scr.addch(y, x, curses.ACS_ULCORNER)
    scr.addch(y, x+w-1, curses.ACS_URCORNER)
    scr.addch(y+h-1, x, curses.ACS_LLCORNER)
    scr.addch(y+h-1, x+w-1, curses.ACS_LRCORNER)



def draw_box_brackets(scr, y, x, h, w):
    """
    Draw an ascii box but without most of the top and bottom lines so that
        it looks like a big ol' pair of square brackets. Only actually
        different from draw_box if w > 4.
    """
    draw_box(scr, y, x, h, w)
    if w > 4:
        scr.hline(y, x+2, curses.ascii.SP, w-4)
        scr.hline(y+h-1, x+2, curses.ascii.SP, w-4)


def clear_box(scr, y, x, h, w):
    """
    Clear an ascii box (a HOLLOW rectangle) with width w and height h.
    """
    scr.hline(y, x, curses.ascii.SP, w)
    scr.vline(y+1, x, curses.ascii.SP, h-2)
    scr.vline(y+1, x+w-1, curses.ascii.SP, h-2) 
    scr.hline(y+h-1, x, curses.ascii.SP, w)


def fill_rect(scr, y, x, h, w, char):
    """
    Fill a rectangular area with a given character.
    """
    for _y in range(h):
        for _x in range(w):
            scr.addch(_y + y, _x + x, char)

def print_in_rect(scr, y, x, h, w, words):
    """
    Print a list of strings in the given rect area, wrapping words nicely.
    If a word is too long to fit in the box (width), it's cut short to fit.
    If there are too many words so that they would run off the bottom,
        they're just not printed.
    """
    # Position to print next word
    cx = 0
    cy = 0
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


def print_right_align(scr, y, x, word):
    """
    Print a string so that its last character is at y,x. Doesn't handle
        error checking.
    """
    scr.addstr(y, x-len(word), word)


def gen_chars(how_many):
    """
    Return a string of some random non-repeating characters, always with
        at least one vowel.
    """
    val = random.sample(string.ascii_lowercase, how_many)
    vowels = "aeiouy"
    if not any(c in val for c in vowels):
        # Replace a random one with a random vowel
        vowel = random.choice(vowels)
        index = random.randint(0, len(val)-1)
        val[index] = vowel

    return "".join(val)


def debug_print(scr, string):
    scr.addstr(0,0, "("+string+")")


