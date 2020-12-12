import json
import sys
from collections import defaultdict

"""
This program parses an (English) dictionary from a json file, and gives a
    list of anagrams that can be found from words containing only the
    given characters, where the first given character can be found in every
    word.

An anagram is "a word or phrase made by transposing the letters of another word
    or phrase." (https://www.merriam-webster.com/dictionary/anagram)

This program's results include words with removed letters (not only 
    transposed). 
"""


def get_anagrams(dict_file, chars):
    """
    Return a list of words as described at the top of this file.
    """

    if not chars.isalpha():
        print("You didn't only enter characters and now I must die")
        exit()

    words = _load_words(dict_file)

    if not words:
        print("No words found in given dictionary file.")
        exit()

    # Store all words in dictionary as {"sorted letters": [matching words]} pairs.
    word_dict = defaultdict(list)  # dict of [sorted letters in word]: word
    for word in words:
        word_dict["".join(sorted(word))].append(word)

    results = list()

    # Results are stored in a list of lists where each inner list stores words
    #   containing exactly the same characters (in different orders)
    for c, w in word_dict.items():
        if chars[0] in c and set(c).issubset(set(chars)):
            results.append(w)

    # Flatten list
    results = [x for l in results for x in l]
    return results


def _load_words(filename):
    """
    Parse and return the contents of a dictionary file in json format
    """
    try:
        with open(filename) as word_file:
            valid_words = set(json.loads(word_file.read()))
            return valid_words
    except IOError:
        print("Could not open file '{}'.".format(filename))
        exit()


def main():
    if len(sys.argv) != 3:
        print("Bad arguments. Usage: {} <dict file> <chars>\n".format(sys.argv[0]))
        exit()

    results = get_anagrams(sys.argv[1], sys.argv[2])
    print("found {} words: \n{}".format(len(results), results))


if __name__ == "__main__":
    main()
