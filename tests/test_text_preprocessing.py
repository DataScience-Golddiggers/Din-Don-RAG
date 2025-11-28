import pytest
import pandas as pd
from src.text_preprocessing import TextPreprocessor


@pytest.fixture
def preprocessor():
    return TextPreprocessor(language='english')


def test_clean_text_removes_urls(preprocessor):
    text = "Check out https://example.com for more info"
    cleaned = preprocessor.clean_text(text)
    assert "https://example.com" not in cleaned
    assert "example" not in cleaned or "com" not in cleaned


def test_clean_text_removes_emails(preprocessor):
    text = "Contact us at test@example.com"
    cleaned = preprocessor.clean_text(text)
    assert "test@example.com" not in cleaned


def test_clean_text_removes_numbers(preprocessor):
    text = "The year 2024 has 365 days"
    cleaned = preprocessor.clean_text(text)
    assert "2024" not in cleaned
    assert "365" not in cleaned


def test_clean_text_converts_to_lowercase(preprocessor):
    text = "HELLO World"
    cleaned = preprocessor.clean_text(text)
    assert cleaned.islower()


def test_clean_text_handles_none(preprocessor):
    result = preprocessor.clean_text(None)
    assert result == ''


def test_tokenize_returns_list(preprocessor):
    text = "This is a test"
    tokens = preprocessor.tokenize(text)
    assert isinstance(tokens, list)
    assert len(tokens) > 0


def test_tokenize_removes_stopwords(preprocessor):
    text = "the quick brown fox"
    tokens = preprocessor.tokenize(text, remove_stopwords=True)
    assert "the" not in tokens


def test_preprocess_returns_string(preprocessor):
    text = "This is a test"
    result = preprocessor.preprocess(text)
    assert isinstance(result, str)


def test_preprocess_dataframe():
    preprocessor = TextPreprocessor(language='english')
    df = pd.DataFrame({
        'text': ['Hello world!', 'Test 123', 'Email: test@example.com']
    })
    
    result = preprocessor.preprocess_dataframe(df, 'text')
    
    assert 'cleaned_text' in result.columns
    assert 'tokens' in result.columns
    assert 'processed_text' in result.columns
    assert len(result) <= len(df)
