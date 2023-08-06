class FileContext:
    """文件操作"""

    def __init__(self, filename, mode, **kwargs):
        self.filename = filename
        self.mode = mode
        self.kwargs = kwargs
        self.__file = None

    def __enter__(self):
        self.__file = open(file=self.filename, mode=self.mode, **self.kwargs)
        return self.__file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__file.close()
