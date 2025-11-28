import pickle
import json
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from src.logger import logger


def save_object(obj: Any, file_path: Path):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'wb') as f:
        pickle.dump(obj, f)
    logger.info(f"Object saved to {file_path}")


def load_object(file_path: Path) -> Any:
    with open(file_path, 'rb') as f:
        obj = pickle.load(f)
    logger.info(f"Object loaded from {file_path}")
    return obj


def save_json(data: Dict, file_path: Path):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"JSON saved to {file_path}")


def load_json(file_path: Path) -> Dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    logger.info(f"JSON loaded from {file_path}")
    return data


def plot_word_frequencies(
    word_freq: Dict[str, int],
    top_n: int = 20,
    figsize: tuple = (12, 6),
    save_path: Path = None
):
    top_words = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n])
    
    plt.figure(figsize=figsize)
    plt.bar(top_words.keys(), top_words.values())
    plt.title(f'Top {top_n} Most Frequent Words')
    plt.xlabel('Word')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Plot saved to {save_path}")
    
    plt.show()


def generate_wordcloud(
    text: str,
    width: int = 800,
    height: int = 400,
    max_words: int = 100,
    background_color: str = 'white',
    save_path: Path = None
):
    wordcloud = WordCloud(
        width=width,
        height=height,
        background_color=background_color,
        max_words=max_words
    ).generate(text)
    
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud', fontsize=20)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"WordCloud saved to {save_path}")
    
    plt.show()


def plot_confusion_matrix(
    cm,
    classes: List[str] = None,
    figsize: tuple = (8, 6),
    save_path: Path = None
):
    plt.figure(figsize=figsize)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=classes, yticklabels=classes)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Confusion matrix saved to {save_path}")
    
    plt.show()


def plot_class_distribution(
    df: pd.DataFrame,
    column: str,
    figsize: tuple = (10, 6),
    save_path: Path = None
):
    plt.figure(figsize=figsize)
    df[column].value_counts().plot(kind='bar')
    plt.title('Class Distribution')
    plt.xlabel('Class')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Class distribution plot saved to {save_path}")
    
    plt.show()


def get_text_statistics(df: pd.DataFrame, text_column: str) -> Dict[str, float]:
    df_copy = df.copy()
    df_copy['text_length'] = df_copy[text_column].astype(str).str.len()
    df_copy['word_count'] = df_copy[text_column].astype(str).str.split().str.len()
    
    stats = {
        'total_documents': len(df_copy),
        'avg_text_length': df_copy['text_length'].mean(),
        'min_text_length': df_copy['text_length'].min(),
        'max_text_length': df_copy['text_length'].max(),
        'avg_word_count': df_copy['word_count'].mean(),
        'min_word_count': df_copy['word_count'].min(),
        'max_word_count': df_copy['word_count'].max(),
    }
    
    return stats
