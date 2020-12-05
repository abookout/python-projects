## Prefixer
Prefixer is a little program that looks through all the words in a dictionary text file (json formatted), matches some predefined prefixes to those words, and swaps them with another prefix that should make sense for the word.

This project was made hoping for some funny results, but it was likely a combination of a dictionary with way too many words that I've never heard before, as well as a poor choice of prefix swapping pairs, that made good results sparse. The best one I've gotten so far was "bigonometry", from "trigonometry" with the prefix swap pair of "bi" and "tri".

[Here's the dictionary I used](https://github.com/dwyl/english-words/blob/master/words_dictionary.json) (not included in this repo); it's not perfect but it works for the purpose of this project.

## Printlines
Also included in this repo is a program I put together to randomly choose and display a given number of lines from a file. 

## To Use

First run prefixer with "python3 prefixer.py <json_dict>", and then "python3 printlines.py output.txt <num lines>" to get some maybe funny words in your stdout. Run the printlines.py program again to get some other maybe funny words. Repeat as necessary.

Note: when run, prefixer overwrites a file named "output.txt" in the same directory.
