#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: wikiseriesbaslib.py
#
# Copyright 2023 Bas van Kesteren
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for wikiseriesbaslib.

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

import logging
import requests
from bs4 import BeautifulSoup as Bfs


__author__ = '''Bas van Kesteren <bvkdummy@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''25-05-2023'''
__copyright__ = '''Copyright 2023, Bas van Kesteren'''
__credits__ = ["Bas van Kesteren"]
__license__ = '''MIT'''
__maintainer__ = '''Bas van Kesteren'''
__email__ = '''<bvkdummy@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging
LOGGER_BASENAME = '''wikiseriesbaslib'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def search_series(name):
    api_url = 'https://en.wikipedia.org/w/api.php'
    limit = 10
    term = f'List_of_{name}_episodes'
    parameters = {'action': 'opensearch',
                  'format': 'json',
                  'formatversion': '1',
                  'namespace': '0',
                  'limit': limit,
                  'search': term}
    search_response = requests.get(api_url, params=parameters, timeout=300)
    series_url = search_response.json()[3][0]
    series_response = requests.get(series_url, timeout=300)
    soup = Bfs(series_response.text, features="html.parser")
    season_table = soup.find('table', class_='wikitable')
    seasons_numbers = [item.text for item in season_table.find_all('span', class_='nowrap')]
    season_episodes = soup.find_all('table', class_='wikiepisodetable')
    return {f'Season {key}': [entry.text.split('"')[1]
                              for entry in value.find_all('td', class_='summary')]
            for key, value in zip(seasons_numbers, season_episodes)}
