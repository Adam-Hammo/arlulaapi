import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='arlulaapi',  
     version='1.0.2',
     author="Adam Hamilton",
     author_email="adamhammo99@gmail.com",
     description="A package to facilitate access to the Arlula Imagery Marketplace API",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/Adam-Hammo/arlulaapi.git",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )