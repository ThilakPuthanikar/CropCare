import json
import logging
from typing import Any
from sqlalchemy.orm import Session
from ..models.ai_history import AIUsageHistory

logger = logging.getLogger(__name__)


class AIService:
    @staticmethod
    def log_history(
        db: Session,
        user_id: int,
        feature_type: str,
        input_payload: Any,
        output_payload: Any,
    ) -> None:
        """Log AI usage to ai_usage_history gracefully without disrupting requests if DB errors occur."""
        try:
            input_str = (
                json.dumps(input_payload, default=str)
                if isinstance(input_payload, (dict, list))
                else str(input_payload or "")
            )
            output_str = (
                json.dumps(output_payload, default=str)
                if isinstance(output_payload, (dict, list))
                else str(output_payload or "")
            )

            record = AIUsageHistory(
                user_id=user_id,
                feature_type=feature_type,
                input_payload=input_str,
                output_payload=output_str,
            )
            db.add(record)
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.error(
                f"AIService: Failed to log AI history for user {user_id} ({feature_type}): {exc}"
            )


ai_service = AIService()
