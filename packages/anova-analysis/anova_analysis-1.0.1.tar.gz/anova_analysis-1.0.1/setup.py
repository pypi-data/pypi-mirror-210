from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="anova_analysis", 
        version="1.0.1",
        author=["Sarath S","Saranyadevi S"],
        author_email="insightagri10@gmail.com",
        description="A package for performing ANOVA analysis by RBD",
        license='MIT',
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        packages=find_packages(),
        url="https://github.com/Insight-deviler/anova_analysis",
        install_requires=["tabulate", "pandas"], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'ANOVA', 'RBD', 'analysis of variance'],
        classifiers= [
             "Programming Language :: Python :: 3",
             "License :: OSI Approved :: MIT License",
             "Operating System :: OS Independent",],
        python_requires = ">=3.6"
)