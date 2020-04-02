from pycorenlp import StanfordCoreNLP

from ParsingResult import ParsingResult

class ParsingRequest():
    def __init__(self, text):
        self.text = text

    def get_result(self):
        nlp = StanfordCoreNLP("http://nlp:9000")
        output = nlp.annotate(self.text, properties={
            'annotators': 'ner, pos',
            'outputFormat': 'json'
            })
        result = ParsingResult(output)
        return result

