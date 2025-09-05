from setuptools import setup, find_packages

setup(
    name="llm_cli",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "httpx>=0.27.0",
        "typer>=0.9.0",
        "rich>=13.7.0",
        "sqlite-utils>=3.36",
        "numpy>=1.26",
    ],
    entry_points={
        "console_scripts": [
            "llm-cli=llm_cli.cli:app",
        ],
    },
)
