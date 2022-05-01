from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize, pos_tag
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import wordnet

# 将词组中名词转为单数
def singular_phrase(phrase):
    tokenizer = RegexpTokenizer(r'\w+') # 删除字母数字外其他字符
    tokens = tokenizer.tokenize(phrase)
    tagged_sent = pos_tag(tokens)     # 获取单词词性
    wnl = WordNetLemmatizer()
    lemmas_sent = []
    for tag in tagged_sent:
        word = tag[0]
        if tag[1] == 'NNS':
            word = wnl.lemmatize(word, pos=wordnet.NOUN)
        lemmas_sent.append(word)
    return ' '.join(lemmas_sent)

if __name__ == "__main__":
    print(singular_phrase('christmas!! dogs 10inch for women chewlers'))