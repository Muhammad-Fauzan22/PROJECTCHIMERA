import threading

class SingletonMeta(type):
    """
    Metaclass ini menciptakan pola desain Singleton.
    Ini memastikan bahwa sebuah kelas hanya memiliki satu instance.
    """
    _instances = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
