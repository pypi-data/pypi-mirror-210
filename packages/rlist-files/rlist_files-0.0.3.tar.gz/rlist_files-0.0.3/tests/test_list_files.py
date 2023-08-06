#!/usr/bin/env python

"""Tests for `list_files` package."""

import pytest


from list_files import list_files


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


# import timeit
# def test_list_files(func, pattern):
#   a=timeit.timeit(lambda: func(pattern=pattern, recursive=True), number=100)
#   b=timeit.timeit(lambda: func(pattern=pattern, recursive=False), number=100)
#   c=timeit.timeit(lambda: func(pattern=pattern, recursive=True, ignore_case=True), number=100)
#   d=timeit.timeit(lambda: func(pattern=pattern, recursive=False, ignore_case=True), number=100)
#   e=timeit.timeit(lambda: func(pattern=pattern, recursive=True, full_names=True), number=100)
#   f=timeit.timeit(lambda: func(pattern=pattern, recursive=False, full_names=True), number=100)
#   return [a, b, c, d, e, f]
# # the differences are negligible 
# fast = test_list_files(list_files_fast, pattern="l$")
# slow = test_list_files(list_files, pattern="l$")
