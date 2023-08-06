from setuptools import setup

setup(
  name = "minipkg",
  version = "1.0.0",
  description = "All the power of Python...in the palm of your hand.",
  long_description = "miniPkg is a package that implements a module named miniPy, programmed by Omer Drkić that adds loads of new features and makes Python easier to use. It adds some extension to the 'math' library and to the actual Python environment, as well as some useful data manipulation tools.",
  author = "Omer Drkić",
  author_email = "omerdrkic2501@gmail.com",
  py_modules = [
    "minipy"
  ],
  classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Win32 (MS Windows)",
    "Framework :: Jupyter",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Boost Software License 1.0 (BSL-1.0)",
    "Natural Language :: English",
    "Operating System :: Microsoft",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Interpreters",
    "Topic :: Software Development :: Libraries",
    "Typing :: Typed"
  ],
  license = "Boost Software License 1.0",
  install_requires = [
    "keyboard"
  ],
  python_requires = ">=3.10"
)