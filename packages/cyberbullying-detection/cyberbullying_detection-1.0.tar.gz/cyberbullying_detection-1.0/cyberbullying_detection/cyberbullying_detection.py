from pkg_resources import resource_stream
from num2words import num2words
from bs4 import BeautifulSoup
import re
import unidecode
from string import punctuation
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk import tokenize
from nltk.corpus import stopwords
import pickle


model = pickle.load(resource_stream('cyberbullying_detection', 'data/lg.pkl'))
vector = pickle.load(resource_stream('cyberbullying_detection', 'data/count.pkl'))

class cyberbullying:
    def __init__(self,data):
        self.text = data

    def lower_case_convertion(self):
        lower_text = self.text.lower()
        return lower_text

    def remove_punctuation(self):
        """
        Return :- String after removing punctuations
        Input :- String
        Output :- String
        """
        return self.text.translate(str.maketrans('', '', punctuation))

    def numtowords(self):
        """
        Return :- self.text which have all numbers or integers in the form of words
        Input :- string
        Output :- string
        """
        # splitting self.text into words with space
        after_spliting = self.text.split()

        for index in range(len(after_spliting)):
            if after_spliting[index].isdigit():
                after_spliting[index] = num2words(after_spliting[index])

        # joining list into string with space
        numbers_to_words = ' '.join(after_spliting)
        return numbers_to_words

    def remove_html_tags_beautifulsoup(self):
        """
        Return :- String without Html tags
        input :- String
        Output :- String
        """
        parser = BeautifulSoup(self.text, "html.parser")
        without_html = parser.get_text(separator = " ")
        return without_html

    def remove_urls(self):
        """
        Return :- String without URLs
        input :- String
        Output :- String
        """
        url_pattern = r'https?://\S+|www\.\S+'
        without_urls = re.sub(pattern=url_pattern, repl=' ', string=self.text)
        return without_urls

    def accented_to_ascii(self):
        """
        Return :- self.text after converting accented characters
        Input :- string
        Output :- string
        """
        # apply unidecode function on self.text to convert
        # accented characters to ASCII values
        self.text = unidecode.unidecode(self.text)
        return self.text

    def remove_extra_spaces(self):
        """
        Return :- string after removing extra whitespaces
        Input :- String
        Output :- String
        """
        space_pattern = r'\s+'
        without_space = re.sub(pattern=space_pattern, repl=" ", string=self.text)
        return without_space

    def remove_single_char(self):
        """
        Return :- string after removing single characters
        Input :- string
        Output:- string
        """
        single_char_pattern = r'\s+[a-zA-Z]\s+'
        without_sc = re.sub(pattern=single_char_pattern, repl=" ", string=self.text)
        return without_sc


    def lemmatization(self):
        lemma = WordNetLemmatizer()
        # word tokenization
        tokens = word_tokenize(self.text)

        for index in range(len(tokens)):
            # lemma word
            lemma_word = lemma.lemmatize(tokens[index])
            tokens[index] = lemma_word

        return ' '.join(tokens)

    def label(self):
        label={'religion': 0,     
        'age': 1,                    
        'gender':2,                 
        'ethnicity':3,              
        'not_cyberbullying':4,      
        'other_cyberbullying':5}
        return label[self.text]

    def find(self):
        self.text = self.lower_case_convertion()
        self.text = self.remove_punctuation()
        self.text = self.numtowords()
        self.text = self.lower_case_convertion()
        self.text = self.remove_html_tags_beautifulsoup()
        self.text = self.remove_urls()
        self.text = self.accented_to_ascii()
        self.text = self.remove_single_char()
        stop = stopwords.words('english')
        self.text= ' '.join([word for word in self.text.split() if word not in (stop)])
        self.text = self.lemmatization()
        self.text = [self.text]
        vect = vector.transform(self.text).toarray()
        my_prediction = model.predict(vect)
        val = my_prediction[0]
        label={0:'religion',     
        1:'age',                    
        2:'gender',                 
        3:'ethnicity',              
        4:'not_cyberbullying',      
        5:'other_cyberbullying'}
        msg = label[val]
        print(msg)