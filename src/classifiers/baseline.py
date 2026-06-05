from __future__ import annotations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


class ProblemCategoryBaseline:
    """Optional ML baseline: TF-IDF + Logistic Regression."""

    def __init__(self) -> None:
        self.pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
                ("clf", LogisticRegression(max_iter=200, random_state=42)),
            ]
        )

    def train(self, data: pd.DataFrame, text_col: str = "text", label_col: str = "problem_category") -> dict:
        train_df, test_df = train_test_split(
            data,
            test_size=0.2,
            random_state=42,
            stratify=data[label_col],
        )
        self.pipeline.fit(train_df[text_col], train_df[label_col])
        predictions = self.pipeline.predict(test_df[text_col])

        return {
            "classification_report": classification_report(test_df[label_col], predictions, output_dict=True),
            "confusion_matrix": confusion_matrix(test_df[label_col], predictions).tolist(),
            "labels": sorted(test_df[label_col].unique().tolist()),
        }

    def predict(self, texts: list[str]) -> list[str]:
        return self.pipeline.predict(texts).tolist()
