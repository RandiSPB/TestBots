import nltk
import os


class NaturalLanguageProcessor:
    def __init__(self, lang='russian', download_data='punkt'):
        nltk.download(download_data)
        self.lang = lang

    def simple_process(self, word_base_ref, text):
        words = list(nltk.word_tokenize(text.lower(), self.lang))
        print(words)
        if 'о' in words:
            tmp_index_data = words.index('о')
            new_word = words[tmp_index_data] + ' ' + words[tmp_index_data + 1]
            words.pop(tmp_index_data)
            words.pop(tmp_index_data)
            words.insert(tmp_index_data, new_word)
        print(words)
        for word in words:
            if word in word_base_ref.keys():
                word_base_ref[word] += 1
                break
