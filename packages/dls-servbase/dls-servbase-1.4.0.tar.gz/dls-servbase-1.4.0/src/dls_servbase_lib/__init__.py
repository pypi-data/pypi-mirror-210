from importlib.metadata import version

__version__ = version("dls-servbase")
del version

__all__ = ["__version__"]
