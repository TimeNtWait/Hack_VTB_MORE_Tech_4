#!/usr/bin/env python3
# coding: utf-8

import trend_functions



def main():
    stoplist=["банк","организация", "россия", "год", "сообщить", "господин", "г.", "-"]
    feeds = trend_functions.parse_feeds()
    tred_words, df_nouns = trend_functions.get_trend_words(feeds)
    heads_dict = trend_functions.get_trends(tred_words, stoplist, df_nouns)
    return heads_dict


if __name__ == "__main__":
    heads_dict=main()
    print(heads_dict)