# -*- coding: utf-8 -*-
import wlp_parser

def mkdict(infile):
    dict = {}

    with open(infile, 'r') as __current_file:
        tree = wlp_parser.parser.parse(
            wlp_parser.lexer.lex(__current_file.read()))

        for subtree in tree:
            current_key = subtree[0].getstr().strip('<>')
            if current_key not in dict:
                dict[current_key] = {}

            for key, value in subtree[1]:
                key = key.getstr()
                value = value.getstr().strip("'\"")
                dict[current_key][key] = value

    return dict
