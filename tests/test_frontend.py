# -*- coding: utf-8 -*-

import click
from click.testing import CliRunner
from koach.__main__ import apply_color, cli, display as _display


def test_apply_color():
    corrects = [
        {'word': u'검정'},
        {'word': u'빨강'},
    ]
    colored_text = apply_color(u'노랑 초록 빨강 파랑', corrects)
    assert colored_text == \
        u'노랑 초록 {0} 파랑'.format(click.style(u'빨강', fg='red'))


def test_display_empty(monkeypatch):
    monkeypatch.setattr('koach.__main__.display', lambda x, _: _display(x, []))
    runner = CliRunner()
    result = runner.invoke(cli, input=u'반짝이 운1동복 갖고 싶다.')
    assert not result.exception
    assert result.output == u'no error was found\n'


def test_display(monkeypatch):
    text = u'저한테는 이 사람이 김태희고 전도연입니다. ' \
        u'제가, 길라임씨 열렬한 팬이거든요.\n' \
        u'이게 최선입니까? 확실해요?\n' \
        u'길라임 씨는 언제부터 그렇게 예뻤나? 작년부터?\n' \
        u'김수한무 거북이와 두루미 삼천갑자 동방삭 치치카포 사리사리센타 ' \
        u'워리워리 세브리깡 무두셀라 구름이 허리케인에 담벼락 담벼락에 ' \
        u'서생원 서생원에 고양이 고양이엔 바둑이 바둑이는 돌돌이'

    fake_corrects = [
        {
            'word': u'길라임씨',
            'help': u'가명 길라임',
            'replaces': [u'ㄱㄹㅇㅆ', u'ㅇㅇㅇㅇ']
        },
        {
            'word': u'최선입니까?',
            'help': u'최선을 다하지 않았네요. 다시 해오세요.',
            'replaces': [u'ㅊㅅㅇㄴㄲ?']
        }]

    correct_result = u'{0} 저한테는 이 사람이 김태희고 전도연입니다. ' \
        u'제가, {1} 열렬한 팬이거든요.\n' \
        u'{1} -> {2}, {3}\n' \
        u'가명 길라임\n\n' \
        u'{4} 이게 {5} 확실해요?\n' \
        u'{5} -> {6}\n' \
        u'최선을 다하지 않았네요. 다시 해오세요.\n\n' \
        u''.format(click.style(u'line 1 col 29:', fg='cyan'),
                   click.style(u'길라임씨', fg='red'),
                   click.style(u'ㄱㄹㅇㅆ', fg='green'),
                   click.style(u'ㅇㅇㅇㅇ', fg='green'),
                   click.style(u'line 2 col 4:', fg='cyan'),
                   click.style(u'최선입니까?', fg='red'),
                   click.style(u'ㅊㅅㅇㄴㄲ?', fg='green'))

    monkeypatch.setattr('koach.__main__.display',
                        lambda x, _: _display(x, fake_corrects))
    runner = CliRunner()
    result = runner.invoke(cli, input=text, color=True)
    assert not result.exception
    assert result.output == correct_result
