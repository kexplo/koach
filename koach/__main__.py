# -*- coding: utf-8 -*-

from __future__ import absolute_import

import bisect
import re
import sys

import click

from .query import query


__all__ = ['cli']


def find_all(substr, string):
    """
    >>> find_all('b', 'aaaabbccddeeefffbdde')
    [4, 5, 16]
    """
    return [i.start() for i in re.finditer(substr, string)]


def calc_line_col(index, line_info):
    """
    >>> calc_line_col(10, [10, 26])
    (1, 11)
    >>> calc_line_col(11, [10, 26])
    (2, 1)
    """
    line = bisect.bisect_left(line_info, index) + 1
    if line == 1:
        return 1, index + 1
    line_start_index = line_info[line - 2]
    col = index - line_start_index
    return line, col


def calc_line_col_from_string(substr, string, start=0, line_info=None):
    u"""
    >>> calc_line_col_from_string('0', '1234567890\\nabcdefghijklmno\\np')
    (1, 10)
    >>> calc_line_col_from_string('a', '1234567890\\nabcdefghijklmno\\np')
    (2, 1)
    >>> calc_line_col_from_string('hello', 'first line\\nabchello, world\\nz')
    (2, 4)
    >>> calc_line_col_from_string(u'집회', \
                                  u'대한민국헌법 제2장 국민의 권리와 의무\\n' \
                                  u'제21조\\n' \
                                  u'제1항 모든 국민은 언론·출판의 자유와 ' \
                                  u'집회·결사의 자유를 가진다.')
    (3, 23)
    """
    if line_info is None:
        line_info = find_all('\n', string)
    index = string.find(substr, start)
    return calc_line_col(index, line_info)


def get_line_substring(string, line, line_info=None):
    u"""
    line: 1-based index.
    >>> print get_line_substring(u'대한민국헌법 제1장 총강\\n제1조\\n' \
                                 u'제1항 대한민국은 민주공화국이다.\\n' \
                                 u'제2항 대한민국의 주권은 국민에게 있고, ' \
                                 u'모든 권력은 국민으로부터 나온다.', 3)
    제1항 대한민국은 민주공화국이다.

    """
    if line_info is None:
        line_info = find_all('\n', string)
    if not line_info:
        return string
    if line == 1:
        start_index = 0
    else:
        start_index = line_info[line - 2] + 1
    try:
        end_index = line_info[line - 1]
    except IndexError:
        return string[start_index:]
    return string[start_index:end_index]


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

    line_info = find_all('\n', text)
    next_index = 0
    for correct in corrects:
        index = text.find(correct['word'], next_index)
        if index == -1:
            click.echo(u'can not found {0}', file=sys.stderr)
            continue
        next_index = index + len(correct['word'])
        line, col = calc_line_col(index, line_info)
        line_col_text = click.style('line {0} col {1}:'.format(line, col),
                                    fg='cyan')
        substr_line = get_line_substring(text, line, line_info)
        click.echo(u'{0} {1}'.format(line_col_text,
                                     apply_color(substr_line, [correct])))
        colored_wrong_word = click.style(correct['word'], fg='red')
        colored_fixed_word = ', '.join(
            click.style(w, fg='green') for w in correct['replaces'])
        click.echo(u'{0} -> {1}'.format(colored_wrong_word,
                                        colored_fixed_word))
        click.echo(correct['help'] + '\n')


@click.command()
@click.argument('file', type=click.File('r', encoding='utf-8'), default='-')
def cli(file):
    """부산대 한국어 문법 검사기( http://speller.cs.pusan.ac.kr/ )에 의존하는
    CLI 한국어 문법 검사기.
    FILE을 읽어서 부산대 한국어 문법 검사기의 결과를 표시합니다."""
    data = file.read()
    if not data:
        return
    display(data, query(data))


if __name__ == '__main__':
    cli()
