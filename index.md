---
layout: default
title: Replication Files
---

# Replication Files for:

#### Santamarina, F. J., Lecy, J. D., & van Holm, E.J. How To Code A Million Missions: Developing Bespoke Nonprofit Activity Codes Using Machine Learning Algorithms.

## Data Sources

IRS Exempt Organizations Form 1023-EZ Approvals - the files hosted here contain all approved 1023-EZ filings for tax exempt status filed in a year: [IRS files by year](https://www.irs.gov/charities-non-profits/exempt-organizations-form-1023-ez-approvals)

For all data used and generated as part of this paper, please visit our Harvard Dataverse repository, [Replication Data for: Bespoke NPO Taxonomies](https://dataverse.harvard.edu/dataverse/bespoke-npo-taxonomies).

## Replication Steps

### Data Cleaning Steps

[Files referenced in this section](https://doi.org/10.7910/DVN/BL6XLW)

1. Download the 2018 and 2019 files because they have the field "MISSION"
   * See a crosswalk of the different variables available in the files for 2017, 2018, and 2019 [here](https://dataverse.harvard.edu/file.xhtml?fileId=4468208&version=1.1); in the repository, it is the file named "Crosswalk of variables across all 2017-2018-2019"
2. Drop all organizations with "", indicating blanks, in field "MISSION"
3. Save cleaned files as .CSV for easier import into data analysis software

### Number of observed applications, before and after cleaning

Year | Step in Cleaning | Description | Values
-----|------------------|-------------|-------
2018 | 1 | None, full source | 54,773
2018 | 2 | Dropped blanks | 4,861
2018 | 3 | Without blanks | 49,912
2019 | 1 | None, full source | 56,146
2019 | 2 | Dropped blanks | 2
2019 | 3 | Without blanks | 56,144

In the cleaned files, I:
* Added new column, "Nteebasic" - only reports the first letter from the 3-character "Nteecode" field
* Added new column, "Year" - contains the year of the approved filings
* Changed column "Ein" to "EIN"



### [Raw Data Files](https://github.com/lecy/political-ideology-of-nonprofits/tree/master/DATA/01-raw-data)

### [Data Steps](/CODE/01-data-steps.html)

### Coding Mission Statements  

For related projects, see here:

- [ [coded mission statements](https://github.com/lecy/political-ideology-of-nonprofits/raw/master/DATA/03-mission-statement-data/coded-mission-statements.xlsx) ]  
- [ [intercoder reliabiility tests](https://raw.githubusercontent.com/lecy/political-ideology-of-nonprofits/master/CODE/intercoder-reliability.R) ]  

<br>

## Source Code

### [GitHub](https://github.com/fjsantam/bespoke-npo-taxonomies)





