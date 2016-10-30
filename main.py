# -*- coding: utf-8 -*-

from __future__ import absolute_import

import click

from query import query


def apply_color(text, corrects):
    next_index = 0
    for correct in corrects:
        find_index = text.find(correct['word'], next_index)
        if find_index == -1:
            continue
        len_word = len(correct['word'])
        colored_word = click.style(correct['word'], fg='red')
        text = text[:find_index] + colored_word + text[find_index+len_word:]
        next_index = find_index + len(colored_word)
    return text


def display(text, corrects):
    if not corrects:
        click.echo(u'no error was found')

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
            line_col_text = click.style('line {0} col {1}:'
                                        ''.format(line_number, index),
                                        fg='cyan')
            click.echo(u'{0} {1}'.format(line_col_text,
                                         apply_color(line, [correct])))
            colored_wrong_word = click.style(correct['word'], fg='red')
            colored_fixed_word = ', '.join(
                click.style(w, fg='green') for w in correct['replaces'])
            click.echo(u'{0} -> {1}'.format(colored_wrong_word,
                                            colored_fixed_word))
            click.echo(correct['help'] + '\n')
            break


if __name__ == '__main__':
    test_data = '한국어 맞춤법/문법 검사기 는 부산대학교 인공지 능연구실과 ' \
        '(주)나라 인포테크가 함께 만들고 있습니다.\n' \
        '이 검사 기는 개인이나 학 생만 무 료로  사용할 수 있습니다.'
    corrects = query(test_data)
    display(test_data, corrects)
