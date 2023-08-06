from collections import Counter

def count_in_list(l, word):
    c = Counter(l)
    #print("Hello")
    return c[word]


