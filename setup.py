from setuptools import setup, find_packages

setup(
    name="arbitrage-engine",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "web3>=6.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Multi-DEX arbitrage detection and execution system",
    keywords="defi arbitrage amm ethereum",
    python_requires=">=3.8",
)
