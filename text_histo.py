# text_histo.py

import string
from itertools import islice

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

def process_file(filename):
    hist = dict()
    fp = open(filename, encoding='utf-8')
    for line in fp:
        process_line(line, hist)
    return hist

def process_line(line, hist):
    line = line.replace('-', ' ')
    for word in line.split():
        word = word.strip(string.punctuation + string.whitespace)
        word = word.lower()
        hist[word] = hist.get(word, 0) + 1

def total_words(hist):
    return sum(hist.values())

def different_words(hist):
    return len(hist)

def most_common(hist):
    t = []
    for key, value in hist.items():
        t.append((value, key))
        t.sort(reverse=True)
    return t

def print_most_common(hist, num=10):
    t = most_common(hist)
    print(f'The most common {num} words are:')
    for freq, word in t[:num]:
        print(word, freq, sep='\t')

hist = process_file('emma.txt')
n_items = take(5, hist.items())
print(n_items)
print('Total number of words:', total_words(hist))
print('Number of different words:', different_words(hist))
print_most_common(hist)
print_most_common(hist, 20)