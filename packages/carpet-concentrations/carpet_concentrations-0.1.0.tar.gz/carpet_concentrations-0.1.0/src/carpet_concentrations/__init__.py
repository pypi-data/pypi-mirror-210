"""
Core tools for the development of greenhouse gas concentration input files

These files are often called flying carpets, hence the name. Such gridded
files can be developed for use cases beyond greenhouse gas concentrations,
hence this repository should be seen as a subset of wider 'carpet'
functionality.
"""
import importlib.metadata

__version__ = importlib.metadata.version("carpet_concentrations")
