import setuptools


setuptools.setup(
    name="bloxflipeasily", # Put your username here!
    version="0.0.2", # The version of your package!
    author="Pytronomy", # Your name here!
    description="Made by Pytronomy on youtube", # A short description here!
    packages=setuptools.find_packages(), # A list of all packages for Python to distribute!
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ], # Enter meta data into the classifiers list!
    python_requires='>=3.6', # The version requirement for Python to run your package!
)
