from functools import wraps

class endpoint:
    """Custom decorator factory for marking FastAPI endpoints."""

    @staticmethod
    def get(path: str):
        def decorator(func):
            func._endpoint_info = {"method": "get", "path": path}
            return func
        return decorator

    @staticmethod
    def post(path: str):
        def decorator(func):
            func._endpoint_info = {"method": "post", "path": path}
            return func
        return decorator

    @staticmethod
    def put(path: str):
        def decorator(func):
            func._endpoint_info = {"method": "put", "path": path}
            return func
        return decorator

    @staticmethod
    def delete(path: str):
        def decorator(func):
            func._endpoint_info = {"method": "delete", "path": path}
            return func
        return decorator

    @staticmethod
    def websocket(path: str):
        def decorator(func):
            func._endpoint_info = {"method": "websocket", "path": path}
            return func
        return decorator
