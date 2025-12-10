import sys
from pathlib import Path
# Add /app to sys.path so we can import from utils (which is mounted at /app/utils)
# In the container, the structure is:
# /app/scripts/train_pipeline.py
# /app/utils/
# /app/src/ (if mounted, but the error suggests imports are from src.*)

# If the original code imported from src.*, it means it expected a src folder.
# However, in our Dockerfile/volumes, we have:
# /app/utils (from ./utils)
# /app/src (from ./src) - Wait, did we mount src? Yes, in the last step.

# The issue is likely that 'src' is not a package (no __init__.py) or the path is slightly off.
# Let's check where we are.
sys.path.append("/app")

import pandas as pd
import argparse
from sklearn.model_selection import train_test_split

# Adjust imports based on the actual structure in the container.
# The utils folder contains the modules directly (config.py, logger.py, etc.)
# So it should be 'from utils.config import config' NOT 'from src.config import config'
# UNLESS the original project structure had these inside src/ and we are reusing that code.
# Looking at the file list from the beginning:
# utils/
#   config.py
#   logger.py
#   ...
# So the correct import is 'from utils.config import config'

from utils.config import config
from utils.logger import logger
from utils.data_loader import DataLoader
from utils.text_preprocessing import TextPreprocessor
from utils.feature_extraction import FeatureExtractor
from utils.model_trainer import ModelTrainer
from utils.utils import save_object


def main(args):
    config.ensure_directories()
    
    logger.info("=" * 50)
    logger.info("Starting NLP Training Pipeline")
    logger.info("=" * 50)
    
    logger.info(f"Loading data from {args.input_file}")
    loader = DataLoader()
    df = loader.load_csv(args.input_file)
    
    logger.info(f"Preprocessing text (language: {args.language})")
    preprocessor = TextPreprocessor(
        language=args.language,
        use_lemmatization=args.lemmatization
    )
    df_processed = preprocessor.preprocess_dataframe(
        df,
        text_column=args.text_column,
        remove_stopwords=args.remove_stopwords
    )
    
    logger.info("Extracting features")
    extractor = FeatureExtractor()
    X, vectorizer = extractor.extract_tfidf(
        df_processed['processed_text'].tolist(),
        max_features=args.max_features
    )
    
    if args.label_column in df_processed.columns:
        if args.binary:
            logger.info("Converting labels to binary (relevant=1, irrelevant=0)")
            # Map 'irrelevant' to 0, everything else to 1
            df_processed['binary_label'] = df_processed[args.label_column].apply(
                lambda x: 0 if str(x).lower() == 'irrelevant' else 1
            )
            y = df_processed['binary_label'].values
        else:
            y = df_processed[args.label_column].values
        
        logger.info("Splitting data into train/test sets")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=args.test_size,
            random_state=args.random_state,
            stratify=y
        )
        
        logger.info(f"Training {args.model} model")
        trainer = ModelTrainer(model_type=args.model)
        trainer.train(X_train, y_train)
        
        logger.info("Evaluating model")
        metrics = trainer.evaluate(X_test, y_test)
        
        print("\n" + "=" * 50)
        print("EVALUATION RESULTS")
        print("=" * 50)
        for metric, value in metrics.items():
            print(f"{metric.capitalize()}: {value:.4f}")
        print("=" * 50)
        
        print("\nClassification Report:")
        print(trainer.get_classification_report(X_test, y_test))
        
        model_path = config.MODELS_DIR / f"{args.model}.pkl"
        trainer.save_model(model_path)
        
        vectorizer_path = config.MODELS_DIR / "vectorizer.pkl"
        save_object(vectorizer, vectorizer_path)
        
        logger.info("Training pipeline completed successfully!")
    else:
        logger.warning(f"Label column '{args.label_column}' not found. Skipping model training.")
        
        vectorizer_path = config.MODELS_DIR / "vectorizer.pkl"
        save_object(vectorizer, vectorizer_path)
        
        logger.info("Feature extraction completed. No model trained (unsupervised mode).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train NLP model pipeline")
    
    parser.add_argument(
        "--input-file",
        type=str,
        required=True,
        help="Path to input CSV file"
    )
    parser.add_argument(
        "--text-column",
        type=str,
        default="text",
        help="Name of the text column"
    )
    parser.add_argument(
        "--label-column",
        type=str,
        default="label",
        help="Name of the label column"
    )
    parser.add_argument(
        "--language",
        type=str,
        default="italian",
        choices=["italian", "english", "spanish", "french", "german"],
        help="Language for stopwords"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="logistic_regression",
        choices=["naive_bayes", "logistic_regression", "svm", "random_forest"],
        help="Model type to train"
    )
    parser.add_argument(
        "--max-features",
        type=int,
        default=1000,
        help="Maximum number of features for vectorization"
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Test set size (0-1)"
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random state for reproducibility"
    )
    parser.add_argument(
        "--no-lemmatization",
        dest="lemmatization",
        action="store_false",
        help="Disable lemmatization"
    )
    parser.add_argument(
        "--no-stopwords",
        dest="remove_stopwords",
        action="store_false",
        help="Keep stopwords"
    )
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Train a binary relevance classifier (1=relevant, 0=irrelevant)"
    )
    
    parser.set_defaults(lemmatization=True, remove_stopwords=True)
    
    args = parser.parse_args()
    main(args)
