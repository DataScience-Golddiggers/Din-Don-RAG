import numpy as np
import pandas as pd
from typing import List, Tuple, Optional, Dict
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from gensim.models import Word2Vec
from src.logger import logger


class FeatureExtractor:
    
    def __init__(self):
        self.vectorizer = None
        self.topic_model = None
        self.word2vec_model = None
    
    def extract_bow(
        self,
        texts: List[str],
        max_features: int = 1000,
        min_df: int = 2,
        max_df: float = 0.95,
        **kwargs
    ) -> Tuple[np.ndarray, CountVectorizer]:
        self.vectorizer = CountVectorizer(
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            **kwargs
        )
        features = self.vectorizer.fit_transform(texts)
        logger.info(f"Extracted BoW features: shape {features.shape}")
        return features.toarray(), self.vectorizer
    
    def extract_tfidf(
        self,
        texts: List[str],
        max_features: int = 1000,
        min_df: int = 2,
        max_df: float = 0.95,
        ngram_range: Tuple[int, int] = (1, 2),
        **kwargs
    ) -> Tuple[np.ndarray, TfidfVectorizer]:
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            ngram_range=ngram_range,
            **kwargs
        )
        features = self.vectorizer.fit_transform(texts)
        logger.info(f"Extracted TF-IDF features: shape {features.shape}")
        return features.toarray(), self.vectorizer
    
    def extract_topics_lda(
        self,
        texts: List[str],
        n_topics: int = 10,
        max_features: int = 1000,
        **kwargs
    ) -> Tuple[np.ndarray, LatentDirichletAllocation]:
        vectorizer = CountVectorizer(max_features=max_features, min_df=2)
        bow = vectorizer.fit_transform(texts)
        
        self.topic_model = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            **kwargs
        )
        topic_features = self.topic_model.fit_transform(bow)
        
        logger.info(f"Extracted {n_topics} topics using LDA")
        return topic_features, self.topic_model
    
    def extract_topics_nmf(
        self,
        texts: List[str],
        n_topics: int = 10,
        max_features: int = 1000,
        **kwargs
    ) -> Tuple[np.ndarray, NMF]:
        vectorizer = TfidfVectorizer(max_features=max_features, min_df=2)
        tfidf = vectorizer.fit_transform(texts)
        
        self.topic_model = NMF(
            n_components=n_topics,
            random_state=42,
            **kwargs
        )
        topic_features = self.topic_model.fit_transform(tfidf)
        
        logger.info(f"Extracted {n_topics} topics using NMF")
        return topic_features, self.topic_model
    
    def get_top_words_per_topic(
        self,
        feature_names: List[str],
        n_words: int = 10
    ) -> Dict[int, List[str]]:
        if self.topic_model is None:
            raise ValueError("No topic model fitted. Run extract_topics_* first.")
        
        topics = {}
        for topic_idx, topic in enumerate(self.topic_model.components_):
            top_indices = topic.argsort()[-n_words:][::-1]
            top_words = [feature_names[i] for i in top_indices]
            topics[topic_idx] = top_words
        
        return topics
    
    def train_word2vec(
        self,
        tokenized_texts: List[List[str]],
        vector_size: int = 100,
        window: int = 5,
        min_count: int = 2,
        workers: int = 4,
        **kwargs
    ) -> Word2Vec:
        self.word2vec_model = Word2Vec(
            sentences=tokenized_texts,
            vector_size=vector_size,
            window=window,
            min_count=min_count,
            workers=workers,
            **kwargs
        )
        logger.info(f"Trained Word2Vec model with {len(self.word2vec_model.wv)} words")
        return self.word2vec_model
    
    def get_document_vector(
        self,
        tokens: List[str],
        aggregation: str = "mean"
    ) -> np.ndarray:
        if self.word2vec_model is None:
            raise ValueError("No Word2Vec model trained. Run train_word2vec first.")
        
        vectors = []
        for token in tokens:
            if token in self.word2vec_model.wv:
                vectors.append(self.word2vec_model.wv[token])
        
        if not vectors:
            return np.zeros(self.word2vec_model.vector_size)
        
        vectors = np.array(vectors)
        if aggregation == "mean":
            return vectors.mean(axis=0)
        elif aggregation == "sum":
            return vectors.sum(axis=0)
        elif aggregation == "max":
            return vectors.max(axis=0)
        else:
            raise ValueError(f"Unknown aggregation method: {aggregation}")
