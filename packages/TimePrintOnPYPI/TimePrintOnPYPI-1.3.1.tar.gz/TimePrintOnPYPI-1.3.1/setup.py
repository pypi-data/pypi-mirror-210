from setuptools import setup
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='TimePrintOnPYPI',
    version='1.3.1',
    description='A package for printing text with time delay between characters',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/SForces/TimePrint',
    author='Osman TUNA',
    author_email='osmntn08@gmail.com',
    license='MIT',
    packages=['TimePrint'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
)
