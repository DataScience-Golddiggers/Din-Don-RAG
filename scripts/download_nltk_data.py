import nltk
import sys


def download_nltk_resources():
    resources = [
        'punkt',
        'stopwords',
        'wordnet',
        'omw-1.4',
        'averaged_perceptron_tagger',
        'maxent_ne_chunker',
        'words'
    ]
    
    print("Downloading NLTK resources...")
    for resource in resources:
        try:
            nltk.download(resource, quiet=False)
            print(f"✓ Downloaded: {resource}")
        except Exception as e:
            print(f"✗ Failed to download {resource}: {e}")
    
    print("\n✓ All NLTK resources downloaded successfully!")


if __name__ == "__main__":
    download_nltk_resources()
