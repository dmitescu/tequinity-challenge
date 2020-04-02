import json

class ParsingResult:
    def __init__(self, result):
        self.result = result

    def to_json(self):
        return json.dumps({"result": self.result})
