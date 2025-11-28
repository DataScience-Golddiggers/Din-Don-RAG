import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import pandas as pd

from src.config import config
from src.logger import logger
from src.text_preprocessing import TextPreprocessor
from src.model_trainer import ModelTrainer
from src.utils import load_object


def main(args):
    logger.info("Loading model and vectorizer...")
    
    model = ModelTrainer.load_model(args.model_path)
    vectorizer = load_object(args.vectorizer_path)
    
    if args.input_text:
        texts = [args.input_text]
    elif args.input_file:
        df = pd.read_csv(args.input_file)
        texts = df[args.text_column].tolist()
    else:
        raise ValueError("Either --input-text or --input-file must be provided")
    
    logger.info(f"Preprocessing {len(texts)} text(s)...")
    preprocessor = TextPreprocessor(language=args.language)
    processed_texts = [preprocessor.preprocess(text) for text in texts]
    
    logger.info("Vectorizing text...")
    X = vectorizer.transform(processed_texts)
    
    logger.info("Making predictions...")
    predictions = model.predict(X)
    
    if hasattr(model, 'predict_proba'):
        probabilities = model.predict_proba(X)
    else:
        probabilities = None
    
    print("\n" + "=" * 50)
    print("PREDICTIONS")
    print("=" * 50)
    
    for i, (text, pred) in enumerate(zip(texts, predictions)):
        print(f"\nText {i+1}:")
        print(f"  Original: {text[:100]}...")
        print(f"  Prediction: {pred}")
        
        if probabilities is not None:
            print(f"  Probabilities: {probabilities[i]}")
    
    print("=" * 50)
    
    if args.output_file:
        output_df = pd.DataFrame({
            'text': texts,
            'prediction': predictions
        })
        
        if probabilities is not None:
            for i in range(probabilities.shape[1]):
                output_df[f'prob_class_{i}'] = probabilities[:, i]
        
        output_df.to_csv(args.output_file, index=False)
        logger.info(f"Predictions saved to {args.output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make predictions with trained model")
    
    parser.add_argument(
        "--model-path",
        type=Path,
        default=config.MODELS_DIR / "logistic_regression.pkl",
        help="Path to trained model"
    )
    parser.add_argument(
        "--vectorizer-path",
        type=Path,
        default=config.MODELS_DIR / "vectorizer.pkl",
        help="Path to fitted vectorizer"
    )
    parser.add_argument(
        "--input-text",
        type=str,
        help="Single text to predict"
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        help="CSV file with texts to predict"
    )
    parser.add_argument(
        "--text-column",
        type=str,
        default="text",
        help="Name of text column in input file"
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Output CSV file for predictions"
    )
    parser.add_argument(
        "--language",
        type=str,
        default="italian",
        help="Language for preprocessing"
    )
    
    args = parser.parse_args()
    main(args)
