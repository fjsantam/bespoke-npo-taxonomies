---
layout: default
title: Replication Files
---

# Replication Files for:

#### Santamarina, F. J., Lecy, J. D., & van Holm, E.J. How To Code A Million Missions: Developing Bespoke Nonprofit Activity Codes Using Machine Learning Algorithms.

## Data Sources

IRS Exempt Organizations Form 1023-EZ Approvals - the files hosted here contain all approved 1023-EZ filings for tax exempt status filed in a year: [IRS files by year](https://www.irs.gov/charities-non-profits/exempt-organizations-form-1023-ez-approvals)

## Data Cleaning Steps

1. Download the 2018 and 2019 files because the have the field "MISSION"
   * See of the files for 2017, 2018, and 2019 [here](https://github.com/fjsantam/bespoke-npo-taxonomies/blob/main/DATA/Crosswalk%20of%20variables%20across%20all%202017-2018-2019.xlsx)
2. Dropped all organizations with "", indicating blanks, in field "MISSION"
3. Saved cleaned files as .CSV

# of observed applications:
Year | Step in Cleaning | Values
-----|------------------|-------
2018 | None, full source | 54,773
2018 | Dropped blanks | 4,861
2018 | Without blanks | 49,912
2019 | None, full source | 56,146
2019 | Dropped blanks | 2
2019 | Without blanks | 56,144

In the cleaned files, I:
* Added new column, "Nteebasic" - only reports the first letter from the 3-character "Nteecode" field
* Added new column, "Year" - contains the year of the approved filings
* Changed column "Ein" to "EIN"

## Replication Steps

### [Raw Data Files](https://github.com/lecy/political-ideology-of-nonprofits/tree/master/DATA/01-raw-data)

### [Data Steps](/CODE/01-data-steps.html)

### [Matching Republican and Democrat Supermajority Districts](/CODE/02-matching.html)

### [Comparison of Nonprofits in Matched Supermajority Districts](/CODE/03-spatial-join-nonprofits-to-vtds.R)

### Coding Mission Statements  

- [ [taxonomies + protocol](assets/mission-coding-protocols-final.pdf) ]  
- [ [coded mission statements](https://github.com/lecy/political-ideology-of-nonprofits/raw/master/DATA/03-mission-statement-data/coded-mission-statements.xlsx) ]  
- [ [intercoder reliabiility tests](https://raw.githubusercontent.com/lecy/political-ideology-of-nonprofits/master/CODE/intercoder-reliability.R) ]  

<br>

## Source Code

### [GitHub](https://github.com/fjsantam/bespoke-npo-taxonomies)





