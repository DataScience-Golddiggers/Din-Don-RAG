import pickle
import numpy as np
from pathlib import Path
from typing import Any, Dict, Tuple, Optional
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from utils.logger import logger
from utils.config import config


class ModelTrainer:
    
    def __init__(self, model_type: str = "logistic_regression"):
        self.model_type = model_type
        self.model = self._get_model(model_type)
        self.best_params = None
    
    def _get_model(self, model_type: str):
        models = {
            "naive_bayes": MultinomialNB(),
            "logistic_regression": LogisticRegression(max_iter=1000, random_state=42),
            "svm": SVC(random_state=42),
            "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
        }
        
        if model_type not in models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        return models[model_type]
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> Any:
        logger.info(f"Training {self.model_type} model...")
        self.model.fit(X_train, y_train)
        logger.info("Training completed")
        return self.model
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        else:
            raise AttributeError(f"{self.model_type} does not support predict_proba")
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
        average: str = "weighted"
    ) -> Dict[str, float]:
        y_pred = self.predict(X_test)
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average=average, zero_division=0),
            "recall": recall_score(y_test, y_pred, average=average, zero_division=0),
            "f1": f1_score(y_test, y_pred, average=average, zero_division=0),
        }
        
        logger.info(f"Evaluation metrics: {metrics}")
        return metrics
    
    def get_classification_report(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> str:
        y_pred = self.predict(X_test)
        report = classification_report(y_test, y_pred)
        return report
    
    def get_confusion_matrix(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> np.ndarray:
        y_pred = self.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        return cm
    
    def cross_validate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        cv: int = 5,
        scoring: str = "accuracy"
    ) -> Dict[str, float]:
        logger.info(f"Performing {cv}-fold cross-validation...")
        scores = cross_val_score(self.model, X, y, cv=cv, scoring=scoring)
        
        results = {
            "mean_score": scores.mean(),
            "std_score": scores.std(),
            "scores": scores.tolist(),
        }
        
        logger.info(f"Cross-validation results: mean={results['mean_score']:.4f}, std={results['std_score']:.4f}")
        return results
    
    def hyperparameter_tuning(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        param_grid: Dict[str, Any],
        cv: int = 5,
        scoring: str = "accuracy"
    ) -> Dict[str, Any]:
        logger.info("Starting hyperparameter tuning...")
        
        grid_search = GridSearchCV(
            self.model,
            param_grid,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        self.model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_
        
        logger.info(f"Best parameters: {self.best_params}")
        logger.info(f"Best score: {grid_search.best_score_:.4f}")
        
        return {
            "best_params": self.best_params,
            "best_score": grid_search.best_score_,
            "cv_results": grid_search.cv_results_
        }
    
    def save_model(self, file_path: Optional[Path] = None):
        if file_path is None:
            file_path = config.MODELS_DIR / f"{self.model_type}.pkl"
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "wb") as f:
            pickle.dump(self.model, f)
        
        logger.info(f"Model saved to {file_path}")
    
    @staticmethod
    def load_model(file_path: Path):
        with open(file_path, "rb") as f:
            model = pickle.load(f)
        
        logger.info(f"Model loaded from {file_path}")
        return model
