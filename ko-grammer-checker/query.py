# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from bs4 import BeautifulSoup
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
