from sqlalchemy import Column, Integer, String

from Database import init_db, db_session
from Database import Base

class Text(Base):
    __tablename__ = 'texts'
    id = Column(Integer, primary_key=True)
    text = Column(String(512))

    def __init__(self, text):
        cropped_text = text[0:512]
        self.text = cropped_text
