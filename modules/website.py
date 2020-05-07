import requests
import re
import spacy
import copy
from lxml import etree
from readability import Document
from bs4 import BeautifulSoup
from paragraph import Paragraph
import time


class Website:

    # use Literata
    nlp = spacy.load("en_core_web_sm")
    # pattern =
    # re.compile('((http|ftp|https)://)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,10}([-a-zA-Z0-9@:%_\+.~#?&//=]*)')

    def __init__(self, url=None, raw_html=None):
        if url is None and raw_html is None:
            raise AttributeError(
                "Please initiate with either a URL or HTML file.")
        if url is not None:
            self.__url = url
        if raw_html is not None:
            self.__raw_html = raw_html

    def __insert_helper(haystack, needle, index):
        return haystack[:index] + needle + haystack[index:]

    def __get_overlap(a, b):
        '''Elements from b that are overlapping will be deleted. Assume a and b are sorted lists of tuples.'''
        res, i, j = [], 0, 0
        while i < len(a) and j < len(b):
            if a[i]['end'] <= b[j]['end']:
                if a[i]['end'] >= b[j]['start']:
                    res.append(j)
                i += 1
                continue
            elif a[i]['end'] >= b[j]['end']:
                if a[i]['start'] <= b[j]['end']:
                    res.append(j)
                j += 1
                continue
        return list(set(res))

    @staticmethod
    def extract_html_tags(s):
        ret = []
        for match in Website.html_tag_pattern.finditer(s):
            start, end, tag = match.start(), match.end(), match[0]
            ret.append({
                "start": start,
                "end": end,
                "tag": tag
            })
            s = "".join((s[:start], " " * (end - start), s[end:]))
        return s, ret

    @staticmethod
    def get_entities_from_text(s):
        doc = Website.nlp(s)
        return [{
            "name": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char
        } for ent in doc.ents]

    @staticmethod
    def get_annotated_entities(s):
        #         print(s)
        new_s, tags = Website.extract_html_tags(s)
        ents = Website.get_entities_from_text(new_s)
        for overlap in Website.__get_overlap(tags, ents)[::-1]:
            ents.pop(overlap)
#         print(Website.get_entities_from_text(new_s)[::-1])
        for ent in ents[::-1]:
            s = Website.__insert_helper(
                s, "</{}>".format(ent['name'].lower()), ent['end'])
            s = Website.__insert_helper(
                s, "<{}>".format(
                    ent['name'].lower()), ent['start'])
        return s

    @property
    def url(self):
        if not hasattr(self, '_Website__url'):
            raise AttributeError("No URL found")
        return self.__url

    @property
    def raw_html(self):
        if not hasattr(self, '_Website__raw_html'):
            response = requests.get(self.url)
            self.__raw_html = response.text
        return self.__raw_html

    @property
    def reader_html(self):
        if not hasattr(self, '_Website__reader_html'):
            self.__reader_html = Document(self.raw_html)  # kill ads
        return self.__reader_html

    @property
    def tree(self):
        if not hasattr(self, '_Website__tree'):
            self.__tree = BeautifulSoup(self.reader_html.summary(), 'lxml')
        return self.__tree

    @property
    def display(self):
        if not hasattr(self, "_Website__display"):
            self.__display = copy.copy(self.tree)
            head = self.__display.new_tag('head')
            title = self.__display.new_tag('title')
            title.string = self.reader_html.title()
            head.append(title)
            self.__display.body.insert_before(head)

            body_title = self.tree.new_tag('h1')
            body_title.string = self.reader_html.title()
            next(self.__display.body.children).insert_before(body_title)
        return self.__display

    @property
    def links(self):
        if not hasattr(self, "_Website__links"):
            self.__links = set()
            for link in self.raw_tree.find_all('a'):
                # fix
                href = link.get('href')
                if not href or href == "#":
                    continue
                if href[0] == '/':
                    href = self.url + href
                if not href.startswith(
                        'http://') or href.startswith('http://') or href.startswith('ftp://'):
                    href = self.url + '/' + href
                self.links.add(href)
        return self.__links

    @property
    def word_count(self):
        pass  # TODO: make

    @property
    def annotated_tree(self):
        if not hasattr(self, '_Website__annotated_tree'):
            self.__annotated_tree = copy.copy(self.display)
            web_text = " ".join(filter(lambda s: len(s) > 300, map(lambda p: p.get_text(),
                                                                   self.display.find_all('p'))))
            vocab = Paragraph(web_text).fivefilters_get_terms()['text']
            for tag in self.__annotated_tree.find_all('p'):
                s = tag.encode_contents().decode('utf8')
                if len(s) <= 300:
                    continue
                # TODO: make asynchronous
                new_string = "<annotated>{}</annotated>".format(
                    Paragraph(s, vocab).annotated_with_entities)
                tag.string = ""
                tag.replace_with(BeautifulSoup(new_string, 'lxml-xml'))
#                 print(BeautifulSoup(new_string, 'lxml-xml'))
        return self.__annotated_tree

    def __str__(self):
        return "<Website object with url {}>".format(self.url)


if __name__ == "__main__":
    site = Website("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1994795/")
    # print(list(filter(lambda s: len(s) > 300, map(lambda p: p.get_text(),
    # site.display.find_all('p')))))
    print(site.annotated_tree)
    # web_text = " ".join(map(lambda p: p.get_text(),
    #                         site.display.find_all('p')))
    # vocab = Paragraph(web_text).fivefilters_get_terms()
    # print(vocab)
    # print(list(map(lambda p: p.get_text(), site.display.find_all('p'))))

#     doc = Website.nlp(site.display)
