# -*- coding: utf-8 -*-


from koach.query import query
import pytest


@pytest.mark.parametrize('query_string,expected', [
    (u'검사기 넘나 좋은 것', [{
        'help': u"'너무나'는 '넘나'로 줄여 쓸 수 없습니다.",
        'replaces': [u'너무나 좋은'],
        'word': u'넘나 좋은'
    }]),
    (u'검사기 멋졍', [{
        'help': u'뜻으로 볼 때 바르지 않은 표현입니다.',
        'replaces': [u'먹지요', u'멎지요'],
        'word': u'멋졍'
    }]),
])
def test_busan_univ(query_string, expected):
    assert query(query_string) == expected
