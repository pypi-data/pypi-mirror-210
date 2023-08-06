import time
import json

from starlette.concurrency import iterate_in_threadpool
from typing import Callable
from loguru import logger
from fastapi import Request
from fastapi import Response
import sys
import pathlib

def configure_logger( app_name: str = "app" ,log_level: str = "DEBUG", log_path: str = None):
    logger_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS!UTC} - [{level}] {message}"
    )

    logger.remove()
    logger.add(
        sys.stdout, level=log_level, colorize=True, format=logger_format
    )

    if log_path:
        logger.add(
            pathlib.Path(log_path, f"{app_name}.log"),
            format=logger_format,
            level=log_level,
            rotation="500mb",
            compression="gz",
        )

async def loggingMiddleware(request: Request, call_next: Callable) -> Response:
    start_time = time.time()
    request_logger_data = {
        "type": "REQUEST",
        "method": request.method,
        "path": request.url.path,
    }
    logger.debug(json.dumps(request_logger_data))
    response: Response = await call_next(request)
    response_logger_data = {
        "type": "RESPONSE",
        "status_code": response.status_code,
        "request_time_duration": time.time() - start_time,
    }
    if response.status_code != 200:
        response_body = [chunk async for chunk in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(response_body))
        response_body = json.loads(response_body[0].decode())
        logger.error(
            json.dumps(
                {
                    **response_logger_data, 
                    "error": response_body['detail']
                }
            )
        )
    else:
        logger.success(json.dumps(response_logger_data))
    return response