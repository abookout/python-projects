
class _OptionBox:
    """
    Store data for a rect box with a string header, as well as one type
        of data entry from the user. It's always centered horizontally
        screen because I don't ever need it to not be.
    """

    def __init__(self, y, header_str, input_object):
        self.header_str = header_str
        self.input_object = input_object

        self.y = y
        self.w = len(header_str)

        # Calculate x position of box left edge



class _MultipleSelection:
    """
    Store current selection and handle cycling through possible selections.
    A selection is an item that the user can select with their arrow keys.
    Only can handle selections of height 3 (2 for the box, 1 for a char).
    If there are two selections in the group, it displays them with 
        " or " between.
    """
#TODO make it handle the or thing

    def __init__(self, scr, selections):
        """
        Create a new selection group, where each selection is a (minimally 3x3)
            box with at least one character in it. The box is made visible
            iff its selection is active.

        selections must be passed as a list of tuples of (y, x, text), where
            y and x are the position of the box's top left, and text is the
            string to display within it.
        """
        if len(selections) == 0:
            sys.exit("Bad selection group: {}".format(selections))

        # Store width of this entire selection group
        _, _, selection_strings = zip(*selections)
        self.width = sum(len(s)+2 for s in selection_strings) + 4 #TODO

        self.selections = selections
        self.curr_selection_i = 1

        self.change_selection(scr, curses.KEY_LEFT)

    def get_selection_val(self):
        """
        Return currently selected selection. Index corresponds to the same
            items that were passed into init.
        """
        return self.curr_selection_i

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
            _clear_box(scr, old_sel[0], old_sel[1], 3, old_sel_w)

            if keypress == curses.KEY_LEFT:
                self.curr_selection_i -= 1
                self.curr_selection_i %= len(self.selections)
            elif keypress == curses.KEY_RIGHT:
                self.curr_selection_i += 1
                self.curr_selection_i %= len(self.selections)

            # Setup new selection
            new_sel = self.selections[self.curr_selection_i]
            new_sel_w = len(new_sel[2])+2
            _draw_box(scr, new_sel[0], new_sel[1], 3, new_sel_w)

