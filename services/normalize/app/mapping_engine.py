"""
ML-Powered Account Mapping Engine

Implements:
1. Rule-based mapping (pattern matching)
2. String similarity mapping (TF-IDF, Levenshtein)
3. Machine learning classification
4. Hybrid approach with confidence scoring
"""
import logging
import re
import pickle
from typing import List, Dict, Any, Tuple, Optional
from uuid import UUID
from difflib import SequenceMatcher

import numpy as np
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .models import MappingConfidence, MappingStatus
from .schemas import SimilarAccountResponse

logger = logging.getLogger(__name__)


# ========================================
# Rule-Based Mapper
# ========================================

class RuleBasedMapper:
    """
    Pattern-based account mapping using rules

    Applies user-defined rules to map accounts based on
    keywords, patterns, and regular expressions.
    """

    @staticmethod
    async def apply_rules(
        account_name: str,
        account_code: str,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """
        Apply mapping rules to find best match

        Returns:
            Dict with suggested_account_code, confidence, rule_name
            or None if no rule matches
        """
        query = text("""
            SELECT
                rule_name,
                target_account_code,
                confidence_boost,
                priority,
                is_regex
            FROM atlas.mapping_rules
            WHERE is_active = true
            ORDER BY priority DESC, confidence_boost DESC
        """)

        result = await db.execute(query)
        rules = result.fetchall()

        for rule in rules:
            rule_name, target_code, confidence_boost, priority, is_regex = rule

            # Check if rule matches
            if is_regex:
                # Use regex matching
                if re.search(rule_name, account_name, re.IGNORECASE):
                    return {
                        "suggested_account_code": target_code,
                        "confidence": min(0.85 + confidence_boost, 0.99),
                        "method": "rule_regex",
                        "rule_name": rule_name
                    }
            else:
                # Simple keyword matching
                if rule_name.lower() in account_name.lower():
                    return {
                        "suggested_account_code": target_code,
                        "confidence": min(0.80 + confidence_boost, 0.99),
                        "method": "rule_keyword",
                        "rule_name": rule_name
                    }

        return None


# ========================================
# Similarity-Based Mapper
# ========================================

class SimilarityMapper:
    """
    String similarity-based account mapping

    Uses TF-IDF vectorization and Levenshtein distance
    to find similar account names in chart of accounts.
    """

    @staticmethod
    def levenshtein_similarity(s1: str, s2: str) -> float:
        """
        Calculate Levenshtein similarity between two strings

        Returns:
            Similarity score between 0.0 and 1.0
        """
        return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

    @staticmethod
    async def find_similar_accounts(
        account_name: str,
        db: AsyncSession,
        top_k: int = 5
    ) -> List[SimilarAccountResponse]:
        """
        Find similar accounts using string similarity

        Method:
        1. Fetch all chart of accounts entries
        2. Calculate Levenshtein distance to each
        3. Return top-k most similar

        Args:
            account_name: Account name to match
            db: Database session
            top_k: Number of similar accounts to return

        Returns:
            List of similar accounts with scores
        """
        query = text("""
            SELECT
                account_code,
                account_name,
                account_type
            FROM atlas.chart_of_accounts
            WHERE is_active = true
        """)

        result = await db.execute(query)
        accounts = result.fetchall()

        # Calculate similarity scores
        similarities = []
        for account_code, name, account_type in accounts:
            score = SimilarityMapper.levenshtein_similarity(account_name, name)
            if score >= settings.SIMILARITY_THRESHOLD:
                similarities.append({
                    "account_code": account_code,
                    "account_name": name,
                    "account_type": account_type,
                    "similarity_score": round(score, 3)
                })

        # Sort by similarity (descending) and return top-k
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        return [
            SimilarAccountResponse(**sim)
            for sim in similarities[:top_k]
        ]

    @staticmethod
    async def suggest_mapping(
        account_name: str,
        account_code: str,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """
        Suggest account mapping using similarity

        Returns best match if similarity exceeds threshold
        """
        similar_accounts = await SimilarityMapper.find_similar_accounts(
            account_name, db, top_k=1
        )

        if similar_accounts and len(similar_accounts) > 0:
            best_match = similar_accounts[0]

            # Convert similarity to confidence
            # High similarity (0.9+) = high confidence
            # Medium similarity (0.7-0.9) = medium confidence
            confidence = best_match.similarity_score * 0.95

            return {
                "suggested_account_code": best_match.account_code,
                "suggested_account_name": best_match.account_name,
                "confidence": confidence,
                "method": "similarity_levenshtein",
                "alternatives": [
                    {
                        "account_code": acc.account_code,
                        "account_name": acc.account_name,
                        "score": acc.similarity_score
                    }
                    for acc in similar_accounts[1:5] if len(similar_accounts) > 1
                ]
            }

        return None


# ========================================
# ML-Based Mapper
# ========================================

class MLMapper:
    """
    Machine learning-based account mapping

    Uses trained classification model to predict account mappings.
    Supports Random Forest, Gradient Boosting, and Neural Networks.
    """

    def __init__(self):
        """Initialize ML mapper"""
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.model_loaded = False

    def load_model(self, model_path: str = None):
        """
        Load trained ML model from disk

        Args:
            model_path: Path to pickled model file
        """
        try:
            path = model_path or settings.ML_MODEL_PATH

            with open(path, 'rb') as f:
                model_data = pickle.load(f)

            self.model = model_data['model']
            self.vectorizer = model_data.get('vectorizer')
            self.label_encoder = model_data.get('label_encoder')
            self.model_loaded = True

            logger.info(f"ML model loaded from {path}")
            return True

        except FileNotFoundError:
            logger.warning(f"ML model not found at {path}")
            self.model_loaded = False
            return False
        except Exception as e:
            logger.error(f"Error loading ML model: {e}")
            self.model_loaded = False
            return False

    def extract_features(self, account_name: str, account_code: str) -> Dict[str, Any]:
        """
        Extract features from account for ML prediction

        Features:
        - TF-IDF vectors from account name
        - Length of account name
        - Presence of common keywords (cash, receivable, payable, etc.)
        - Account code patterns
        """
        features = {
            "name_length": len(account_name),
            "code_length": len(account_code),
            "has_cash": int("cash" in account_name.lower()),
            "has_receivable": int("receivable" in account_name.lower()),
            "has_payable": int("payable" in account_name.lower()),
            "has_inventory": int("inventory" in account_name.lower()),
            "has_revenue": int("revenue" in account_name.lower() or "sales" in account_name.lower()),
            "has_expense": int("expense" in account_name.lower() or "cost" in account_name.lower()),
            "has_asset": int("asset" in account_name.lower()),
            "has_liability": int("liability" in account_name.lower() or "payable" in account_name.lower()),
            "has_equity": int("equity" in account_name.lower() or "capital" in account_name.lower()),
        }

        return features

    async def predict_mapping(
        self,
        account_name: str,
        account_code: str,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """
        Predict account mapping using ML model

        Returns:
            Dict with suggested_account_code, confidence, alternatives
            or None if model not loaded or prediction fails
        """
        if not self.model_loaded:
            logger.warning("ML model not loaded, attempting to load...")
            if not self.load_model():
                return None

        try:
            # Extract features
            features = self.extract_features(account_name, account_code)

            # If using vectorizer (TF-IDF), transform text
            if self.vectorizer:
                text_features = self.vectorizer.transform([account_name])
                # Combine with numeric features
                numeric_features = np.array([[
                    features["name_length"],
                    features["has_cash"],
                    features["has_receivable"],
                    features["has_payable"],
                    features["has_inventory"],
                    features["has_revenue"],
                    features["has_expense"],
                ]])
                X = np.hstack([text_features.toarray(), numeric_features])
            else:
                # Use only engineered features
                X = np.array([[v for v in features.values()]])

            # Predict with probability
            if hasattr(self.model, 'predict_proba'):
                probas = self.model.predict_proba(X)[0]
                predicted_class_idx = np.argmax(probas)
                confidence = float(probas[predicted_class_idx])

                # Get top 3 predictions
                top_indices = np.argsort(probas)[::-1][:3]

                if self.label_encoder:
                    predicted_account = self.label_encoder.inverse_transform([predicted_class_idx])[0]
                    alternatives = [
                        {
                            "account_code": self.label_encoder.inverse_transform([idx])[0],
                            "confidence": float(probas[idx])
                        }
                        for idx in top_indices[1:]  # Skip first (main prediction)
                    ]
                else:
                    # Fallback if no label encoder
                    predicted_account = str(predicted_class_idx)
                    alternatives = []

                # Fetch account name from database
                query = text("""
                    SELECT account_name
                    FROM atlas.chart_of_accounts
                    WHERE account_code = :account_code
                    LIMIT 1
                """)
                result = await db.execute(query, {"account_code": predicted_account})
                row = result.fetchone()

                return {
                    "suggested_account_code": predicted_account,
                    "suggested_account_name": row[0] if row else "Unknown",
                    "confidence": confidence,
                    "method": "ml_classification",
                    "alternatives": alternatives,
                    "features": features
                }
            else:
                # Model doesn't support probability prediction
                prediction = self.model.predict(X)[0]

                return {
                    "suggested_account_code": str(prediction),
                    "confidence": 0.75,  # Default confidence
                    "method": "ml_classification",
                    "alternatives": []
                }

        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return None


# ========================================
# Hybrid Mapper (Combines all methods)
# ========================================

class HybridMapper:
    """
    Hybrid account mapper combining rules, similarity, and ML

    Strategy:
    1. Try rule-based mapping first (highest confidence)
    2. If no rule matches, try ML prediction
    3. If ML confidence < threshold, fall back to similarity
    4. Combine results and select best suggestion
    """

    def __init__(self):
        """Initialize hybrid mapper"""
        self.rule_mapper = RuleBasedMapper()
        self.similarity_mapper = SimilarityMapper()
        self.ml_mapper = MLMapper()

        # Attempt to load ML model
        self.ml_mapper.load_model()

    async def suggest_mapping(
        self,
        account_name: str,
        account_code: str,
        db: AsyncSession,
        use_ml: bool = True,
        use_rules: bool = True
    ) -> Dict[str, Any]:
        """
        Generate mapping suggestion using hybrid approach

        Returns:
            Complete mapping suggestion with confidence score
        """
        suggestions = []

        # 1. Try rule-based mapping
        if use_rules:
            rule_result = await self.rule_mapper.apply_rules(account_name, account_code, db)
            if rule_result:
                suggestions.append(rule_result)

        # 2. Try ML prediction
        if use_ml:
            ml_result = await self.ml_mapper.predict_mapping(account_name, account_code, db)
            if ml_result:
                suggestions.append(ml_result)

        # 3. Try similarity mapping
        similarity_result = await self.similarity_mapper.suggest_mapping(account_name, account_code, db)
        if similarity_result:
            suggestions.append(similarity_result)

        # Select best suggestion based on confidence
        if not suggestions:
            return {
                "suggested_account_code": None,
                "suggested_account_name": None,
                "confidence": 0.0,
                "confidence_level": MappingConfidence.LOW,
                "method": "none",
                "alternatives": []
            }

        # Sort by confidence and select best
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        best_suggestion = suggestions[0]

        # Determine confidence level
        confidence = best_suggestion['confidence']
        if confidence >= 0.90:
            confidence_level = MappingConfidence.VERY_HIGH
        elif confidence >= 0.75:
            confidence_level = MappingConfidence.HIGH
        elif confidence >= 0.60:
            confidence_level = MappingConfidence.MEDIUM
        else:
            confidence_level = MappingConfidence.LOW

        return {
            "suggested_account_code": best_suggestion.get("suggested_account_code"),
            "suggested_account_name": best_suggestion.get("suggested_account_name", "Unknown"),
            "confidence": confidence,
            "confidence_level": confidence_level,
            "method": best_suggestion["method"],
            "alternatives": best_suggestion.get("alternatives", []),
            "all_methods": [s["method"] for s in suggestions]
        }
