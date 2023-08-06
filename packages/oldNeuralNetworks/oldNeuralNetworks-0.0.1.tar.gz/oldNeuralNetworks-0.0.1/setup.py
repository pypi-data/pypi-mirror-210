from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Old Neural Network models'
 
# Setting up
setup(
    name="oldNeuralNetworks",
    version=VERSION,
    author="Hrushikesh Kachgunde",
    author_email="<hrushiskachgunde@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['numpy'],
    keywords=['python', 'neural networks', 'ann', 'mcculloh-pitt', 'ART neural network'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)