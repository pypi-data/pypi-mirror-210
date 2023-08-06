from setuptools import setup, find_packages

# Setting up
setup(
    name="NeuralNetworkFlow",
    version="0.0.1",
    author="PythonCoder2002",
    author_email="<adityabijapurkar@gmail.com>",
    description="Neural Network Data",
    long_description=open('README.txt').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['numpy', 'matplotlib', 'scikit-learn', 'tensorflow'],
    keywords=['python', 'neural networks', 'ann',
              'mcculloh-pitt', 'ART neural network'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
