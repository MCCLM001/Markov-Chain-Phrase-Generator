"""
This script implements a markov chain sentence generater. Specifically, it asks the user for a URL, scrapes the text from the URL, and then builds a markov chain to model the "style" of that text. Finally, it generates a series of 10 sentences in the "style" of that text. 

To try out this script, press the green "Run" button above and follow the instructions.

References: 
- https://www.codingame.com/playgrounds/41655/how-to-build-a-chatbot-in-less-than-50-lines-of-code
- https://www.geeksforgeeks.org/how-to-scrape-paragraphs-using-python/
"""

import random, re
import requests
from bs4 import BeautifulSoup
import string
import os
from collections import defaultdict

MIN_FILE_SIZE = 5000


class LString:
    def __init__(self):
        self._total = 0
        self._successors = defaultdict(int)

    def put(self, word):
        self._successors[word] += 1
        self._total += 1

    def get_random(self):
        ran = random.randint(0, self._total - 1)
        for key, value in self._successors.items():
            if ran < value:
                return key
            else:
                ran -= value


couple_words = defaultdict(LString)


def load(phrases):
    with open(phrases, 'r') as f:
        for line in f:
            if any(c.isalpha() for c in line):
                add_message(line)


def add_message(message):
    message = re.sub(r'[^\w\s\']', '', message).lower().strip()
    words = message.split()
    for i in range(2, len(words)):
        couple_words[(words[i - 2], words[i - 1])].put(words[i])
    couple_words[(words[-2], words[-1])].put("")


def generate():
    result = []
    while len(result) < 10 or len(result) > 20:
        result = []
        s = random.choice(list(couple_words.keys()))
        result.extend(s)
        while result[-1]:
            w = couple_words[(result[-2], result[-1])].get_random()
            result.append(w)

    return " ".join(result)


def clean_string(raw_string):
    """
  Wikipedia articles often have in-line references, which will be
  processed as a word followed by a number by this model (eg. common106).
  We want to remove the numbers in these occurrances.
  """
    words = []
    for word in raw_string.split(' '):
        if len(word) and word[0].isalpha() and word[-1].isdigit():
            clean_word = word.rstrip(string.digits)
            words.append(clean_word)
        else:
            words.append(word)
    return " ".join(words)


# this is the main function
if __name__ == "__main__":
    print("Hello! Welcome to my Markov Chain Sentence Generater.\n\n"
          "You will be asked to enter a URL, and this script will"
          " generate 10 phrases in the style of the text from"
          " that URL. Or, you can press enter and this script will"
          " use a default Wikipedia article about pandas.\n")

    response = None

    while response is None:
        link = input("Please enter a URL (or press enter for default): ")
        if not link:
            link = "https://en.wikipedia.org/wiki/Giant_panda"
        if link[:8] != "https://":
            link = "https://" + link

        try:
            response = requests.get(link)
        except Exception:
            print("Invalid URL. Please try again.\n")

        htmldata = response.text

        soup = BeautifulSoup(htmldata, 'html.parser')
        data = ''
        with open('sentences.txt', 'w') as f:
            for data in soup.find_all("p"):
                text = data.get_text()
                if (any(c.isalnum() for c in text)):
                    f.write(data.get_text())

        if os.path.getsize("sentences.txt") < MIN_FILE_SIZE:
            print("The URL you gave doesn't contain much text."
                  " Please enter a URL with more text.\n")
            response = None

    print(f"\nPrinting 10 phrases in the style of \"{link}\"...\n")
    load("sentences.txt")
    for i in range(10):
        print(f"Phrase {i+1}:")
        raw_string = generate()
        print(clean_string(raw_string))
        print()
