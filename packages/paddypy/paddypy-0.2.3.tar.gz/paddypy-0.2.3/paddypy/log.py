import datetime
import logging
import sys
import time
import traceback
from functools import wraps

from opencensus.ext.azure.log_exporter import AzureLogHandler

from . import access


class CloudLogger:
    """
    Initialize the CloudLogger class.

    :param app_logger_name: The name of the application logger.
    :type app_logger_name: str
    :param module_name: The name of the module using the logger.
    :type module_name: str
    :param applicationinsights_key: The Application Insights key, defaults to None.
    :type applicationinsights_key: str, optional
    :param logger_level: The logging level, defaults to 10 (DEBUG).
    :type logger_level: int, optional
    """

    def __init__(
        self,
        app_logger_name,
        module_name,
        applicationinsights_key=None,
        logger_level=10,
    ):
        self.LOGGER_LEVEL = logger_level
        self.logger = self._get_logger(
            app_logger_name=app_logger_name,
            module_name=module_name,
            applicationinsights_key=applicationinsights_key,
            logger_level=self.LOGGER_LEVEL,
        )
        self.logger.setLevel(level=logger_level)

    def _get_logger(
        self, app_logger_name, module_name, applicationinsights_key, logger_level
    ):
        """
        Get the logger instance with the specified configurations.

        :param app_logger_name: The name of the application logger.
        :type app_logger_name: str
        :param module_name: The name of the module using the logger.
        :type module_name: str
        :param applicationinsights_key: The Application Insights key.
        :type applicationinsights_key: str
        :param logger_level: The logging level.
        :type logger_level: int
        :return: The configured logger instance.
        :rtype: logging.Logger
        """
        FMT = "[{levelname:^9}] {name}: {message}"
        FORMATS = {
            logging.DEBUG: FMT,
            logging.INFO: "\33[36m{fmt}\33[0m".format(fmt=FMT),
            logging.WARNING: "\33[33m{fmt}\33[0m".format(fmt=FMT),
            logging.ERROR: "\33[31m{fmt}\33[0m".format(fmt=FMT),
            logging.CRITICAL: "\33[1m\33[31m{fmt}\33[0m".format(fmt=FMT),
        }

        class CustomFormatter(logging.Formatter):
            def format(self, record):
                log_fmt = FORMATS[record.levelno]
                formatter = logging.Formatter(log_fmt, style="{")
                return formatter.format(record)

        handler = logging.StreamHandler()
        handler.setFormatter(CustomFormatter())
        logging.basicConfig(level=logger_level, handlers=[handler])

        logger = logging.getLogger(app_logger_name).getChild(module_name)
        if applicationinsights_key:
            azure_handler = AzureLogHandler(
                connection_string=str(applicationinsights_key)
            )
            azure_handler.setLevel(logger_level)
            logger.addHandler(azure_handler)
        return logger

    # def timeit(self, func):
    #     @wraps(func)
    #     def timeit_wrapper(*args, **kwargs):
    #         start_time = time.perf_counter()
    #         result = func(*args, **kwargs)
    #         end_time = time.perf_counter()
    #         total_time = end_time - start_time
    #         self.logger.log(msg=f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds', level=logging.INFO)
    #         #logging.log(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds', level=logging.DEBUG)
    #         return result
    #     return timeit_wrapper

    # def timeit_silence(self, func):
    #     @wraps(func)
    #     def timeit_wrapper(*args, **kwargs):
    #         start_time = time.perf_counter()
    #         result = func(*args, **kwargs)
    #         end_time = time.perf_counter()
    #         total_time = end_time - start_time
    #         arg_types = tuple(type(arg).__name__ for arg in args)
    #         kwarg_types = {key: type(val).__name__ for key, val in kwargs.items()}
    #         log_msg = f'Function {func.__name__}{arg_types} {kwarg_types} Took {total_time:.4f} seconds'
    #         self.logger.log(msg=log_msg, level=logging.INFO)
    #         return result
    #     return timeit_wrapper

    def timeit(self, silence_args=False):
        """
        Decorator for timing a function and logging the execution time.

        :param silence_args: If True, logs the types of the arguments instead of their values, defaults to False.
        :type silence_args: bool, optional
        :return: Decorated function.
        """

        def decorator(func):
            @wraps(func)
            def timeit_wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                total_time = end_time - start_time
                if silence_args:
                    arg_types = tuple(type(arg).__name__ for arg in args)
                    kwarg_types = {
                        key: type(val).__name__ for key, val in kwargs.items()
                    }
                    log_msg = f"Function {func.__name__}{arg_types} {kwarg_types} Took {total_time:.4f} seconds"
                else:
                    log_msg = f"Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds"

                self.logger.log(msg=log_msg, level=logging.INFO)
                return result

            return timeit_wrapper

        return decorator

    def except_block(self, exception: Exception, exception_message="No message"):
        """
        Log the details of an exception, including module name, function name, custom message,
        time of occurrence, exception type, arguments, instance, stack trace, and local variables.

        :param exception: The exception instance.
        :type exception: Exception
        :param exception_message: A custom message for the exception, defaults to "No message".
        :type exception_message: str, optional
        """
        exception_timne = str(datetime.datetime.now())
        exception_type = str(type(exception))
        exception_argument = str(exception.args)
        exception_instance = str(exception)
        current_frame = sys._getframe().f_back
        if current_frame is not None:
            module_name = current_frame.f_globals["__name__"]
            function_name = current_frame.f_code.co_name
            local_variables = current_frame.f_locals
        else:
            module_name = "unknown"
            function_name = "unknown"
            local_variables = {"local_variables": "unknown"}

        stack_trace = traceback.format_exc()
        self.logger.log(
            msg="Exception module name: {message}".format(message=module_name),
            level=logging.ERROR,
        )
        self.logger.log(
            msg="Exception function name: {message}".format(message=function_name),
            level=logging.ERROR,
        )
        self.logger.log(
            msg="Exception message: {message}".format(message=exception_message),
            level=logging.ERROR,
        )
        self.logger.log(
            msg="Exception occured at: {message}".format(message=exception_timne),
            level=logging.ERROR,
        )
        self.logger.log(
            msg="Exception instance type: {message}".format(message=exception_type),
            level=logging.ERROR,
        )
        self.logger.log(
            msg="Exception argument: {message}".format(message=exception_argument),
            level=logging.ERROR,
        )
        self.logger.log(
            msg="Exception instance: {message}".format(message=exception_instance),
            level=logging.ERROR,
        )
        self.logger.log(
            msg="Exception stack trace: {message}".format(message=stack_trace),
            level=logging.ERROR,
        )
        self.logger.log(
            msg="Exception local variables: {message}".format(message=local_variables),
            level=logging.ERROR,
        )
