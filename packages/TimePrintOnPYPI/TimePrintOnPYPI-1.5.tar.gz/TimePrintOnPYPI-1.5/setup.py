from setuptools import setup
from setuptools.command.install import install

class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        print("Need Help ? Contact Me From e-mail;\nosmntn08@gmail.com")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='TimePrintOnPYPI',
    version='1.5',
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
    cmdclass={
        'install': CustomInstallCommand,
    },
)
