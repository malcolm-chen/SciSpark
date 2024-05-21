import nltk
from nltk.tokenize import WordPunctTokenizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

sen_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') 

# nltk.download('stopwords')

def tokenize_en(text):
    return [tok for tok in nltk.word_tokenize(text)]

# split paragraph texts in to single words
def split_para(text):
    stop_words = set(stopwords.words('english'))
    words = []
    for i, w in enumerate(tokenize_en(text)):
        if w.isalnum() and w.lower() not in stop_words:
            words.append({
                'id': i,
                'word': w,
                'stopword': False,
                'keyword': 0
            })
        else:
            words.append({
                'id': i,
                'word': w,
                'stopword': True,
                'keyword': 0
            })
    return words

def split_sentence(text):
    return  sen_tokenizer.tokenize(text) 
