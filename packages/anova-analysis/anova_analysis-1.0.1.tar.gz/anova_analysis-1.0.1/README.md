# ANOVA Analysis Package

The ANOVA Analysis Package is a Python package that provides functions for performing ANOVA (Analysis of Variance) analysis on experimental data.
Currently it can perform RBD analysis only

## Installation

You can install the package using pip:

```
pip install anova_analysis
```
## Usage

```
import ANOVA_RBD

#Set the replication, treatment, and file path

replication = 4
treatment = 23
file_path = "path/to/excel/file.xlsx"

# Perform ANOVA analysis

ANOVA_RBD.RBD(replication, treatment, file_path)
```
## Features

- Calculates the correction factor, total sum of squares, replication sum of squares, treatment sum of squares, and error sum of squares.
- Generates an ANOVA table with source, degrees of freedom, sum of squares, mean square, and F-values.
- Saves the results in a text file for further analysis or reporting.

## Example Dataset

- The package requires an Excel file containing the experimental data. The data should be arranged in a Randomized Block Design (RBD) format, with treatments in columns and replications in rows. 
- Please ensure that the first column contains the block or replication information.

## License
This package is licensed under the MIT License. See the LICENSE file for more information.

## Contributing
Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request on the GitHub repository.

## Authors
- Sarath S (insightagri10@gmail.com)
- Saranyadevi S

## Acknowledgements

- This package was developed as part of a research work. 
- This is based on ```Biometrical Methods in Quantitative Genetic Analysis by R.K. Singh and B.D. Chaudhary```
- I would like to thank all contributors and supporters.