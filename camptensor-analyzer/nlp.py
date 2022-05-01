from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize, pos_tag
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import wordnet

# 将词组中名词转为单数
def format_phrase(phrase):
    phrase = phrase.lower()
    if len(phrase) == 10:
        if phrase.isdigit() or phrase[:2] == 'b0':
            return phrase, 'asin'
        elif phrase[:2] == 'B0':
            return phrase.lower(), 'asin'
    tokenizer = RegexpTokenizer(r'\w+') # 删除字母数字外其他字符
    tokens = tokenizer.tokenize(phrase)
    tagged_sent = pos_tag(tokens)     # 获取单词词性
    wnl = WordNetLemmatizer()
    lemmas_sent = []
    for word, pos in tagged_sent:
        if pos.startswith('N'):
            word = wnl.lemmatize(word, pos=wordnet.NOUN)
        elif pos.startswith('J'):
            word = wnl.lemmatize(word, pos=wordnet.ADJ)
        elif pos.startswith('V'):
            word = wnl.lemmatize(word, pos=wordnet.VERB)
        elif pos.startswith('R'):
            word = wnl.lemmatize(word, pos=wordnet.ADV)
        lemmas_sent.append(word)
    return ' '.join(lemmas_sent).lower(), 'keyword'

def get_parts_of_speech(searchterm):
    tokens = word_tokenize(searchterm)
    tagged_sent = pos_tag(tokens)
    wnl = WordNetLemmatizer()
    adj, noun = [], []
    for word, pos in tagged_sent:
        if pos.startswith('N'): 
            word = wnl.lemmatize(word, pos=wordnet.NOUN)
            noun.append(word)
        elif pos.startswith('J'):
            word = wnl.lemmatize(word, pos=wordnet.ADJ)
            adj.append(word)
    print(searchterm)
    print(adj, noun)
    return adj, noun

if __name__ == "__main__":
    print(get_parts_of_speech('beautiful girls'))