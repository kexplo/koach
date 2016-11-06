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


@click.command()
@click.argument('input', type=click.File('r', encoding='utf-8'))
def cli(input):
    """부산대 한국어 문법 검사기( http://speller.cs.pusan.ac.kr/ )에 의존하는
    한국어 문법 검사기"""
    data = input.read()
    if not data:
        return
    display(data, query(data))


if __name__ == '__main__':
    cli()
