import itertools
import os
import re

import scrapy
import PyPDF2

LOCAL_FILENAME = 'book.pdf'
LOCAL_FOLDER = 'storage'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf_path = f"{BASE_DIR}/{LOCAL_FOLDER}/{LOCAL_FILENAME}"
text_and_font = []


def find_paragraph():
    pattern = re.compile("P[0-9]{3}")
    for i, value in enumerate(text_and_font):
        if pattern.match(value[0]):
            yield i


class ArticlespiderSpider(scrapy.Spider):
    name = "articlespider"
    start_urls = ["file://"+pdf_path]

    @staticmethod
    def visitor_text(text, ctm, tm, font_dict, font_size):
        lines = text.split("\n")
        for line in lines:
            if any(value in line.lower() for value in ('5th World Psoriasis', 'acta',)):
                text_and_font.pop()
                continue
            if line:
                text_and_font.append((line, font_dict, font_size))

    @staticmethod
    def split_affiliations(affiliations):
        affiliations_dict = {}
        affiliations_list = re.split(r'(\d+)', affiliations)
        if len(affiliations_list) > 1:
            counter = 1
            for i in range(1, len(affiliations_list), 2):
                key = str(counter)
                value = affiliations_list[i + 1]
                value = value.replace('and', '')
                value = value.strip()
                affiliations_dict[key] = value
                counter += 1
            return affiliations_dict
        else:
            return affiliations_list

    # @staticmethod
    def store_data(self, names, affiliations):
        complete_set = {}
        affiliations_dict = self.split_affiliations(affiliations)
        if not any(char.isdigit() for char in names):
            names_list = names.split(',')
            affiliation = affiliations_dict[0]
            for name in names_list:
                name = name.strip()
                complete_set[name] = affiliation
        else:
            names_list = re.split(r'(\d+)', names)
            for i in range(1, len(names_list), 2):
                name = names_list[i - 1].replace(',', '').strip()
                affiliation_key = names_list[i]
                try:
                    affiliation = affiliations_dict[affiliation_key]
                except Exception as e:
                    affiliation = 'Error: ' + str(e)
                complete_set[name] = affiliation
        return complete_set

    def parse(self, response, **kwargs):
        affiliatopn_patterns = ('pharma', 'university', 'clinic', 'academy', 'hospital', 'department',
                                'medical', 'research', 'group', 'country', 'derma', 'sweden')
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_number in range(6, len(pdf_reader.pages)-4):
                pdf_reader.pages[page_number].extract_text(visitor_text=self.visitor_text)

            gen = find_paragraph()
            while True:
                paragraph_id = next(gen, None)
                if paragraph_id:
                    title = ''
                    names = ''
                    affiliation = ''
                    text = ''
                    session_name = text_and_font[paragraph_id][0]
                    i = paragraph_id+1
                    while 'Bold' in text_and_font[i][1]['/BaseFont']:
                        title += text_and_font[i][0]
                        i += 1
                    while 'Italic' in text_and_font[i][1]['/BaseFont'] and 'Introduction' not in text_and_font[i][0] and len(text_and_font[i][0]) > 1:
                        if any(value in text_and_font[i][0].lower() for value in affiliatopn_patterns):
                            break
                        else:
                            names += text_and_font[i][0]
                        i += 1
                    while 'Italic' in text_and_font[i][1]['/BaseFont'] and 'Introduction' not in text_and_font[i][0]:
                        affiliation += text_and_font[i][0]
                        i += 1
                    while i < len(text_and_font) and not re.match(r'P\d{3}', text_and_font[i][0]):
                        text += text_and_font[i][0]
                        i += 1
                    item = {'session_name': session_name, 'title': title,
                            'name_and_affiliation': self.store_data(names, affiliation), 'text': text}
                    yield item

                else:
                    break


        pass
