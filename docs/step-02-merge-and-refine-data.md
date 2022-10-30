---
title: "Step 02: Merge and Refine Data"
author: "Francisco J. Santamarina; Eric J. van Holm"
date: "September 03, 2021"
output:
  html_document:
    keep_md: true
    df_print: paged
    theme: readable
    highlight: tango
    toc: yes
    toc_float: yes
    code_folding: hide
---



In this tutorial document, we will review the second step, merging and refining data for our analysis of nonprofit mission statements.

*Additional information on replication steps and data for this project can be found [on this GitHub page](https://fjsantam.github.io/bespoke-npo-taxonomies/)*

# Introduction

Now that the [data has been cleaned and pre-processed](https://fjsantam.github.io/bespoke-npo-taxonomies/step-01-data-preprocessing.html), we need to merge the different datasets and refine them into a format that is appropriate for our machine learning algorithm, Naive Bayes. We also need to refine data elements that we folded into the DFM but are not yet useful for our purposes.

Let's load the libraries that we will be using. Some of these libraries will be used in future steps, as well. 


```{.r .fold-show}
library( caret ) # for our confusion matrix
library( dplyr ) # for data wrangling
library( DT ) # for datatables
library( e1071 ) # for our algorithms
library( ggplot2 ) # for visualizations
library( magrittr ) # for formatting text
library( pander ) # for attractive tables in rmarkdown
library( quanteda ) # for text analysis
library( scales ) # for visualizations
```

We will be repeating this process three times, once for each of the cleaned datasets (minimal, standard, and custom). This tutorial will walk through one in detail, then present the other two as single code chunks, before finally outputting an RData file with all three datasets present. We want to merge our data on nonprofit mission statements with information about what each nonprofit identified as their [NTEE code](https://nccs.urban.org/project/national-taxonomy-exempt-entities-ntee-codes) and their tax-exempt purpose codes.

Tax-exempt purpose codes are non-exclusive codes indicating which purpose(s) an organization selected as justification for tax exemption. When filling out [Form 1023-EZ to receive tax-exempt status](https://www.irs.gov/forms-pubs/about-form-1023-ez), an applicant can select or identify multiple tax exempt purpose codes. As summarized by the [IRS](https://www.irs.gov/charities-non-profits/charitable-purposes), 

> The exempt purposes set forth in Internal Revenue Code section 501(c)(3) are *charitable*[sic], religious, educational, scientific, literary, testing for public safety, fostering national or international amateur sports competition, and the prevention of cruelty to children or animals.  

In contrast, organizations can only select one NTEE code. The National Taxonomy of Exempt Entities (NTEE) codes are part of a system created in 1987 as a way to classify organizations that qualify for a range of exemptions, and is used by the IRS, scholars, funders, and various other actors to identify nonprofits at a glance. For additional information and issues with this taxonomy, please refer to our main paper. While NTEE codes can get vary granular, we will be aggregating them into ten major categories below.

# Preparing the data

All three datasets, which consist of document-frequency matrices (dfm) that capture the preprocessed text data from the 2018 and 2019 IRS 1023EZ applications, can be found at this [Harvard Dataverse site](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/EO2HIM). 

## "Minimal" Dataset

We start by reading in the "minimal" dataset.


```{.r .fold-show}
dat <- read.csv( "https://dataverse.harvard.edu/api/access/datafile/5028824", 
                                       stringsAsFactors = F )
```



Preview the dataset.


```r
class( dat )
```

```
## [1] "data.frame"
```

```r
head(names( dat ), 20)
```

```
##  [1] "X"                      "EIN"                    "Case.Number"           
##  [4] "Formrevision"           "Eligibilityworksheet"   "Orgname1"              
##  [7] "Orgname2"               "Address"                "City"                  
## [10] "State"                  "Zip"                    "Zippl4"                
## [13] "Accountingperiodend"    "Primarycontactname"     "Primarycontactphone"   
## [16] "Primarycontactphoneext" "Primarycontactfax"      "Userfeesubmitted"      
## [19] "Ofcrdirtrust1firstname" "Ofcrdirtrust1lastname"
```

```r
dim( dat )
```

```
## [1] 104072   2054
```

The dimensions above indicate the number of documents in our dataset and the number of terms that we are analyzing. The list of values beginning with "X" indicate the column names. You may recall that in Step 01, the last step for each dataset was to merge some of the original IRS data with the document-frequency matrix (dfm). We can see in this list some of the IRS data variables that are present for each observation.

### Create the "answer keys" 

We must know what the correct "answer" is for each observation to determine the accuracy and performance of our classifier. 

#### For tax-exempt purpose codes

We establish that answer key for the IRS tax-exempt purpose codes below. To do so, we will create a new dataset that just contains those eight columns, as well as a few others we may be interested in.


```{.r .fold-show}
taxExempt <- c( "Orgpurposecharitable", 
                "Orgpurposereligious", 
                "Orgpurposeeducational", 
                "Orgpurposescientific", 
                "Orgpurposeliterary", 
                "Orgpurposepublicsafety", 
                "Orgpurposeamateursports", 
                "Orgpurposecrueltyprevention" )

otherCats <- c( "Incorporatedstate",
                "Donatefundsyes",
                "Onethirdsupportpublic",
                "Onethirdsupportgifts",
                "Disasterreliefyes" )

taxonomies <- 
  dat %>% 
  select( taxExempt, otherCats )
```

#### For NTEE codes

Our dataset has the full NTEE codes for each nonprofit. We want to refine or compress that full set of codes, specifically that of column Nteebasic, which contains 26 unique values. A standard approach to doing so for NTEE codes is to use the major 10 groups, a list of ten categories into which each of the 26 major groups (the letter value of each NTEE code designation) is assigned. Names and categories are adapted from the [NCCS' website on NTEE codes](https://nccs.urban.org/project/national-taxonomy-exempt-entities-ntee-codes). For any observations that do not have an NTEE code, we default to assigning them to the "Unknown" category.


```{.r .fold-show}
ntmaj10 <- rep( NA, nrow(dat) )
ntmaj10[ dat$Nteebasic == "A" ] <- "art"
ntmaj10[ dat$Nteebasic == "B" ] <- "edu"
ntmaj10[ dat$Nteebasic %in% c("C","D") ] <- "env"
ntmaj10[ dat$Nteebasic %in% c("E","F","G","H")  ] <- "health"
ntmaj10[ dat$Nteebasic %in% c("I","J","K","L","M","N","O","P") ] <- "hserv"
ntmaj10[ dat$Nteebasic == "Q" ] <- "int"
ntmaj10[ dat$Nteebasic %in% c("R","S","T","U","V","W") ] <- "public"
ntmaj10[ dat$Nteebasic == "X" ] <- "rel"
ntmaj10[ dat$Nteebasic == "Y" ] <- "mutual"
ntmaj10[ dat$Nteebasic == "Z" ] <- "unknown"
ntmaj10[ is.na( dat$Nteebasic ) ] <- "unknown"
```

#### Final answer key

Transform the factor variables to a set of binary variables and join the two answer keys together.


```r
ntmaj10.dummies <- model.matrix( ~ 0 + ntmaj10 )
ntmaj10.df <- data.frame( ntmaj10, ntmaj10.dummies, stringsAsFactors=F )

taxonomies <- bind_cols( taxonomies, ntmaj10.df )
```

### Previewing Answers

We can also explore what the answer key looks like. Let's first explore each of the NTEE Major 10 categories as percentages of the total.


```r
t1 <- prop.table( table( ntmaj10 ) )
t1 <- sort( t1 )

t1.y <- barplot( t1, # data to use
                 horiz=TRUE, # draw bars left to right instead of bottom to top, with the first at the bottom
                 las=2, # label orientation
                 col="gray20", # color fill of the bars
                 xlim = c(0,0.4), # establishing the bounds of the x-axis
                 main = "Barplot of NTEE Major 10 Categories,\nAs Percent of Total" ) # main title of the visual

# Alternatively, you can use the pipe operator, %>%, from library "magrittr" to assist in turning outputs into percentages
## https://stackoverflow.com/questions/9185745/appending-sign-in-output-of-prop-table
## See post by dnlbrky
t1.sub <- c(t1[1:9]) # create a dedicated subset of the table for labels outside the bars
t1.sub[10] <- NA # if you don't do this, then R will recycle t1[1] because it wants to write 10 labels with 9 values

text( t1, t1.y, percent(t1.sub,accuracy = 0.01), pos=4, col="black", cex=0.8 ) # put the labels to the right of the end of the bar
text( t1["hserv"], t1.y, percent(t1["hserv"],accuracy = 0.01), pos=2, col="white", cex=0.8 ) # put the label to the left of the end of the bar
```

![](step-02-merge-and-refine-data_files/figure-html/unnamed-chunk-8-1.png)<!-- -->

As we see in the barplot above, Human Services nonprofits compose 39.14% of our dataset. This is not surprising, as that one category represents 8 of the 26 major groups. The smallest percentage consists of Mutual/Membership Benefit nonprofits.

We can next explore what these percentages mean, in terms of the actual count of nonprofits.


```r
t2 <- table( ntmaj10 ) 
t2 <- sort( t2 )
t2.y <- barplot( t2, horiz=TRUE, las=2, col="gray20", main = "Barplot of NTEE Major 10 Categories,\nAs Counts" )
text( t2, t2.y, t2, pos=4, col="black", cex=0.8 )
text( t2["hserv"], t2.y, t2["hserv"], pos=2, col="white", cex=0.8 ) # put the label to the left of the end of the bar
```

![](step-02-merge-and-refine-data_files/figure-html/unnamed-chunk-9-1.png)<!-- -->

We could replicate the steps above to look at the tax-exempt purpose codes, **however**: The barplots are likely to be noisy, since one organization can select anywhere from one to all eight of the codes. Rather than trying to decipher noisy data at a glance, we can perform some of that data exploration after our analysis.


### Binding answer key and dfm

We now want to bind the dfm portion of our imported "minimal" dataset to the ground-truth, answer key columns that we have just identified. The following code drops other values from this full dataset, resulting in a dataset with only the dfm and the answer keys. 


```{.r .fold-show}
start.of.dfm <- which( names(dat) == "text" )

dfm <- dat[ , start.of.dfm:ncol(dat) ]

dat2 <- cbind( taxonomies, dfm ) 
```

We next will convert the dataframe into a corpus object using the package `quanteda`. First, assign a numeric ID to the new dataset we created, transform it into a list of character strings, and then create the corpus object.


```r
dat2$id_numeric <- 1:nrow( dat2 ) 

dat.corpus <- data.frame( lapply( dat2, as.character ), 
                          stringsAsFactors = FALSE ) 

dat.corpus <- corpus( dat.corpus, text_field = "Corpus" ) 
```

Let's preview what the corpus object for the "minimal" dataset looks like.


```r
head( dat.corpus )
```

```
## Corpus consisting of 6 documents and 1,964 docvars.
## text1 :
## "kathys place center cor grieving children nonprofit corporat..."
## 
## text2 :
## "houston chapter gospel music workshop america houston chapte..."
## 
## text3 :
## "palm leaf management inc specific_purpose corporation provid..."
## 
## text4 :
## "electromagnetic safety alliance organization organized educa..."
## 
## text5 :
## "berlin bambino league non_profit youth_baseball organization..."
## 
## text6 :
## "brentwood historical society mission educate people ages his..."
```

Finally, save a copy of the corpus that is ready to be used in our bootstrapping. 


```{.r .fold-show}
dat.corpus.minimal <- dat.corpus

save( dat.corpus.minimal, file = "data/dat-corpus-minimal-clean.RData" )
```


## "Standard" Dataset

Repeat the steps above for the "standard" dataset. We start by reading in the relevant data from the Harvard Dataverse site. The code chunk below contains the steps performed earlier but presented in one place, from reading in the data through saving off the dataset containing the dfm and the answer key.


```{.r .fold-show}
#Read in the data
dat <- read.csv( "https://dataverse.harvard.edu/api/access/datafile/5028825", 
                                       stringsAsFactors = F )

#Create Answer Key for tax-exempt purpose codes
taxExempt <- c( "Orgpurposecharitable", 
                "Orgpurposereligious", 
                "Orgpurposeeducational", 
                "Orgpurposescientific", 
                "Orgpurposeliterary", 
                "Orgpurposepublicsafety", 
                "Orgpurposeamateursports", 
                "Orgpurposecrueltyprevention" )

otherCats <- c( "Incorporatedstate",
                "Donatefundsyes",
                "Onethirdsupportpublic",
                "Onethirdsupportgifts",
                "Disasterreliefyes" )

taxonomies <- 
  dat %>% 
  select( taxExempt, otherCats )

#Create Answer Key for NTEE codes
ntmaj10 <- rep( NA, nrow(dat) )
ntmaj10[ dat$Nteebasic == "A" ] <- "art"
ntmaj10[ dat$Nteebasic == "B" ] <- "edu"
ntmaj10[ dat$Nteebasic %in% c("C","D") ] <- "env"
ntmaj10[ dat$Nteebasic %in% c("E","F","G","H")  ] <- "health"
ntmaj10[ dat$Nteebasic %in% c("I","J","K","L","M","N","O","P") ] <- "hserv"
ntmaj10[ dat$Nteebasic == "Q" ] <- "int"
ntmaj10[ dat$Nteebasic %in% c("R","S","T","U","V","W") ] <- "public"
ntmaj10[ dat$Nteebasic == "X" ] <- "rel"
ntmaj10[ dat$Nteebasic == "Y" ] <- "mutual"
ntmaj10[ dat$Nteebasic == "Z" ] <- "unknown"
ntmaj10[ is.na( dat$Nteebasic ) ] <- "unknown"

#Transform NTEE factors to binary
ntmaj10.dummies <- model.matrix( ~ 0 + ntmaj10 )
ntmaj10.df <- data.frame( ntmaj10, ntmaj10.dummies, stringsAsFactors=F )

#Bind answer keys
taxonomies <- bind_cols( taxonomies, ntmaj10.df )

#Bind DFM and full answer key
start.of.dfm <- which( names(dat) == "text" )
dfm <- dat[ , start.of.dfm:ncol(dat) ]
dat2 <- cbind( taxonomies, dfm ) 

#Convert dataframe into corpus object
dat2$id_numeric <- 1:nrow( dat2 ) 
dat.corpus <- data.frame( lapply( dat2, as.character ), 
                          stringsAsFactors = FALSE ) 
dat.corpus <- corpus( dat.corpus, text_field = "Corpus" ) 

#Save copy of the data
dat.corpus.standard <- dat.corpus
save( dat.corpus.standard, file = "data/dat-corpus-standard-clean.RData" )
```


## "Custom" Dataset

Repeat the steps above for the "custom" dataset. Begin with reading in the data. Then continue with the consolidated steps to merge and refine the answer keys and "custom" dfm.


```{.r .fold-show}
#Read in the data
dat <- read.csv( "https://dataverse.harvard.edu/api/access/datafile/5028823", 
                                       stringsAsFactors = F )

#Create Answer Key for tax-exempt purpose codes
taxExempt <- c( "Orgpurposecharitable", 
                "Orgpurposereligious", 
                "Orgpurposeeducational", 
                "Orgpurposescientific", 
                "Orgpurposeliterary", 
                "Orgpurposepublicsafety", 
                "Orgpurposeamateursports", 
                "Orgpurposecrueltyprevention" )

otherCats <- c( "Incorporatedstate",
                "Donatefundsyes",
                "Onethirdsupportpublic",
                "Onethirdsupportgifts",
                "Disasterreliefyes" )

taxonomies <- 
  dat %>% 
  select( taxExempt, otherCats )


#Create Answer Key for NTEE codes
ntmaj10 <- rep( NA, nrow(dat) )
ntmaj10[ dat$Nteebasic == "A" ] <- "art"
ntmaj10[ dat$Nteebasic == "B" ] <- "edu"
ntmaj10[ dat$Nteebasic %in% c("C","D") ] <- "env"
ntmaj10[ dat$Nteebasic %in% c("E","F","G","H")  ] <- "health"
ntmaj10[ dat$Nteebasic %in% c("I","J","K","L","M","N","O","P") ] <- "hserv"
ntmaj10[ dat$Nteebasic == "Q" ] <- "int"
ntmaj10[ dat$Nteebasic %in% c("R","S","T","U","V","W") ] <- "public"
ntmaj10[ dat$Nteebasic == "X" ] <- "rel"
ntmaj10[ dat$Nteebasic == "Y" ] <- "mutual"
ntmaj10[ dat$Nteebasic == "Z" ] <- "unknown"
ntmaj10[ is.na( dat$Nteebasic ) ] <- "unknown"

#Transform NTEE factors to binary
ntmaj10.dummies <- model.matrix( ~ 0 + ntmaj10 )
ntmaj10.df <- data.frame( ntmaj10, ntmaj10.dummies, stringsAsFactors=F )

#Bind answer keys
taxonomies <- bind_cols( taxonomies, ntmaj10.df )

#Bind DFM and full answer key
start.of.dfm <- which( names(dat) == "text" )
dfm <- dat[ , start.of.dfm:ncol(dat) ]
dat2 <- cbind( taxonomies, dfm ) 

#Convert dataframe into corpus object
dat2$id_numeric <- 1:nrow( dat2 ) 
dat.corpus <- data.frame( lapply( dat2, as.character ), 
                          stringsAsFactors = FALSE ) 
dat.corpus <- corpus( dat.corpus, text_field = "Corpus" ) 

#Save copy of the data
dat.corpus.custom <- dat.corpus
save( dat.corpus.custom, file = "data/dat-corpus-custom-clean.RData" )
```


## Full Dataset

As we will be analyzing all three datasets relative to each other, save a copy of all three corpus objects in one file.


```{.r .fold-show}
save( dat.corpus.minimal, dat.corpus.standard, dat.corpus.custom, file = "data/dat-corpus-all.RData" )
```

***

Once this last step is done, we are now ready to apply the Naive Bayes classifier to our corpus objects. We will proceed to [Step 3: Classification with Bootstrapping](https://fjsantam.github.io/bespoke-npo-taxonomies/step-03-classification-bootstrapping). 
