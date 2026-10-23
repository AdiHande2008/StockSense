import json
from datetime import datetime
import pandas as pd
import numpy as np
from app.db.database import SessionLocal
from app.models.entities import Instrument, DailyPrice, ModelVersion, EvaluationMetric, Prediction
from app.ml.models import train_and_evaluate_symbol
from app.ml.engine import predict_latest_direction
from app.core.config import settings

def run_optimization():
    db = SessionLocal()
    insts = db.query(Instrument).all()

    print("=" * 65)
    print("  Starting Enhanced Per-Stock Machine Learning Optimization")
    print("=" * 65)
    results = []

    for idx, inst in enumerate(insts):
        # Retrieve recent historical sessions
        prices = (
            db.query(DailyPrice)
            .filter_by(instrument_id=inst.id)
            .order_by(DailyPrice.trading_date.desc())
            .limit(245)
            .all()
        )
        prices.reverse()
        df_prices = pd.DataFrame([
            {
                "trading_date": p.trading_date,
                "open": p.open,
                "high": p.high,
                "low": p.low,
                "close": p.close,
                "volume": p.volume,
            }
            for p in prices
        ])

        # Train and select best model among Logistic Regression, Random Forest, Gradient Boosting, Ensemble
        res = train_and_evaluate_symbol(inst.symbol, df_prices, settings.ARTIFACTS_DIR)

        # 1. Update ModelVersion
        mv = db.query(ModelVersion).filter_by(instrument_id=inst.id).first()
        if not mv:
            mv = ModelVersion(instrument_id=inst.id, version=f"{inst.symbol.lower()}-v2.0")
            db.add(mv)
            db.commit()
            db.refresh(mv)
        mv.version = f"{inst.symbol.lower()}-v2.0"
        mv.algorithm = res["selected_algorithm"]
        mv.artifact_path = res["artifact_path"]
        mv.published_at = datetime.utcnow()
        db.commit()

        # 2. Update EvaluationMetric
        em = db.query(EvaluationMetric).filter_by(model_version_id=mv.id, partition="TEST").first()
        if not em:
            em = EvaluationMetric(model_version_id=mv.id, partition="TEST")
            db.add(em)
        m = res["metrics"]
        bm = res["baseline_metrics"]
        em.accuracy = m["accuracy"]
        em.balanced_accuracy = m["balanced_accuracy"]
        em.baseline_balanced_accuracy = bm["balanced_accuracy"]
        em.precision = m["precision"]
        em.recall = m["recall"]
        em.f1 = m["f1"]
        em.samples = m["samples"]
        em.confusion_matrix_json = json.dumps(m["confusion_matrix"])
        em.start_date = datetime.strptime(res["test_period"]["from"], "%Y-%m-%d").date()
        em.end_date = datetime.strptime(res["test_period"]["to"], "%Y-%m-%d").date()
        db.commit()

        # 3. Update Latest Prediction
        pred_res = predict_latest_direction(inst.symbol, df_prices, res["artifact_path"])
        pred = db.query(Prediction).filter_by(instrument_id=inst.id).first()
        if not pred:
            pred = Prediction(instrument_id=inst.id, model_version_id=mv.id)
            db.add(pred)
        pred.direction = pred_res["direction"]
        pred.score = pred_res["score"]
        pred.as_of_date = pred_res["as_of_date"]
        pred.target_date = datetime(2026, 10, 26).date()
        pred.features_summary_json = json.dumps(pred_res["features_summary"])
        pred.stale = False
        db.commit()

        algo_label = res["selected_algorithm"]
        acc_pct = m["accuracy"] * 100
        bal_pct = m["balanced_accuracy"] * 100
        results.append({
            "symbol": inst.symbol,
            "algorithm": algo_label,
            "accuracy": acc_pct,
            "balanced_accuracy": bal_pct,
            "baseline": bm["balanced_accuracy"] * 100,
            "direction": pred_res["direction"],
            "score": pred_res["score"],
        })
        print(f"[{idx+1}/10] {inst.symbol:<12} {algo_label:<22} Acc: {acc_pct:.1f}% | BalAcc: {bal_pct:.1f}%")

    print("-" * 65)
    mean_acc = np.mean([r["accuracy"] for r in results])
    mean_bal = np.mean([r["balanced_accuracy"] for r in results])
    print(f"Overall Average: Accuracy = {mean_acc:.1f}%, Balanced Accuracy = {mean_bal:.1f}%")
    print("=" * 65)
    db.close()
    return results

if __name__ == "__main__":
    run_optimization()
