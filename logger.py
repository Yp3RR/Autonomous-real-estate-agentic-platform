import logging
import json
import time
from datetime import datetime, timezone
import os


class JSONFormatter(logging.Formatter):

    def format(self, record):
        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
        }
        # Attach any extra fields passed in
        for key, value in record.__dict__.items():
            if key not in (
                "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "name", "taskName"
            ):
                log_obj[key] = value

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj, default=str)


def get_logger(name: str = "northstar") -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JSONFormatter())
        logger.addHandler(console_handler)

        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(os.path.join(log_dir, "northstar.log"))
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)

    return logger


# Convenience helpers

def log_request(logger, session_id: str, message: str):
    logger.info("chat_request", extra={
        "session_id": session_id,
        "user_message": message,
    })


def log_tool_fired(logger, session_id: str, tool_name: str, result: dict):
    logger.info("tool_fired", extra={
        "session_id": session_id,
        "tool_name": tool_name,
        "result": result,
    })


def log_response(logger, session_id: str, response: str, duration_ms: float, tools_fired: list):
    logger.info("agent_response", extra={
        "session_id": session_id,
        "response_preview": response[:100],
        "duration_ms": round(duration_ms, 2),
        "tools_fired": tools_fired,
    })


def log_error(logger, session_id: str, error: Exception):
    logger.error("agent_error", extra={
        "session_id": session_id,
        "error_type": type(error).__name__,
        "error_message": str(error),
    }, exc_info=True)


def log_analytics(logger, session_id: str, analytics: dict):
    logger.info("analytics_generated", extra={
        "session_id": session_id,
        "lead_score": analytics.get("lead_score"),
        "interest_level": analytics.get("interest_level"),
        "visit_booked": analytics.get("visit_booked"),
        "escalated": analytics.get("escalated_to_human"),
    })