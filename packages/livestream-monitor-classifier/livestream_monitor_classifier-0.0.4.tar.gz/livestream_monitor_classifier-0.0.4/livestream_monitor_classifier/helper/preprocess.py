import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from unidecode import unidecode
from pathlib import Path

path = Path(__file__).parent/'../data/stopwords-custom.txt'
with path.open() as f:
  stopwords = f.read().splitlines()

class Preprocess:
  def __init__(self):
    self._stemmer = StemmerFactory().create_stemmer()

  def _cleaning(self, text):
    # remove USER text
    text = re.sub(r'\b\w*user\w*\b', '', text, flags=re.IGNORECASE)
    # remove username
    text = re.sub(r"@[\w]*", '', text)
    # remove latin alphabet
    text = unidecode(text)
    # remove hyperlink
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', '', text)
    # remove special char
    text = re.sub(r"[()\"#/@;:<>{}*`'+=~|.!?,]", "", text)
    text = re.sub('[^a-zA-Zа-яА-Я]+', ' ', text)
    # remove whitespace
    text = re.sub("\s\s+", " ", text)
    text = text.lstrip().rstrip()
    # remove emoticons
    emoji_pattern = re.compile("["u"\U0001F600-\U0001F64F" u"\U0001F300-\U0001F5FF" u"\U0001F680-\U0001F6FF" u"\U0001F1E0-\U0001F1FF" "]+", flags=re.UNICODE)
    text = re.sub(emoji_pattern, '', text)
    # print('CLEANING : ', text)
    return text

  def _case_folding(self, text):
    text = text.lower()
    # print('CASE FOLDING : ',text)
    return text

  def get(self, text):
    text = self._cleaning(text)
    text = self._case_folding(text)
    return text

  def get_list(self, text_list):
    texts = [self.get(text) for text in text_list]
    return texts
