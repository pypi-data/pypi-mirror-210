import logging
from sys import stdout
import structlog
from structlog.stdlib import LoggerFactory


def edit_logging_event(_, __, event_dict):
    try:

        new_event_dict = event_dict
        error = event_dict.get("event")

        new_event_dict['Status'] = error.exception_type
        # new_event_dict['ErrorCode'] = error.error_code
        new_event_dict['Message'] = error.error_message
        new_event_dict['Error'] = event_dict.get("Error")
        new_event_dict['ErrorType'] = event_dict.get("ErrorType")
        new_event_dict['RequestId'] = error.request_id
        new_event_dict['Caller'] = error.validation_type
        new_event_dict.pop("event")

        return new_event_dict

    except Exception as e:
        pass

    try:

        new_event_dict = event_dict

        new_event_dict['Status'] = event_dict.get("event")
        new_event_dict['Message'] = event_dict.get("Message")
        new_event_dict['Error'] = event_dict.get("Error")
        new_event_dict['ErrorType'] = event_dict.get("ErrorType")
        new_event_dict['RequestId'] = event_dict.get("RequestId")
        new_event_dict['Caller'] = event_dict.get("Caller")
        new_event_dict.pop("event")

        return new_event_dict

    except Exception as e:
        pass

    return event_dict


def _logger():
    logging.basicConfig(
        format="%(message)s",
        stream=stdout,
        level=logging.INFO
    )

    structlog.configure(
        logger_factory=LoggerFactory(),
        processors=[
            edit_logging_event,
            structlog.processors.TimeStamper(fmt="iso", utc=True, key='Timestamp'),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ]
    )

    log = structlog.get_logger()

    return log
