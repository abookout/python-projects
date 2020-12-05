import json
import sys

"""
The purpose of this program is to generate new English words by switching 
	prefixes with their opposites (e.g. prepare -> postpare).
"""

pairs = (
        ('anti','pro'),
        ('pre', 'post'),
        ('over', 'under'),
        ('up', 'down'),
        #('by', 'un'),
        ('fore', 'hind'),
        ('off', 'on'),
        ('un', 're'),
        ('co', 'with'),
        ('back', 'front'),
        ('bi', 'tri'),
        ('uni', 'bi'),
        ('uni', 'tri'),
        ('inter', 'extra'),
        ('hetero', 'homo'),
        ('proto', 'ultra'),
        ('uni', 'poly'),
        ('uni', 'omni'),
        ('neo', 'paleo'),
        ('mono', 'multi'),
        ('non', 'omni'),
        ('pro', 'con'),
        ('hypo', 'hyper'),
        ('phobic', 'phyllic'),
        ('macro', 'micro'),
        ('micro', 'mega'),
        ('iso', 'hetero'),
        ('crypto', 'pan'),
        #('a', 'ambi'),
        ('ante', 'post'),
        ('proto', 'deuter'),
        ('ex', 'em'),
        ('ex', 'el'),
        ('hyper', 'infra'),
        ('mega', 'milli'),
)

prefixes = [x for y in pairs for x in y]

def load_words():
    try:
        with open(sys.argv[1]) as word_file:
            words = json.load(word_file)
            return words
    except: 
        print("Error: could not open file '{}'.".format(sys.argv[1]))


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 prefixer.py <json_dict>")
        return

    # get list of english words
    allwords = load_words()

    # get list of english words with one of the listed prefixes,
    #   store in sets of (word, prefix)
    print("getting list of applicable words")
    words = dict()
    for w in allwords:
        for p in prefixes:
            if w.startswith(p) and not w == p:
                words[w] = p

    # swap the prefix
    print("swapping prefixes")
    newwords = list()
    for w, p in words.items():
        pair = findpair(p)
        newword = swapprefix(w, pair)
        # don't add any actual words. that's boring.
        if newword not in words:
            newwords.append((newword, w, pair))

        
    print("Found {} words with prefixes.".format(len(newwords)))

    # write words to file
    print("writing words to file")
    with open("output.txt", "w") as f:
        for i in newwords:
            nw, w, (a, b) = i
            f.write("{}: from {} ({},{})\n".format(nw, w, a, b))
    print("DONE!")


def findpair(prefix):
    # get the specified prefix pair from pairs
    for pair in pairs:
        a,b = pair
        if prefix == a or prefix == b:
            return pair
    return None


def swapprefix(word, pair):
    # return word with its prefix swapped according to the given prefix pair
    newword = word
    a,b = pair
    if word.startswith(a):
        newword = word.replace(a, b, 1)
    elif word.startswith(b):
        newword = word.replace(b, a, 1)
    else:
        newword = None

    return newword


if __name__ == '__main__':
    main()





