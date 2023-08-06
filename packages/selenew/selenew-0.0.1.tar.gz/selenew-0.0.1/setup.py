from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='selenew',
    version='0.0.1',
    author='Toghrul Mirzayev',
    author_email='togrul.mirzoev@gmail.com',
    description='SeleNew is a framework over Selenium to simplify UI Test Automation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Topic :: Software Development :: Testing",
    ],
    install_requires=[
        'selenium>=4.4.3',
        'webdriver-manager>=3.8.5',
        'colorama>=0.4.4'
    ],
    keywords=[
        'testing',
        'selenium',
        'selenew',
        'browser',
        'ui',
        'qa'
    ],
    python_requires='>=3.7',
)
