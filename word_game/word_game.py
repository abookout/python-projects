import sys
import os
import curses
import json
from curses import wrapper, ascii
from anagram_generator import get_anagrams, load_json_dict

from word_game_lib import *

"""
This is a word-guessing game, where you must guess all of the words that can be
    made from a specified number of characters, with one "special" character
    that is guaranteed to be in every word.
"""


def main(stdscr):
    if len(sys.argv) != 2:
        sys.exit("\n\nHi! Thanks for trying my game.\n"
                 "This is a word guessing game, where you're given a "
                 "list of letters you must use to make words, as well as "
                 "one letter you must use in every word. You can change "
                 "it up by choosing specific letters or changing the "
                 "minimum word length.\n\n"
                 "In order to play it, you need a dictionary file in "
                 "json format. Run as follows:\n"
                 "  'python3 {} <json dictionary>'\n\n".format(sys.argv[0]))

    # Make sure terminal is big enough (curses is fussy)
    term_size = os.get_terminal_size()
    if term_size[0] < 42 or term_size[1] < 24:
        sys.exit("Error: I'm feeling a little claustrophobic...\n"
              "Curses needs a bigger terminal window to display properly.\n")

    filename = sys.argv[1]
    try:
        with open(filename) as f:
            jd = set(json.loads(f.read()))
            if not jd:
                sys.exit("Error: '{}' is not a valid dictionary."\
                            .format(filename))
    except IOError:
        sys.exit("Error: could not open (or perhaps find) file '{}'."\
                    .format(filename))


    # Set up window lookin' nice (curses)
    stdscr.clear()
    stdscr.border(0)
    curses.curs_set(0)# Make cursor invisible
    tmp = "Adam's Word Game"
    stdscr.addstr(1, curses.COLS//2-len(tmp)//2, tmp)
    stdscr.hline(2, 1, curses.ACS_HLINE, curses.COLS-2)

    # Show user settings screen
    chars, min_chars = _settings(stdscr)

    # Show something instead of hanging while getting words
    stdscr.addstr(3, 1, "Loading...")
    stdscr.refresh()
    words = get_anagrams(filename, chars)
    # Take out any words that are shorter than min chars
    words = [word for word in words if len(word) >= min_chars]

    if not words:
        sys.exit("Couldn't find any words in the dictionary with size >= {}"
                " consisting of the letters '{}'.".format(min_chars, chars))

    # Clear screen
    fill_rect(stdscr, 3, 1, curses.LINES-4, curses.COLS-2, curses.ascii.SP)
    stdscr.refresh()

    # Make cursor visible again
    curses.curs_set(2)

    # Start the game
    _game(stdscr, chars, min_chars, words)

def _settings(stdscr):
    """
    Display settings window to user so that they can choose to play with:
        either random chars (and how many), or specific chars (and which ones),
        as well as choose the minimum accepted word length.

    Return a tuple of (chars, min word size).
    """
    h_center = curses.COLS // 2

    tmp = "Navigate with the arrow keys."
    stdscr.addstr(3, h_center-len(tmp)//2, tmp)

    # Display instructions to start game
    start_text = "Press enter to begin the game!"
    start_text_y = curses.LINES-2
    start_text_x = h_center-len(start_text)//2
    stdscr.addstr(start_text_y, start_text_x, start_text)

    # Let user pick from playing with random chars or choosing their own
    rand_or_choose_y = 4
    rand_or_choose_sel = MultipleSelection(rand_or_choose_y+2,\
                                    ["Random letters", "Choose my own"])

    rand_or_choose_ob = OptionBox(rand_or_choose_y,\
                    "Would you like to play with:", rand_or_choose_sel)

    rand_or_choose_sel.draw(stdscr)
    rand_or_choose_ob.draw(stdscr, 2)

    # Setup letter count option (default to 6, the 4th option)
    rand_letter_count_y = rand_or_choose_y+6
    rand_letter_count_sel = MultipleSelection(rand_letter_count_y+2,\
                                            [str(i) for i in range(2, 10)], 4)
    rand_letter_count_ob = OptionBox(rand_letter_count_y,\
                    "How many letters?", rand_letter_count_sel)

    # Setup choose own letters option
    enter_own_letters_y = rand_letter_count_y
    enter_own_letters_if = InputField(enter_own_letters_y+2, 16)
    enter_own_letters_ob = OptionBox(enter_own_letters_y, "Enter them here:",\
                                     enter_own_letters_if)


    # Let user choose the minimum accepted word size
    min_word_size_y = rand_letter_count_y+6
    min_word_size_sel = MultipleSelection(min_word_size_y+2,\
                                        [str(i) for i in range(0, 10)], 4)
    min_word_size_ob = OptionBox(min_word_size_y,\
                    "Minimum word size:", min_word_size_sel)
    min_word_size_ob.draw(stdscr, 1)


    sel_input_groups = [rand_or_choose_ob, rand_letter_count_ob, min_word_size_ob]
    cur_group_i = 0

    while True:
        # Handle toggling second option box
        rcl_sel_val = rand_or_choose_sel.get_selection_index()
        if cur_group_i == 1:
            rcl_draw_type = 2   # full box or bracket
        else:
            rcl_draw_type = 1
        if rcl_sel_val == 0:
            # Show rand_or_choose
            #breakpoint()    # middle top and bottom not drawing in full box
            enter_own_letters_ob.clear(stdscr)
            rand_letter_count_ob.draw(stdscr, rcl_draw_type)
            stdscr.refresh()
            sel_input_groups[1] = rand_letter_count_ob
        elif rcl_sel_val == 1:
            # Show enter_own_letters
            rand_letter_count_ob.clear(stdscr)
            enter_own_letters_ob.draw(stdscr, rcl_draw_type)
            stdscr.refresh()
            sel_input_groups[1] = enter_own_letters_ob


        cur_group = sel_input_groups[cur_group_i].input_object

        # Enable the cursor if the current group is an input field
        if isinstance(cur_group, InputField):
            stdscr.move(*cur_group.get_cursor_pos())
            curses.curs_set(2)
        else:
            curses.curs_set(0)

        # Get user input (inc. arrow keys, return)
        c = stdscr.getch()
        if c == curses.ascii.NL:
            break
        elif c == curses.KEY_UP or c == curses.KEY_DOWN:
            sel_input_groups[cur_group_i].draw_brackets(stdscr)

            if c == curses.KEY_UP:
                cur_group_i = (cur_group_i - 1) % len(sel_input_groups)
            else:
                cur_group_i = (cur_group_i + 1) % len(sel_input_groups)
            
            sel_input_groups[cur_group_i].draw_box(stdscr)


        elif isinstance(cur_group, MultipleSelection):  
            if c == curses.KEY_LEFT or c == curses.KEY_RIGHT:
                cur_group.change_selection(stdscr, c)
                cur_group.draw(stdscr)

        elif isinstance(cur_group, InputField):
            cur_group.handle_input(stdscr, c)
            cur_group.draw(stdscr)
        else:
            # Disable cursor
            curses.curs_set(0)

    roc_index = rand_or_choose_sel.get_selection_index()
    letters = ""
    if roc_index == 0:
        # User chose to generate some random letters
        letters = gen_chars(int(rand_letter_count_sel.get_selection_val()))
    elif roc_index == 1:
        # User chose their own letters
        letters = enter_own_letters_if.get_result()
    return (letters, int(min_word_size_sel.get_selection_val()))

def _game(stdscr, chars, min_chars, words):
    require_char = chars[0]
    chars = ''.join(sorted(list(set(chars))))

    #TEST
    #stdscr.addstr(3, curses.COLS//4, "|")
    #stdscr.addstr(3, curses.COLS*3//4, "|")

    # Calculate positions of avail. letter box and required letter box
    avail_size = len(chars) + 2
    avail_pos_x = curses.COLS // 4 - avail_size // 2
    avail_pos_y = 4
    draw_box(stdscr, avail_pos_y, avail_pos_x, 3, avail_size)
    a_l = "Available letters"
    stdscr.addstr(avail_pos_y+3, curses.COLS//4 - len(a_l)//2, a_l)

    req_size = 3
    req_pos_x = curses.COLS * 3 // 4 - req_size//2
    req_pos_y = 4
    draw_box(stdscr, req_pos_y, req_pos_x, 3, req_size)
    r_l = "Required letter"
    stdscr.addstr(req_pos_y+3, curses.COLS*3//4 - len(r_l)//2, r_l)

    stdscr.addstr(avail_pos_y+1, avail_pos_x+1, chars)
    stdscr.addch(req_pos_y+1, req_pos_x+1, require_char)

    # Get positions for user input, found word total, and found words box
    progress_y = curses.LINES - 1
    progress_x = 2

    input_box_y = avail_pos_y  + 6   # Down from "Available letters" w/ pad
    input_box_x = 3
    stdscr.addstr(input_box_y-1, input_box_x, "Input")
    input_box_h = 3
    input_box_w = curses.COLS - input_box_x * 2
    #draw_box(stdscr, input_box_y, input_box_x, input_box_h, input_box_w)

    found_words_box_y = input_box_y + 6
    found_words_box_x = input_box_x
    stdscr.addstr(found_words_box_y-1, found_words_box_x, "Found words")
    found_words_box_h = progress_y-1 - found_words_box_y
    found_words_box_w = input_box_w
    draw_box(stdscr, found_words_box_y, found_words_box_x, found_words_box_h,\
              found_words_box_w)

    stdscr.refresh()

    # Get pos of message for user (right-aligned)
    message_x = curses.COLS - 2 #input_box_x + 5
    message_y = input_box_y + input_box_h + 1
    message_w = input_box_w-6

    # Create and draw user input field
    user_input_field = InputField(avail_pos_y+6, input_box_w)
    user_input_field.draw(stdscr)

    # Show the minimum number of chars that a word can have
    print_right_align(stdscr, curses.LINES-1, curses.COLS-2,\
            "Min word size: {}".format(min_chars))

    found_words = list()
    guess = True
    user_input = ""
    while True:
        # Game loop: 
        if guess:
            # Update user's progress
            stdscr.addstr(progress_y, progress_x,\
                "Found {} of {} words".format(len(found_words), len(words)))
            # Update found words box
            fill_rect(stdscr, found_words_box_y+1, found_words_box_x+1,\
                       found_words_box_h-2, found_words_box_w-2,\
                       curses.ascii.SP)
            print_in_rect(stdscr, found_words_box_y+1, found_words_box_x+1,\
                           found_words_box_h-2, found_words_box_w-2,\
                           found_words)
            stdscr.refresh()
            guess = False

        # Blocking wait for user to type a word (and hit enter)
        while True:
            c = stdscr.getch(*user_input_field.get_cursor_pos())
            if c == curses.ascii.NL:
                user_input = user_input_field.get_result()
                user_input_field.clear_result()
                user_input_field.draw(stdscr)
                break
            else:
                user_input_field.handle_input(stdscr, c)
                user_input_field.draw(stdscr)
                stdscr.refresh()

        # Check if user used bad letters
        bad_letters = set([x for x in user_input if x not in chars])

        def display_message(message):
            print_right_align(stdscr, message_y, message_x, " " * message_w)
            print_right_align(stdscr, message_y, message_x, message)
            stdscr.refresh()

        # Check if we recognize that word and display a message to the user
        if user_input in words and user_input not in found_words:
            found_words.append(user_input)
            found_words.sort()
            display_message("Good job!")
            guess = True
        elif user_input in found_words:
            display_message("You already got that one!")
        elif bad_letters:
            display_message("Bad letters: {}".format("".join(bad_letters)))
        elif len(user_input) < min_chars:
            display_message("That word was too small.")
        elif not require_char in user_input:
            display_message("'{}' must appear in every word."\
                                .format(require_char))
        else:
            display_message("Wrong: {}".format(user_input))


        if len(found_words) == len(words):
            # User wins!
            break


    # Broke out of the loop. User won!
    win_msg_str1 = " Congrats, you found all {} words!! "
    win_msg_str2 = " Press any key to exit."
    win_msg_w = len(win_msg_str1)+2
    win_msg_h = 5
    win_msg_y = curses.LINES//2 - 5
    win_msg_x = curses.COLS//2 - win_msg_w//2
    fill_rect(stdscr, win_msg_y-1, win_msg_x-1, win_msg_h+2, win_msg_w+2,
              curses.ascii.SP)
    draw_box(stdscr, win_msg_y, win_msg_x, win_msg_h, win_msg_w)
    stdscr.addstr(win_msg_y+1, win_msg_x+1, win_msg_str1.format(len(found_words)))
    stdscr.addstr(win_msg_y+3, win_msg_x+1, win_msg_str2)
    while True:
        if stdscr.getch():
            sys.exit()

if __name__ == "__main__":
    # Curses wrapper to make things a little easier on myself
    wrapper(main)

