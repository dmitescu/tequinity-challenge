from pycorenlp import StanfordCoreNLP

from ParsingResult import ParsingResult

import os

class ParsingRequest():
    def __init__(self, text):
        self.text = text

    def get_result(self):
        host = os.environ.get("SC_NLP_HOST") or "nlp:9000"
        nlp = StanfordCoreNLP("http://" + host)
        output = nlp.annotate(self.text, properties={
            'annotators': 'ner, pos',
            'outputFormat': 'json'
            })
        result = ParsingResult(output)
        return result

