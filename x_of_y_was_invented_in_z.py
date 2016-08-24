# coding: utf-8
# pylint: disable=C0103, C0111, C0301

import re
from random import shuffle, choice
from pymorphy2 import MorphAnalyzer
from pymorphy2.units.by_lookup import DictionaryAnalyzer

template = u"{} {} {} {} в {} для расшатывания основ Российской государственности и дестабилизации обстановки в стране."
# TODO: написать настоящее получение списка слов из какого-либо источника, например
#       get_maximum_tweets из twitterbot-utils
text = u"мама захват власть парламента мизандрия феминизм кухня мужчина эмансипация ящера"
places = (u"ФСБ", u"КГБ", u"Украина", u"Россия", u"США")
words = re.sub(u"[^А-Яа-я]", u" ", text, re.UNICODE).split()
words = list(set(words))
m = MorphAnalyzer()


def get_word(pos='NOUN', case='nomn', custom_tags=None, blacklist=None):
    shuffle(words)
    for word in words:
        for p in m.parse(word):
            # skip short words / strange inflections
            if len(p.normal_form) > len(p.word) or len(p.word) < 4:
                continue
            # only dict words to skip AAAAAAAAA
            if not DictionaryAnalyzer in [type(x[0]) for x in p.methods_stack]:
                continue
            # additional filters for second word for example
            if custom_tags:
                if not any(tag in p.tag for tag in custom_tags):
                    continue
            # sometimes where is a strange logic in lookups
            if blacklist:
                if p.normal_form in blacklist:
                    continue
            # assume that we are not going to reuse words
            if p.tag.POS == pos and p.tag.case == case:
                words.remove(word)
                return p

def get_phrase():
    first_word = get_word()
    second_word = get_word(case='gent')
    # get_word(custom_tags=['Geox', 'Abbr'], blacklist=u"того")
    place = m.parse(choice(places))[0].inflect(["loct"])
    
    if not all((first_word, second_word, place)):
        return # maybe we need exception here
    
    grammemes = [first_word.tag.number]
    if 'plur' not in grammemes:
        grammemes.append(first_word.tag.gender)
    
    was = m.parse(u"был")[0].inflect(grammemes)
    invented = m.parse(u"придуман")[0].inflect(grammemes)

    return template.format(first_word.word.capitalize(), second_word.word, was.word, invented.word, place.word)


if __name__ == '__main__':
    print get_phrase().encode('utf-8')
