---
layout: default
title: Replication Files
---

This is a website that hosts replication steps and files for the paper (under review):

> Santamarina, F. J., Lecy, J. D., & van Holm, E.J. How To Code A Million Missions: Developing Bespoke Nonprofit Activity Codes Using Machine Learning Algorithms.

# Data Sources

IRS Exempt Organizations Form 1023-EZ Approvals - the files hosted here contain all approved 1023-EZ filings for tax exempt status filed in a year: [IRS files by year](https://www.irs.gov/charities-non-profits/exempt-organizations-form-1023-ez-approvals)

For all data used and generated as part of this paper, please visit our Harvard Dataverse repository, [Replication Data for: Bespoke NPO Taxonomies](https://dataverse.harvard.edu/dataverse/bespoke-npo-taxonomies).

# Replication Steps

## Data Cleaning Steps

[Files referenced in this section](https://doi.org/10.7910/DVN/BL6XLW)

*Citation:* 
> Santamarina, Francisco, 2021, "Replication Data for: Bespoke NPO Taxonomies - raw and cleaned data from IRS", https://doi.org/10.7910/DVN/BL6XLW, Harvard Dataverse, V1, UNF:6:klFnOYKBm1lUYLa3q6g+vA== [fileUNF] 

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

## [Pre-processing steps](bespoke-npo-taxonomies/docs/Preprocessing_Replication.html)

[Files referenced in this section](https://doi.org/10.7910/DVN/EO2HIM)

*Citation:* 
> Santamarina, Francisco, 2021, "Replication Data for: Bespoke NPO Taxonomies - preprocessed data", https://doi.org/10.7910/DVN/EO2HIM, Harvard Dataverse, V1 

### Detailed overview of approach

Once the IRS raw data had the blanks removed and the three columns added, the text data needs to be cleaned. We performed three different sets of cleaning. As seen in the table below, "minimal" cleaning just standardizes the case of the text and reduces sparsity, or the number of cells in the dataset that contain a value of "0". 

minimal	| standard	| custom
--------|-----------|-------
make all text lower case | minimal steps, and | minimal steps, and
reduce sparsity by removing features that appear less than 100 times and in less than 100 documents | removing unnecessary white space and characters (punctuation, numbers, symbols, and separators) | removing unnecessary white space and characters (punctuation, numbers, symbols, and separators)
 &nbsp; | remove non-breaking spaces and common stopwords | remove non-breaking spaces and common stopwords
 &nbsp; | tokenize most common ngrams | apply Paxton’s custom dictionary (2019a) to tokenize ngrams 

For “standard,” in addition to converting all source text to lower case, we applied common text pre-processing steps, including removing unnecessary white space and characters that consist of punctuation, numbers, symbols, and separators, while concatenating characters separate by a hyphen (e.g., “self-aware” becomes “selfaware”). Non-breaking spaces and common stopwords in the English language were also removed, using quanteda’s provided dictionary (drawn from Lewis et al., 2004). We reviewed the 100 n-grams (or “short subsequences of characters”; (Manning et al., 2009, p.26), defining character k-grams) of n = 3, or 3-grams, with the highest counts. Of the top 100 3-grams, we evaluated those that had frequencies of at least 150 (after which was a large drop in frequencies), then reviewed them to determine if they made sense to be treated as one token. This process was repeated with the top 100 2-grams that had frequencies of at least 600 (after which was a large drop in frequencies). The relevant character sequences were rewritten as a single token for the appropriate 3-grams and 2-grams, in that order. Any spaces remaining within tokens were then removed, and tokens were stemmed using the default quanteda stemming tool. Stemming is an attempt to derive the roots or common character sequences of words by removing trailing characters that denote distinctions irrelevant for our study: “profess”, “professing, and “professes” would thus become “profess”, whereas “professor” and “professors” would become “professor.”
Steps for “custom” deviated for those from “standard” in two ways. Before removing non-letter characters, Paxton et al.’s (2019a) mission glossary was used to correct spelling errors and perform other corrections to the text. Instead of looking for the most common 3-grams and 2-grams to condense into single tokens and applying the default quanteda stemmer, we applied Paxton et al.’s (2019b) mission stemmer. Characteristics for all three document frequency matrices can be found in the table below.

Cleaning Approach	| Documents	| Features	| Percent Sparse
------------------|-----------|----------|----------------
Minimal	| 104,072	| 2,425	| 99.0%
Standard	| 104,072	| 1,855	| 99.2%
Custom	| 104,072	| 1,865	| 99.2%

All three datasets then went through the same, final pre-processing steps. The ground-truth values for the eight tax-exempt codes were used as-is. The NTEE codes were compiled into the 10 NTEE major Groups using the crosswalk provided by the NCCS (Jones 2019), generating 10 new columns populated with binary (0 = no, 1 = yes) values used to indicate if a document was associated with a given group. These 18 categories, in addition to five others from the original dataset (“Incorporatedstate”, “Donatefundsyes”, “Onethirdsupportpublic”, “Onethirdsupportgifts”, “Disasterreliefyes”), were merged with the corpus as columns of binary variables prior to applying analytical techniques.

## [Classification steps](bespoke-npo-taxonomies/docs/Classification_Bootstrapping_Replication)

[Files referenced in this section](https://doi.org/10.7910/DVN/4GZJSK)

*Citation:* 
> Santamarina, Francisco, 2021, "Replication Data for: Bespoke NPO Taxonomies - classification steps", https://doi.org/10.7910/DVN/4GZJSK, Harvard Dataverse, V1 

### Detailed overview of approach

The preprocessed CSV files were then subset to create new objects consisting of document frequency matrices and ground truth "answer keys" of how the organizations identified in regards to the prediction classes of tax-exempt purpose codes and NTEE variables. These files were saved off as .RData files. 

A training dataset of size N was randomly sampled from the full set of 104,072 documents in each corpus without replacement. We applied the default Naïve Bayes classifier algorithm in the quanteda package to predict taxonomy codes from the features extracted from the mission text (Benoit et al. 2018). Accuracy was determined using an independent testing dataset of 20,000 documents for all iterations. The training dataset started with 4,000 pro-processed mission statements, and increased by increments of 4,000 up to a maximum of 80,000 mission statements in the training set. Sampling was repeated 100 times in a bootstrap approach to create a distribution of accuracy scores associated with each training dataset size. The procedure was repeated for the binary variables used to represent each of the tax-exempt purpose codes, NTEE major group codes, and several additional organizational classifications from the 1023-ez metadata. We ran the bootstrapped classifier on the simulation cluster of terminal servers offered by the University of Washington’s Center for Studies in Demography and Ecology. The bootstrapped classifier was applied in parallel to the 3 corpora using the R packages snow (Tierney et al., 2018) and parallel (R Core Team, 2020) on 66 cores. Outputs were saved as .rds files for each unique combination of dataset (3) and variables (22, including 4 not analyzed in this study due to being out of scope of the main topic).

## [Raw Data Files](https://dataverse.harvard.edu/dataverse/bespoke-npo-taxonomies)

## See Also: Coding Mission Statements  

For related projects, see here:

- [ [coded mission statements](https://github.com/lecy/political-ideology-of-nonprofits/raw/master/DATA/03-mission-statement-data/coded-mission-statements.xlsx) ]  
- [ [intercoder reliabiility tests](https://raw.githubusercontent.com/lecy/political-ideology-of-nonprofits/master/CODE/intercoder-reliability.R) ]  

<br>

# Source Code

[GitHub repository](https://github.com/fjsantam/bespoke-npo-taxonomies)


# Citations

Benoit K, Watanabe K, Wang H, Nulty P, Obeng A, Müller S, Matsuo A (2018). “quanteda: An R package for the quantitative analysis of textual data.” *Journal of Open Source Software, 3*(30), 774. doi: 10.21105/joss.00774, https://quanteda.io.

Lewis, D. D., Yang, Y., Rose, T. G., & Li, F. (2004). Rcv1: A new benchmark collection for text categorization research. *Journal of machine learning research, 5*(Apr), 361-397.

Manning, C. D., Schütze, H., & Raghavan, P. (2009). *Introduction to information retrieval.* Cambridge university press. Online edition. https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf 

Paxton, P., Velasco, K., & Ressler, R.. (2019a). Form 990 Mission Glossary v.1. [Computer file]. Ann Arbor, MI: Inter-university Consortium for Political and Social Research [distributor].

Paxton, P., Velasco, K., & Ressler, R. (2019b). Form 990 Mission Stemmer v.1. [Computer file]. Ann Arbor, MI: Inter-university Consortium for Political and Social Research [distributor].

*[Link to Paxton et al.'s files](https://www.pamelapaxton.com/990missionstatements)*

R Core Team (2020). R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria. URL https://www.R-project.org/.

Tierney, L., Rossini, A.J., Li, N., & Sevcikova, H. (2018). snow: Simple Network of Workstations. R package version 0.4-3. https://CRAN.R-project.org/package=snow

