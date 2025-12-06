import re
import pandas as pd
from typing import List, Optional
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, SnowballStemmer


class TextPreprocessor:
    
    def __init__(self, language: str = 'italian', use_lemmatization: bool = True):
        self.language = language
        self.use_lemmatization = use_lemmatization
        
        try:
            self.stop_words = set(stopwords.words(language))
        except:
            print(f"Lingua '{language}' non disponibile, uso 'english'")
            self.stop_words = set(stopwords.words('english'))
        
        # WordNetLemmatizer is primarily for English. For other languages, we might prefer stemming.
        # However, keeping the structure as requested.
        if use_lemmatization and language == 'english':
            self.lemmatizer = WordNetLemmatizer()
        else:
            # Use SnowballStemmer which supports multiple languages (including Italian)
            # If lemmatization was requested for non-English, we fallback to stemming or no-op?
            # Let's fallback to SnowballStemmer as it's the standard for Italian in NLTK.
            try:
                self.stemmer = SnowballStemmer(language)
                self.use_lemmatization = False # Force stemming if not English
            except ValueError:
                print(f"Stemmer per '{language}' non disponibile, uso 'english'")
                self.stemmer = SnowballStemmer("english")
    
    def clean_text(self, text: str) -> str:
        if pd.isna(text):
            return ''
        
        text = str(text)
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'@\w+|#\w+', '', text)
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        text = text.lower()
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str, remove_stopwords: bool = True) -> List[str]:
        if pd.isna(text) or text == '':
            return []
        
        # Pass language to word_tokenize to use the correct punkt model
        tokens = word_tokenize(str(text), language=self.language)
        
        if remove_stopwords:
            tokens = [word for word in tokens if word.lower() not in self.stop_words]
        
        if self.use_lemmatization:
            tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        else:
            tokens = [self.stemmer.stem(word) for word in tokens]
        
        return tokens
    
    def preprocess(self, text: str, remove_stopwords: bool = True) -> str:
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned, remove_stopwords)
        return ' '.join(tokens)
    
    def preprocess_dataframe(self, df: pd.DataFrame, text_column: str, 
                           remove_stopwords: bool = True) -> pd.DataFrame:
        df = df.copy()
        df['cleaned_text'] = df[text_column].apply(self.clean_text)
        df['tokens'] = df['cleaned_text'].apply(
            lambda x: self.tokenize(x, remove_stopwords)
        )
        df['processed_text'] = df['tokens'].apply(lambda x: ' '.join(x))
        
        df = df[df['processed_text'].str.len() > 0]
        
        return df
