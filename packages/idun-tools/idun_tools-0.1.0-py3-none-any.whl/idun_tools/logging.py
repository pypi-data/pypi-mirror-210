"Logger that prints serialized messages and exceptions"
import json, traceback, sys, os
from loguru import logger as logger
from loguru._recattrs import RecordException

default_log_format = (
    "<green>{time}</green> | <level><b>{level}</b></level> | "
    + "<cyan>{name}:{module}:{line}</cyan> - <white><b>{message}</b></white> - <yellow>{extra}</yellow>"
)

enable_exceptiongroups = sys.version_info.major == 3 and sys.version_info.minor >= 11

def pop_extra_errors(record):
    "Collect exception info and remove it from the 'extra' field"
    exceptions = []
    if record["exception"]:
        exceptions.append(record["exception"])
    if record["extra"]:
        if "error" in record["extra"]:
            # This is usually how user code captures errors
            if isinstance(record["extra"]["error"], BaseException):
                exceptions.append(record["extra"]["error"])
                del record["extra"]["error"]
        elif "error_group" in record["extra"]:
            if enable_exceptiongroups and isinstance(record["extra"]["error_group"], BaseExceptionGroup):
                exceptions.append(record["extra"]["error_group"])
                del record["extra"]["error_group"]
    return exceptions


def serialize(record) -> str:
    func = "" if record["function"] != "" else f" in {record['function']}"
    subset = {
        "timestamp": record["time"].timestamp(),
        "level": record["level"].name,
        "message": record["message"],
        "place": f"{record['name']}:{record['module']}:{record['line']}{func}",
    }
    exceptions = pop_extra_errors(record)
    if len(exceptions) == 1:
        subset["exception"] = {
            "type": type(exceptions[0]).__name__,
            "message": str(exceptions[0]),
            "exception": traceback.format_exception(exceptions[0], limit=200),
        }
        if enable_exceptiongroups and isinstance(exceptions[0], BaseExceptionGroup):
            subset["exception"]["exception_group"] = exceptions[0].exceptions
    if len(exceptions) > 1:
        # In case the user code passes in errors in multiple ways
        subset["exception"] = [
            {
                "type": type(exc).__name__,
                "message": str(exc),
                "exception": traceback.format_exception(exc, limit=200),
            }
            for exc in exceptions
        ]
        for i, exc in enumerate(subset["exception"]):
            if enable_exceptiongroups and isinstance(exc, BaseExceptionGroup):
                subset["exception"][i]["exception_group"] = exc.exceptions
    if record["thread"].name != "MainThread":
        subset["thread"] = record["thread"].name
    if len(record["extra"]) > 0:
        subset["extra"] = record["extra"]
        if "serialized" in subset["extra"]:
            del subset["extra"]["serialized"]

    return json.dumps(subset, default=str, ensure_ascii=False) + "\n"


def try_serialize(record) -> None:
    record["extra"]["serialized"] = ""
    try:
        record["extra"]["serialized"] = serialize(record)
    except BaseException as err:
        record["extra"][
            "serialized"
        ] = f"LOGGER ERROR WHILE SERIALIZING RECORD: {type(err)}: {err}"


def patch_extra_exceptions(record) -> None:
    "Patch the first exception provided through the 'extra' field"
    try:
        exceptions = pop_extra_errors(record)
        if len(exceptions) > 0:
            exc = exceptions[0]
            if enable_exceptiongroups and isinstance(exc, BaseExceptionGroup):
                record["exception"] = RecordException(
                    type=type(exc),
                    value=Exception("".join(traceback.format_exception(exc))),
                    # Exception Group traceback is not yet supported by Loguru
                    # see https://github.com/Delgan/loguru/issues/805
                    traceback=None,
                )
            elif isinstance(exc, BaseException):
                record["exception"] = RecordException(
                    type=type(exc), value=exc, traceback=exc.__traceback__
                )
            else:
                record["exception"] = exc
    except Exception as err:
        record[
            "exception"
        ] = f"LOGGER ERROR WHILE GATHERING EXCEPTIONS: {type(err).__name__}: {err}"


# If not in DEBUG mode, setup production logger
if os.getenv("DEBUG") is None:
    logger = logger.patch(try_serialize)
    logger.remove()
    logger.add(
        sys.stdout,
        format="{extra[serialized]}",
        backtrace=True,
        diagnose=False,
        enqueue=True,
    )
else:
    # NOTE: normally we would want to let Loguru handle errors passed through the `extra` field,
    # however Loguru can't handle exceptions that are unpickleable, such as `botocore` errors:
    #     _pickle.PicklingError: Can't pickle <class 'botocore.errorfactory.NoSuchBucket'>:
    #     attribute lookup NoSuchBucket on botocore.errorfactory failed
    #
    # logger = logger.patch(patch_extra_exceptions)
    logger.remove()
    logger.add(
        sys.stdout,
        format=default_log_format,
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )