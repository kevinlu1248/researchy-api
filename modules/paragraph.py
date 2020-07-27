# -*- coding: utf-8 -*-

import requests
from copy import deepcopy
import re
import json

import spacy
from pyate import combo_basic

from .utils import cached_property

# from timer import *
# from modules.cvalues import get_c_values

# TODO: make tagged class
# TODO: add get numbers (with plus or minus)


class Paragraph:

    nlp = spacy.load("en_core_web_sm")
    html_tag_pattern = re.compile("</?[^/>][^>]*/?>")
    __fivefilters_url = "http://termextract.fivefilters.org/extract.php"
    __priority = {"term": 5, "pos": 1, "cardinal": 1}
    __IMPORTANCE_RATIO = 0.05

    def __init__(
        self, html, vocab=None, spaced_raw_text=None, ents=None, raw_ents=None
    ):
        self.html = html
        if vocab is not None:
            self.__key_terms = vocab
        if ents is not None:
            self.__entities = ents
        if raw_ents is not None:
            self.__raw_ents = raw_ents
        if spaced_raw_text is not None:
            self.__spaced_raw_text = spaced_raw_text

    def __compare_priority(a, b):
        # add length priority
        return Paragraph.__priority.get(a["tag"], 0) > Paragraph.__priority.get(
            b["tag"], 0
        )

    def __remove_self_overlap(lst):
        lst.sort(key=lambda x: x["start"])
        i = 0
        while i < len(lst) - 1:
            if lst[i]["end"] >= lst[i + 1]["start"]:
                if Paragraph.__compare_priority(lst[i], lst[i + 1]):
                    lst.pop(i)
                else:
                    lst.pop(i + 1)
            else:
                i += 1
        return lst

    def __insert_helper(haystack, needle, index):
        return haystack[:index] + needle + haystack[index:]

    def __get_overlap(a, b):
        """Elements from b that are overlapping will be deleted. Assume a and b are sorted lists of tuples."""
        res, i, j = [], 0, 0
        while i < len(a) and j < len(b):
            if a[i]["end"] <= b[j]["end"]:
                if a[i]["end"] >= b[j]["start"]:
                    res.append(j)
                i += 1
                continue
            elif a[i]["end"] >= b[j]["end"]:
                if a[i]["start"] <= b[j]["end"]:
                    res.append(j)
                j += 1
                continue
        # TODO: optimize
        # print(sorted(list(set(res))))
        return sorted(list(set(res)))

    def __init_html_tags(self):
        self.__html_tags = []
        self.__spaced_raw_text = deepcopy(self.html)
        for match in Paragraph.html_tag_pattern.finditer(self.__spaced_raw_text):
            start, end, tag = match.start(), match.end(), match[0]
            self.__html_tags.append({"start": start, "end": end, "tag": tag})
            self.__spaced_raw_text = "".join(
                (
                    self.__spaced_raw_text[:start],
                    " " * (end - start),
                    self.__spaced_raw_text[end:],
                )
            )

    def fivefilters_get_terms(self, max=None):
        if max is None:
            max = int(len(set(self.spaced_raw_text)) * Paragraph.__IMPORTANCE_RATIO)
        # print(max)
        data = {
            "text": self.raw_text,
            "output": "json",
            "terms_only": 0,
            "lowercase": 1,
            "text_or_url": "text",
            "max": max,
            "yahoo": 1,
            "filter": 1,
            "max strength": 5,
        }
        response = requests.post(Paragraph.__fivefilters_url, data=data)
        print(json.loads(response.text)["ResultSet"]["Result"])
        return {
            "text": json.loads(response.text)["ResultSet"]["Result"],
            "status": response.status_code,
        }

    @cached_property
    def raw_text(self):
        raw = deepcopy(self.html)
        return re.sub(r" {3,}", " ", raw)

    # @property
    # def raw_text(self):
    #     print(hasattr(self, "__raw_text"))
    #     if not hasattr(self, "__raw_text"):
    #         raw = deepcopy(self.html)
    #         setattr(self, "__raw_text", re.sub(r" {3,}", " ", raw))
    #     return getattr(self, "__raw_text")

    @cached_property
    def spaced_raw_text(self):
        self.__init_html_tags()

    @cached_property
    def html_tags(self):
        self.__init_html_tags()

    @cached_property
    def key_terms(self):
        num_of_terms = int(Paragraph.__IMPORTANCE_RATIO * self.raw_text.count(" "))
        key_terms = combo_basic(self.raw_text).index.values.tolist()
        return key_terms[: min(len(key_terms) - 1, num_of_terms)]

    @cached_property
    def key_term_indices(self):
        indices = []
        # TODO: use a trie since its faster
        for term in self.key_terms:
            index = self.spaced_raw_text.lower().find(term)
            if index == -1:
                continue
            indices.append({"tag": "term", "start": index, "end": index + len(term)})
        return indices

    @cached_property
    def raw_ents(self):
        return Paragraph.nlp(self.spaced_raw_text).ents

    @cached_property
    def entities(self):
        return [
            {"tag": ent.label_, "start": ent.start_char, "end": ent.end_char}
            for ent in self.raw_ents
        ]

    @property
    def annotated_with_entities(self):
        annotated = deepcopy(self.html)
        key_terms = deepcopy(self.key_term_indices)
        html_tags = deepcopy(self.html_tags)
        ents = deepcopy(self.entities)
        all_tags = sorted(key_terms + ents, key=lambda x: x["start"])
        all_tags = Paragraph.__remove_self_overlap(all_tags)
        for overlap in Paragraph.__get_overlap(html_tags, all_tags)[::-1]:
            all_tags.pop(overlap)
        for ent in all_tags[::-1]:
            annotated = Paragraph.__insert_helper(
                annotated, "</{}>".format(ent["tag"].lower()), ent["end"],
            )
            annotated = Paragraph.__insert_helper(
                annotated, "<{}>".format(ent["tag"].lower()), ent["start"],
            )
        return annotated


if __name__ == "__main__":
    s = """An association between the development of cancer and inflammation has long-been appreciated [<a class="bibr popnode tag_hotlink tag_tooltip" href="#R4" id="__tag_831364405" rid="R4">4</a>,<a class="bibr popnode tag_hotlink tag_tooltip" href="#R5" id="__tag_831364344" rid="R5">5</a>]. The inflammatory response orchestrates host defenses to microbial infection and mediates tissue repair and regeneration, which may occur due to infectious or non-infectious tissue damage. Epidemiological evidence points to a connection between inflammation and a predisposition for the development of cancer, i.e. long-term inflammation leads to the development of dysplasia. Epidemiologic studies estimate that nearly 15 percent of the worldwide cancer incidence is associated with microbial infection [<a class="bibr popnode tag_hotlink tag_tooltip" href="#R6" id="__tag_831364367" rid="R6">6</a>]. Chronic infection in immunocompetent hosts such as human papilloma virus or hepatitis B and C virus infection leads to cervical and hepatocellular carcinoma, respectively. In other cases, microbes may cause cancer due to opportunistic infection such as in Kaposi’s sarcoma (a result of human herpes virus (HHV)-8 infection) or inappropriate immune responses to microbes in certain individuals, which may occur in gastric cancer secondary to <em>Helicobacter pylori</em> colonization or colon cancer because of long-standing inflammatory bowel disease precipitated by the intestinal microflora [<a class="bibr popnode tag_hotlink tag_tooltip" href="#R4" id="__tag_831364375" rid="R4">4</a>,<a class="bibr popnode tag_hotlink tag_tooltip" href="#R5" id="__tag_831364391" rid="R5">5</a>]. In many other cases, conditions associated with chronic irritation and subsequent inflammation predispose to cancer, such as the long-term exposure to cigarette smoke, asbestos, and silica [<a class="bibr popnode tag_hotlink tag_tooltip" href="#R4" id="__tag_831364370" rid="R4">4</a>,<a class="bibr popnode tag_hotlink tag_tooltip" href="#R5" id="__tag_831364372" rid="R5">5</a>]."""
    TERMS = [
        "response orchestrates host defenses",
        "cancer",
        "epidemiologic studies estimate",
        "c virus infection",
        "mediates tissue repair",
        "=r chronic infection",
        "non-infectious tissue damage",
        "epidemiological evidence points",
        "inflammation",
        "silica [<",
        "hepatocellular carcinoma",
        "hepatitis b",
        "colon cancer",
        "herpes virus",
    ]
    #     start()
    Paragraph(s, TERMS).annotated_with_entities
#     end()
#     print(Paragraph(s).annotated_with_entities)
