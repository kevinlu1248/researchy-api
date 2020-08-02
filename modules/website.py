import copy
import time

import requests
import spacy
import spacy_readability
from bs4 import BeautifulSoup
from readability import Document

from .paragraph import Paragraph
from .utils import cached_property
from .utils import indirectly_cached_property

tmp = 0
start_ = time.time()


def start():
    global start_
    start_ = time.time()


def end(s=""):
    global start_
    print(s + str(time.time() - start_))
    return time.time() - start_


class Website:
    # nlp = spacy.load("en_ner_bionlp13cg_md")
    reading_nlp = spacy.load("en_core_web_sm")
    reading_nlp.add_pipe(reading_nlp.create_pipe("sentencizer"))
    reading_nlp.add_pipe(spacy_readability.Readability())

    # pattern = \
    # re.compile('((http|ftp|https)://)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,10}([-a-zA-Z0-9@:%_\+.~#?&//=]*)')

    def __init__(self, url=None, raw_html=None, use_vocab=True):
        if url is None and raw_html is None:
            raise AttributeError("Please initiate with either a URL or HTML file.")
        if url is not None:
            self.__url = url
        if raw_html is not None:
            self.__raw_html = raw_html
        self.use_vocab = use_vocab

    def init_readability(self):
        # find a faster library
        doc = Website.reading_nlp(
            self.web_text, disable=["tokenizer", "tagger", "parser", "ner"]
        )
        self.__grade_level = doc._.flesch_kincaid_grade_level
        self.__reading_ease = doc._.flesch_kincaid_reading_ease
        self.__word_count = len(doc)
        for token in doc:
            if not token.text.isalnum():
                self.__word_count -= 1

    @staticmethod
    def extract_html_tags(s):
        ret = []
        for match in Website.html_tag_pattern.finditer(s):
            start, end, tag = match.start(), match.end(), match[0]
            ret.append({"start": start, "end": end, "tag": tag})
            s = "".join((s[:start], " " * (end - start), s[end:]))
        return s, ret

    @staticmethod
    def get_entities_from_text(s):
        doc = Website.nlp(s)
        return [
            {"name": ent.label_, "start": ent.start_char, "end": ent.end_char}
            for ent in doc.ents
        ]

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
                s, "</{}>".format(ent["name"].lower()), ent["end"]
            )
            s = Website.__insert_helper(
                s, "<{}>".format(ent["name"].lower()), ent["start"]
            )
        return s

    @indirectly_cached_property
    def url(self):
        raise AttributeError("No URL found")

    @cached_property
    def raw_html(self):
        # print(hasattr(self, "_Website__raw_html"))
        return requests.get(self.url).text

    @property
    def reader_html(self):
        return Document(self.raw_html)  # kill ads

    @cached_property
    def tree(self):
        return BeautifulSoup(self.reader_html.summary(), "lxml")

    @cached_property
    def display(self):
        display_output = copy.copy(self.tree)
        head = display_output.new_tag("head")
        title = display_output.new_tag("title")
        title.string = self.reader_html.title()
        head.append(title)
        display_output.body.insert_before(head)

        body_title = self.tree.new_tag("h1")
        body_title.string = self.reader_html.title()
        next(display_output.body.children).insert_before(body_title)
        return display_output

    @cached_property
    def links(self):
        rlinks = set()
        for link in self.raw_tree.find_all("a"):
            # fix
            href = link.get("href")
            if not href or href == "#":
                continue
            if href[0] == "/":
                href = self.url + href
            if (
                not href.startswith("http://")
                or href.startswith("http://")
                or href.startswith("ftp://")
            ):
                href = self.url + "/" + href
            rlinks.add(href)
        return rlinks

    @cached_property
    def web_text(self):
        return " ".join(
            filter(
                lambda s: len(s) > 300,
                map(lambda p: p.get_text(), self.display.find_all("p")),
            )
        )

    @indirectly_cached_property
    def grade_level(self):
        self.init_readability()

    @indirectly_cached_property
    def reading_ease(self):
        self.init_readability()

    @indirectly_cached_property
    def word_count(self):
        self.init_readability()

    @cached_property
    def annotated_tree(self):
        #             start() 13ms
        annotated_tree_answer = copy.copy(self.display)
        if self.use_vocab:
            # 691ms TODO SPEED UP
            vocab = Paragraph(self.web_text).key_terms
        else:
            vocab = []
        paragraphs = []
        tags = annotated_tree_answer.find_all("p")
        for tag in tags:
            s = tag.encode_contents().decode("utf8")
            if len(s) <= 300:
                continue
            paragraphs.append(Paragraph(s).spaced_raw_text)
        tags = filter(lambda tag: len(tag.encode_contents().decode("utf8")) > 300, tags)
        docs = list(
            Website.reading_nlp.pipe(paragraphs, disable=["tagger", "parser"])
        )  # parallelize?
        for tag, spaced_raw_text, doc in zip(tags, paragraphs, docs):
            s = tag.encode_contents().decode("utf8")
            # TODO: make asynchronous
            new_string = "<annotated>{}</annotated>".format(
                Paragraph(
                    s, vocab=vocab, raw_ents=doc.ents, spaced_raw_text=spaced_raw_text,
                ).annotated_with_entities
            )  # 410ms TODO SPEED UP
            tag.string = ""
            tag.replace_with(BeautifulSoup(new_string, "lxml-xml"))
        return annotated_tree_answer

    @property
    def description(self):
        return {
            "annotated_tree": str(self.annotated_tree),
            "word_count": self.word_count,
            "reading_ease": self.reading_ease,
            "grade_level": self.grade_level,
        }

    def __str__(self):
        return "<Website object with url {}>".format(self.url)


if __name__ == "__main__":
    with open("index.html", "r") as f:
        site = Website(
            url="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1994795/",
            raw_html=f.read(),
        )
#     start()
#     print(site.description)
#     end()
#     print(site.)
