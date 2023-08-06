from typing import List

from setuptools import setup
from setuptools_rust import Binding, RustExtension
from pathlib import Path

parent_folder: Path = Path(__file__).parent.absolute()

requirements_file_path: Path = parent_folder / "requirements.txt"
with open(requirements_file_path) as fh:
    requirements: List[str] = [i for i in fh if not i.startswith(("--", "#"))]

test_requirements_file_path: Path = parent_folder / "requirements-test.txt"
with open(test_requirements_file_path) as fh:
    test_requirements: List[str] = [i for i in fh if not i.startswith(("--", "#"))]

setup(
    name="tetris_engine",
    author="Peter Lucia",
    rust_extensions=[RustExtension("tetris_engine_backend", binding=Binding.PyO3)],
    install_requires=requirements,
    test_suite='tests',
    tests_require=test_requirements,
    packages=["tetris_engine"],
    zip_safe=False,  # rust extensions are not zip safe, just like C-extensions.
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    url="https://github.com/peter-lucia/tetris_engine",
)
