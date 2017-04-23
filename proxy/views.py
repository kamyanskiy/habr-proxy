# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from bs4 import BeautifulSoup, NavigableString

from django.http import HttpResponse


site = 'https://habrahabr.ru'
local_site = 'http://localhost:8000'
INJECTED_CHARACTER = u'™'


def index(request):
    remote_response = requests.get(site+request.path)
    response = HttpResponse(content=modify_content(remote_response.content))
    response.status_code = remote_response.status_code
    return response


def modify_content(content):
    soup = BeautifulSoup(content, "html.parser")
    if soup:
        modify_text_in_query(soup.find_all(class_='post__title'))
        modify_text_in_query(soup.find_all(class_='post__title_link'))
        modify_text_in_query(soup.find_all(class_='content html_format'))
        replace_nav_links(soup.find_all('a'))
        replace_nav_links(soup.find_all('link'))
    return str(soup)


def modify_text_in_query(query):
    for item in query:
        if len(item.contents) > 0:
            new_item_contents = []
            for citem in item.contents:
                if (isinstance(citem, NavigableString) and \
                                len(citem.split()) > 6):
                    citem = modify_string(citem)

                if citem.name in ('p', 'span') and len(citem.text.split()) > 6:
                    citem.string = modify_string(citem.text)
                new_item_contents.append(citem)
            item.contents = new_item_contents


def replace_nav_links(query):
    for item in query:
        try:
            if hasattr(item, 'href') and item['href'].startswith(site):
                item['href'] = item['href'].replace(site, local_site)
        except KeyError:
            pass


def modify_string(citem, injected_character=INJECTED_CHARACTER):
    processed = []
    for i, w in enumerate(citem.split()):
        if i % 6 == 0:
            w = w + injected_character
        processed.append(w)
    string_with_injected = ' '.join(processed)
    return NavigableString(string_with_injected)
