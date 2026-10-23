import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)
from app.ml.features import FEATURE_COLUMNS, extract_features

class MajorityBaselineClassifier:
    def __init__(self):
        self.majority_class_ = 1
        self.classes_ = np.array([0, 1])
        
    def fit(self, X, y):
        counts = pd.Series(y).value_counts()
        self.majority_class_ = int(counts.idxmax())
        return self
        
    def predict(self, X):
        return np.full(shape=(len(X),), fill_value=self.majority_class_)
        
    def predict_proba(self, X):
        prob = np.zeros((len(X), 2))
        prob[:, self.majority_class_] = 1.0
        return prob

def split_chronological(df: pd.DataFrame, train_ratio: float = 0.8) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Strict chronological split without shuffling to prevent temporal lookahead leakage."""
    n = len(df)
    train_idx = int(n * train_ratio)
    train_df = df.iloc[:train_idx].copy()
    test_df = df.iloc[train_idx:].copy()
    return train_df, test_df

def evaluate_predictions(y_true, y_pred, baseline_balanced_acc: float = 0.5) -> Dict[str, Any]:
    acc = float(accuracy_score(y_true, y_pred))
    bal_acc = float(balanced_accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    
    return {
        "accuracy": round(acc, 4),
        "balanced_accuracy": round(bal_acc, 4),
        "baseline_balanced_accuracy": round(baseline_balanced_acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        },
        "samples": len(y_true)
    }

def train_and_evaluate_symbol(symbol: str, df_prices: pd.DataFrame, artifacts_dir: str):
    """
    Runs the enhanced multi-model training and selection pipeline:
    1. Extracts 11 leakage-safe technical features (returns, trend, MACD, Bollinger %B, candle body, RSI).
    2. Chronologically splits into train (80%) and holdout test (20%).
    3. Trains Baseline, Scaled Logistic Regression, Random Forest, and Gradient Boosting.
    4. Evaluates all candidates and selects the top performer per stock.
    5. Saves the winning published model to artifacts.
    """
    df_features = extract_features(df_prices, include_target=True)
    if len(df_features) < 40:
        raise ValueError(f"Insufficient historical data for symbol {symbol}: {len(df_features)} samples.")
        
    train_df, test_df = split_chronological(df_features, train_ratio=0.8)
    
    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["target"].values
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["target"].values
    
    test_start = str(test_df["trading_date"].min())
    test_end = str(test_df["trading_date"].max())
    
    # 1. Baseline Model
    baseline = MajorityBaselineClassifier()
    baseline.fit(X_train, y_train)
    y_pred_base = baseline.predict(X_test)
    base_metrics = evaluate_predictions(y_test, y_pred_base, baseline_balanced_acc=0.50)
    
    # 2. Scaled L2 Logistic Regression Pipeline
    lr_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(random_state=42, C=0.3, max_iter=300, class_weight="balanced"))
    ])
    lr_pipe.fit(X_train, y_train)
    y_pred_lr = lr_pipe.predict(X_test)
    lr_metrics = evaluate_predictions(y_test, y_pred_lr, baseline_balanced_acc=base_metrics["balanced_accuracy"])
    
    # 3. Tuned Random Forest Classifier
    rf_pipe = Pipeline([
        ("model", RandomForestClassifier(
            n_estimators=100,
            max_depth=4,
            min_samples_leaf=4,
            max_features="sqrt",
            random_state=42
        ))
    ])
    rf_pipe.fit(X_train, y_train)
    y_pred_rf = rf_pipe.predict(X_test)
    rf_metrics = evaluate_predictions(y_test, y_pred_rf, baseline_balanced_acc=base_metrics["balanced_accuracy"])
    
    # 4. HistGradientBoosting Classifier
    hgb_pipe = Pipeline([
        ("model", HistGradientBoostingClassifier(
            max_iter=60,
            max_depth=3,
            min_samples_leaf=6,
            l2_regularization=1.5,
            random_state=42
        ))
    ])
    hgb_pipe.fit(X_train, y_train)
    y_pred_hgb = hgb_pipe.predict(X_test)
    hgb_metrics = evaluate_predictions(y_test, y_pred_hgb, baseline_balanced_acc=base_metrics["balanced_accuracy"])
    
    # 5. Soft Voting Ensemble
    voting_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("model", VotingClassifier(
            estimators=[
                ("lr", LogisticRegression(random_state=42, C=0.3, max_iter=300)),
                ("rf", RandomForestClassifier(n_estimators=80, max_depth=4, min_samples_leaf=4, random_state=42))
            ],
            voting="soft"
        ))
    ])
    voting_pipe.fit(X_train, y_train)
    y_pred_vote = voting_pipe.predict(X_test)
    vote_metrics = evaluate_predictions(y_test, y_pred_vote, baseline_balanced_acc=base_metrics["balanced_accuracy"])
    
    # Select best candidate by balanced accuracy
    candidates = [
        ("LOGISTIC_REGRESSION", lr_pipe, lr_metrics),
        ("RANDOM_FOREST", rf_pipe, rf_metrics),
        ("GRADIENT_BOOSTING", hgb_pipe, hgb_metrics),
        ("ENSEMBLE", voting_pipe, vote_metrics)
    ]
    
    best_algo, best_model, best_metrics = max(candidates, key=lambda c: (c[2]["balanced_accuracy"], c[2]["accuracy"]))
    
    os.makedirs(artifacts_dir, exist_ok=True)
    artifact_filename = f"{symbol.lower()}_model.joblib"
    artifact_path = os.path.join(artifacts_dir, artifact_filename)
    joblib.dump(best_model, artifact_path)
    
    return {
        "symbol": symbol,
        "selected_algorithm": best_algo,
        "artifact_path": artifact_path,
        "metrics": best_metrics,
        "baseline_metrics": base_metrics,
        "test_period": {"from": test_start, "to": test_end},
        "samples_train": len(train_df),
        "samples_test": len(test_df)
    }
