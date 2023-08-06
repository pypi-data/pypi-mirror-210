import os
import traceback
from .modules import http_server
from ValiotWorker.Logging import LogLevel, LogStyle


def health_check_probe(log, loggingStyle):
    log(LogLevel.INFO, "Running HEALTH_CHECK_PROBE ...")

    try:
        envHost = os.environ.get('POD_IP', "0.0.0.0")
        healthCheckPort = int(os.environ.get('HEALTHCHECK_PORT', '65432'))
        http_server.run(log, addr=envHost, port=healthCheckPort)

        log(LogLevel.INFO, "Stopping HEALTH_CHECK_PROBE ...")

    except Exception as e:
        log(LogLevel.ERROR, "Some error happened at the HEALTH_CHECK_PROBE:")
        error_info = f"{str(e)}\nstack trace:\n{traceback.format_exc()}" if loggingStyle != LogStyle.JSON else ""
        error = {
            "message": str(e),
            "stack": traceback.format_exc()
        }
        log(LogLevel.ERROR, f"HEALTH_CHECK_PROBE crashed unexpectedly.\n{error_info}", extra={
            "error": error
        })
