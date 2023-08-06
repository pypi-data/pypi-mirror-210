"""
处理器框架
"""
import abc


class BaseProcessor(abc.ABC):
    """
    处理器基类
    """

    def __init__(self):
        pass

    def read(self, *args, **kwargs):
        raise NotImplementedError()

    def process(self, *args, **kwargs):
        raise NotImplementedError()

    def save(self, *args, **kwargs):
        raise NotImplementedError()

    def run(self, *args, **kwargs):
        raise NotImplementedError()
