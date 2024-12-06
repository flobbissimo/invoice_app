from setuptools import setup, find_packages

setup(
    name="ricevute",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "reportlab>=4.0.0",
        "pillow>=10.0.0",
    ],
    entry_points={
        "gui_scripts": [
            "ricevute=src:main",
        ],
    },
    python_requires=">=3.8",
    author="Pension Flora",
    description="Invoice generator for Pension Flora",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 