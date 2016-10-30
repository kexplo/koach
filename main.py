# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from bs4 import BeautifulSoup
from colorama import Fore
import requests


URL = 'http://speller.cs.pusan.ac.kr/PnuSpellerISAPI_201602/lib/check.asp'
NEXT_URL = 'http://speller.cs.pusan.ac.kr/PnuSpellerISAPI_201602/lib/' \
    'checkNext.asp'


def select_first(soup, selector):
    elements = soup.select(selector)
    if elements:
        return elements[0]
    return None


def single_query(input_text, page_number=1):
    data = {}
    query_url = URL
    if page_number > 1:
        data['text2'] = input_text
        query_url = NEXT_URL
    else:
        data['text1'] = input_text

    r = requests.post(query_url, data=data)

    soup = BeautifulSoup(r.text, 'html.parser')
    next_hunk = select_first(soup, '#bufText2').get('value')

    if u'문법 및 철자 오류가 발견되지 않았습니다.' in r.text:
        return [], next_hunk

    hidden_input_str = select_first(soup, 'input#bufHiddenInputStr')
    if hidden_input_str is None or not hidden_input_str.get('value'):
        raise Exception('Failed to post. maybe blocked')

    correct_tables = soup.select('#correctionTable > * table.tableErrCorrect')
    corrects = []
    for correct_table in correct_tables:
        # tableErr_2 -> 2
        correct_id = correct_table.get('id').split('_')[1]
        word_td = select_first(correct_table, '#tdErrorWord_%s' % correct_id)
        replace_td = select_first(correct_table,
                                  '#tdReplaceWord_%s' % correct_id)
        help_td = select_first(correct_table, '#tdHelp_%s' % correct_id)
        corrects.append({'word': word_td.string.replace('\xa0', ' '),
                         'replaces': list(replace_td.strings),
                         'help': '\n'.join(list(help_td.strings))})
    return corrects, next_hunk


def query(input_text):
    corrects = []
    page_number = 1
    while True:
        # print 'query', page_number, input_text
        result, next_hunk = single_query(input_text, page_number)
        if result:
            corrects += result
        if next_hunk.strip():
            input_text = next_hunk
            page_number += 1
            continue
        break
    return corrects


def wrap_fore_color(text, clr):
    return clr + text + Fore.RESET


def fore_red(text):
    return wrap_fore_color(text, Fore.RED)


def fore_green(text):
    return wrap_fore_color(text, Fore.GREEN)


def fore_cyan(text):
    return wrap_fore_color(text, Fore.CYAN)


def apply_color(text, corrects):
    next_index = 0
    for correct in corrects:
        find_index = text.find(correct['word'], next_index)
        if find_index == -1:
            continue
        len_word = len(correct['word'])
        colored_word = fore_red(correct['word'])
        text = text[:find_index] + colored_word + text[find_index+len_word:]
        next_index = find_index + len(colored_word)
    return text


def display(text, corrects):
    if not corrects:
        print 'no error was found'

    def next_line(text):
        line_number = 1
        for line in text.split('\n'):
            yield (line, line_number)
            line_number += 1
    line_gen = next_line(text)
    line, line_number = next(line_gen)
    next_index = 0
    for correct in corrects:
        while True:
            index = line.find(correct['word'], next_index)
            if index == -1:
                line, line_number = next(line_gen)
                next_index = 0
                continue
            next_index = index + len(correct['word'])
            line_col_text = fore_cyan('line {0} col {1}:'.format(line_number,
                                                                 index))
            print '{0} {1}'.format(line_col_text,
                                   apply_color(line, [correct]))
            colored_wrong_word = fore_red(correct['word'])
            colored_fixed_word = ', '.join(
                fore_green(w) for w in correct['replaces'])
            print '{0} -> {1}'.format(colored_wrong_word, colored_fixed_word)
            print correct['help'] + '\n'
            break


if __name__ == '__main__':
    test_data = '한국어 맞춤법/문법 검사기 는 부산대학교 인공지 능연구실과 ' \
        '(주)나라 인포테크가 함께 만들고 있습니다.\n' \
        '이 검사 기는 개인이나 학 생만 무 료로  사용할 수 있습니다.'
    corrects = query(test_data)
    display(test_data, corrects)
