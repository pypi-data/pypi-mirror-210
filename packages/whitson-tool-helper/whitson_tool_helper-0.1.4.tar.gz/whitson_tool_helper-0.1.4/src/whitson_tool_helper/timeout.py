def apply_timeout(timeout_in_seconds: int):
    def decorator(func):
        def wrapper(*args, **kwargs):
            import signal
            from whitson_tool_helper import CalculationTimeoutError

            def handler(signum, frame):
                raise CalculationTimeoutError

            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout_in_seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator
