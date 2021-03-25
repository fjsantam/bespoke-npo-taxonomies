---
title: "Classifiction with Bootstrapping"
author: "Francisco J. Santamarina; Eric J. van Holm"
date: "March 25, 2021"
output:
  html_document:
    keep_md: true
    df_print: paged
    theme: readable
    highlight: tango
    toc: yes
    toc_float: yes
    code_fold: show
---



Now that the [data has been cleaned and pre-processed](https://fjsantam.github.io/bespoke-npo-taxonomies/docs/Preprocessing_Replication.html), we can begin to classify the data via application of our machine learning algorithm, Naive Bayes. 

Let's load the libraries that we will be using.


```r
library( e1071 ) # for our algorithms
library( caret ) # for our confusion matrix
library( quanteda ) # for text analysis
library( pander ) # for attractive tables in rmarkdown
library( ggplot2 ) # for visualizations
library( scales ) # for visualizations
library( dplyr ) # for data wrangling
library( DT ) # for datatables
```

We will be repeating this process three times, once for each of the cleaned datasets (minimal, standard, and custom). This guide will walk through one in detail, then present the other two as single code chunks, before finally outputting an RData file with all three datasets present. 


# Preparing the data

All three datasets, or document-frequency matrices (dfm) that capture the preprocessed text data from the 2018 and 2019 IRS 1023EZ applications, can be found at this [Harvard Dataverse site](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/EO2HIM). 


## Minimal Dataset

We start by reading in the minimal dataset.


```r
dat <- read.csv( "https://dataverse.harvard.edu/api/access/datafile/4469230", 
                                       stringsAsFactors = F )
```

Preview the dataset.


```r
class( dat )
names( dat )
dim( dat )
```

### Create the "answer key" of tax-exempt purpose codes.


```r
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

### Create the "answer key" of NTEE codes. 

Names and categories are adapted from the [NCCS' website on NTEE codes](https://nccs.urban.org/project/national-taxonomy-exempt-entities-ntee-codes).


```r
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

Transform the factor variables to a set of binary variables and join the two answer keys together.


```re
ntmaj10.dummies <- model.matrix( ~ 0 + ntmaj10 )
ntmaj10.df <- data.frame( ntmaj10, ntmaj10.dummies, stringsAsFactors=F )

taxonomies <- bind_cols( taxonomies, ntmaj10.df )
```

We can also explore what the answer key looks like. 


```r
t1 <- prop.table( table( ntmaj10 ) )
t1 <- sort( t1 )
t1.y <- barplot( t1, horiz=TRUE, las=2, col="gray20" )
text( t1, t1.y, round(t1,2), pos=2, col="white", cex=0.8 )

t2 <- table( ntmaj10 ) 
t2 <- sort( t2 )
t2.y <- barplot( t2, horiz=TRUE, las=2, col="gray20" )
text( t2, t2.y, t2, pos=2, col="white", cex=0.8 )
```

We now want to bind the dfm portion of our imported dataset to the ground-truth, answer key columns that we have just identified. The following code drops other values from this full dataset. 


```r
start.of.dfm <- which( names(dat) == "text" )

dfm <- dat[ , start.of.dfm:ncol(dat) ]

dat2 <- cbind( taxonomies, dfm ) 
```

We next will convert the dataframe into a corpus object using the package "quanteda". First, assign a numeric ID to the new dataset we created, transform it into a list of character strings, and then create the corpus object.


```r
dat2$id_numeric <- 1:nrow( dat2 ) 

dat.corpus <- data.frame( lapply( dat2, as.character ), 
                          stringsAsFactors = FALSE ) 

dat.corpus <- corpus( dat.corpus, text_field = "Corpus" ) 
```

Finally, save off a copy of the corpus that is ready to be used in our bootstrapping. 


```r
dat.corpus.minimal <- dat.corpus

save( dat.corpus.minimal, file = "data/dat-corpus-minimal-clean.RData" )
```


## Standard Dataset

Repeat the steps above for the standard dataset.


```r
dat <- read.csv( "https://dataverse.harvard.edu/api/access/datafile/4469231", 
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


## Custom Dataset

Repeat the steps above for the custom dataset.


```r
dat <- read.csv( "https://dataverse.harvard.edu/api/access/datafile/4469229", 
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

Finally, save a copy of all three corpus objects in one file.


```r
save( dat.corpus.minimal, dat.corpus.standard, dat.corpus.custom, file = "data/dat-corpus-all.RData" )
```


# Classification

To apply the Naive Bayes classifier to our corpus objects, we need to load a dedicated package. Given the size of the data and the amount of time necessary to run our bootstrapping approach of 100 draws on each training dataset size, from 4,000 to 80,000 in increments of 4,000, we will use parallel computing methods. These also require dedicated packages.


```r
library( quanteda.textmodels ) # naive bayes now here as of Mar 2020
library( parallel ) # for detectCores
library( snow ) # for parallel processing
```


## Writing the Functions

To make the data more manageable, we will create functions to structure our distributed computing approach.


### create_model_dfs

The first function returns two objects, returns `dfm.train` and `dfm.test`. It creates the dataframes used in our model, one for training the algorithm and one for testing its performance against the ground-truth answer keys that we created earlier. 


```r
create_model_dfs <- function( corpus, prediction.class, 
                              training.dataset.size, testing.dataset.size )
{
  
  repeat { 
    
    #number of items to choose
    corpus.size <- ndoc( corpus ) #this should already be a corpus
    sample.size <- training.dataset.size + testing.dataset.size
    
    random.sample.ids <- sample( corpus.size,      # vector of 1:corpus.size
                                 sample.size, 
                                 replace = FALSE   # sampling without replacement
    ) 
    
    # Create objects containing which documents 
    # will be used in which dataset, testing or training
    
    id.train <- random.sample.ids[ 1:training.dataset.size ]
    id.test <- random.sample.ids[ ( training.dataset.size + 1 ):( sample.size ) ] 
    
    # draw from where last subset ended to end of object, 
    # i.e., total number of items chosen/sampled above
    
    
    # Create our training and testing DFM datasets
    dfm.train <- 
      corpus_subset( x = corpus, 
                     subset = id_numeric %in% id.train ) %>%
      dfm()
    #dfm( stem = TRUE ) #they should already be stemmed unless we are duplicating steps
    
    dfm.test <- 
      corpus_subset( x = corpus, 
                     subset = id_numeric %in% id.test ) %>%
      dfm()
    #dfm( stem = TRUE ) #they should already be stemmed unless we are duplicating steps
    
    
    # Will the docvars for dfm.train throw an error due to being "constant"?
    ## If yes, restart
    ## If no, exit the loop
    ### See: "y cannot be constant" for textmodel_nb
    ### https://rdrr.io/cran/quanteda.textmodels/src/tests/testthat/test-textmodel_nb.R
    ###see lines 117, 123:124
    ###https://github.com/quanteda/quanteda.textmodels/blob/a5c44127dc59e5fe7d06f5704a3084ae4f042891/R/textmodel_nb.R
    # AND:
    # Do both the training and testing datasets 
    # contain some of the outcome class (at least one instance)?
    ## If yes, exit the loop
    ## If no, restart
    
    if(
      #stats::var(as.numeric(y), na.rm = TRUE) == 0 #What the function tests for
      stats::var( as.numeric( as.factor( docvars( dfm.train, prediction.class ) ) ), na.rm = TRUE ) != 0  & 
      #stats::var( as.numeric( factor( docvars( dfm.test, prediction.class ) ) ) ) > 0 
      sum( as.numeric( docvars( dfm.train, prediction.class ) ) ) > 0 & 
      sum( as.numeric( docvars( dfm.test, prediction.class ) ) ) > 0 )
    { break }

    
    
  } # exit the repeat loop
  
  return( list(dfm.train,dfm.test) )
  
}
```


### calc_model_fit

The second function takes the two datasets and, for a given prediction class (in our case, a single NPO taxonomy code), returns `fit.stats`, the statistics as to how well the trained algorithm was able to fit to the data - in other words, the performance of the algorithm for the given training and testing datasets. 


```r
calc_model_fit <- function( dfm.train, dfm.test, prediction.class )
{
  
  training.dataset.size <- ndoc( dfm.train )
  
  # x is the dfm on which the model will be fit
  # y is a data frame of document level variables, consisting of:
  # the corpus/dfm object whose document-level variables will be set
  # the document-level variable name
  
  nb.fitted.model <- textmodel_nb( dfm.train,   
                                   docvars( dfm.train, prediction.class )
  ) 
  
  #}, error = function( err ){cat("ERROR :",conditionMessage(err), "\n")} #TESTING:
  #) #TESTING:
  #x <- x + 1 #TESTING:
  # if( is.null( nb.fitted.model) == F ){ break } #TESTING:
  
  #}
  
  # for the test set, only keep the values stored in the training set;
  # necessary to have congruent matrices when creating predictions 
  
  dfm.predict.ready <- dfm_select( dfm.test, pattern = dfm.train, selection="keep" ) 
  
  #makes a vector of the variable string from the identified dfm object
  actual_class <- docvars( dfm.predict.ready, prediction.class ) 
  
  #given the model, predict the likelihood of the data from the test set being a given value 
  predicted_class <- predict( nb.fitted.model, newdata = dfm.predict.ready ) 
  
  # a is rows
  # b is columns, 
  # https://www.statmethods.net/stats/frequencies.html
  
  tab_class <- prop.table( table( predicted_class, actual_class  ) )
  
  
  #create proportion table, entries as fraction of marginal table
  ##### PLEASE CONFIRM ORDERING OF ROWS AND COLUMNS: 
  ###### Given the language used in confusionMatrix help, 
  ###### it seems as though predictions should be rows and actual columns
  ###### I switched the order of the variables around accordingly
  #other mode options include "sens_spec", "prec_recall"
  
  
  cm <- confusionMatrix( tab_class, mode = "everything" ) 
  
  
  cm.as.csv <- as.data.frame(t(data.frame(cbind(t(cm$byClass),t(cm$overall)))))
  names( cm.as.csv ) <- "metric.value"
  
  fit.stats <- data.frame( n.train = training.dataset.size,  
                           n.predict = testing.dataset.size,
                           n.predict.class = sum(actual_class==1),
                           prediction.class = prediction.class, 
                           metric.type = rownames( cm.as.csv ),
                           cm.as.csv )
  
  return( fit.stats )
}
```


### bootstrap_nb

The third function calculates the predictive accuracy of the model repeatedly, for a given training dataset size, and stores those results in a list. This function returns a list that contains the bootstrapped results, `bs.results.list`, for a given training dataset size.


```r
########## BOOTSTRAP FUNCTION

# for each level of training dataset size
# calculate the predictive accuracy of the
# model repeatedly and store results in a list

bootstrap_nb <- function( corpus, 
                          prediction.class, 
                          training.dataset.size, 
                          testing.dataset.size,
                          num.bootstraps )
  
{
  bs.results.list <- list()
  
  for( j in 1:num.bootstraps )
  {
    
    dfm.list <- create_model_dfs( corpus, prediction.class, 
                                  training.dataset.size, 
                                  testing.dataset.size )
    dfm.train <- dfm.list[[1]]
    dfm.test  <- dfm.list[[2]]
    
    fit.stats.df <- calc_model_fit( dfm.train, dfm.test, 
                                    prediction.class )
    
    bs.results.list[[ j ]] <- fit.stats.df
    
  }
  
  #return( results.list )
  return( bs.results.list )
  
}
```


### bootstrap_increments_cluster

The fourth function iterates "bootstrap_nb" across training dataset sizes, based on the number of increments: maximum training dataset size, in our case 80,000 observations, divided by the number of observations that we want to increment the training dataset size by, in our case 4,000 observations. This function returns the object `results.list` which reports the bootstrapped results by the number of increments (or level of the training dataset size). This function was slightly modified from a previous project to function in a cluster computing/distributed environment. 


```r
bootstrap_increments_cluster <- function( corpus.name, #must be a character value
                                  training.dataset.size.increment, 
                                  num.increments,
                                  prediction.class, 
                                  testing.dataset.size )
{
  corpus <- get( corpus.name ) #assumes character value
  #corpus.size <- ndoc( corpus )
  
  results.list <- list()
  print( paste0( "Number of Increments: ", num.increments ) )
  
  for( i in 1:num.increments )
  {
    print( paste0( "Increment ", i, " of ", num.increments ) )
    training.dataset.size <- training.dataset.size.increment  * i 
    bs.results <- bootstrap_nb( corpus,  
                                prediction.class, 
                                training.dataset.size, 
                                testing.dataset.size,
                                num.bootstraps )
    
    results.list <- append( results.list, bs.results )
    
  }
  
  return( results.list )
  
}
```

### cluster_wrapper

The fifth function is a wrapper that allows us to distribute the processing of the previous functions per the combination of tax-exempt or NTEE purpose code (a.k.a., prediction class or p.class) and the dataset (minimal, standard, custom). This distribution is the linchpin of the cluster computing method presented in the next section. 


```r
cluster_wrapper <- function( x, dat.combinations, #must be character values
                             training.dataset.size.increment, 
                             num.increments,
                             testing.dataset.size )
                             #num.bootstraps ) #set this instead in the global environ
{ 
  
  corpus.name <- dat.combinations[ x, 1 ]
  prediction.class <- dat.combinations[ x, 2 ]
  
  
  
  print( "#############################" )  
  print( paste0( "####   ", toupper( corpus.name ) ) )
  print( "#############################" )
  
  
    
  print( "##################" )  
  print( paste0( "####   ", toupper( prediction.class ) ) )
  print( "##################" )
  
  
  results.list <- 
    bootstrap_increments_cluster( training.dataset.size.increment=training.dataset.size.increment, 
                                  num.increments=num.increments,
                                  corpus=corpus.name, 
                                  prediction.class=prediction.class,
                                  testing.dataset.size = testing.dataset.size )
  
  df <- dplyr::bind_rows( results.list )
  
  saveRDS( df, paste0( corpus.name,
                       ".bs.results.", 
                       prediction.class, 
                       ".rds" ) )
  


  
} #end function
```


## Preparing the Environment

The next section assumes that you have all three corpus objects in the global environment, for example by importing the `dat-corpus-all.RData` object created earlier.


```r
load( "data/dat-corpus-all.RData" )
```

### Global Environment

Establish some variables and parameters in the global environment of the active, current R session. 

#### Identifying combinations

To be sure that our corpus objects are present and will be referenced correctly, we can check the global environment and create an object to reference the 3 corpus objects.


```r
sort( names( as.list(.GlobalEnv))  )

corpus.names <- grep( "dat\\.", sort( names( as.list(.GlobalEnv))  ), value = TRUE)
corpus.names
```

Let's then create a holding object for the prediction classes.


```r
p.class <- c("Orgpurposecharitable", "Orgpurposereligious", "Orgpurposeeducational",
             "Orgpurposescientific", "Orgpurposeliterary", "Orgpurposepublicsafety",
             "Orgpurposeamateursports", "Orgpurposecrueltyprevention",  
             "Donatefundsyes", "Onethirdsupportpublic", "Onethirdsupportgifts", 
             "Disasterreliefyes",  "ntmaj10art", "ntmaj10edu", "ntmaj10env", 
             "ntmaj10health", "ntmaj10hserv", "ntmaj10int", "ntmaj10mutual", 
             "ntmaj10public", "ntmaj10rel", "ntmaj10unknown")
```

Now let's combine the two unique sets that we have just identified, to create an object that identifies each unique combination of prediction classes and corpus objects. 


```r
dat.combinations <- as.data.frame( cbind( corpus.names[ 1 ], p.class ) )
dat.combinations <- rbind( dat.combinations,
                           cbind( corpus.names[ 2 ], p.class)
                           )
dat.combinations <- rbind( dat.combinations,
                           cbind( corpus.names[ 3 ], p.class)
)
names( dat.combinations ) <- c("corpus.names", "p.class")
dim( dat.combinations ) #should be 66 rows x 2 columns
```


#### Create dedicated folder

Create a dedicated folder for the output of the clustered computations.


```r
dir.name <- paste0("BOOTS-100K.Parallel.Method ",format(Sys.time(), '%Y-%m-%d'),"real" )
dir.create( dir.name )
setwd( dir.name )
```


#### Function arguments

The code chunk below identifies the arguments used in the functions to generate the results analyzed in this project. 


```r
# Function arguments:

dat.combinations <- dat.combinations #repetitive, but here for the sake of illustration
training.dataset.size.increment <- 4000 
training.dataset.size.max <- 80000 #leave at least 20% of the dataset for testing
num.increments <- training.dataset.size.max / training.dataset.size.increment
testing.dataset.size <- 20000
num.bootstraps <- 100
#the parallelizing code treats each variable in the metric type as a separate bootstrap
```

### Parallel Computing

We need to establish some global environment parameters for parallel computing, as well as export parameters from the global environment to the parallel, distributed environments. The code below assumes that you have access to 3 corpus objects x 22 p.classes = 66 processing cores. It thus creates 66 separate clusters. 

For this approach to parallel computing to work, certain objects must exist within each cluster: the functions created earlier, the corpus objects and other objects created earlier, the libraries that we are calling for our functions, and the name of the directory where output should be saved. 

The final line in the code chunk below produces an output allowing us to confirm if anything is missing.


```r
cores <- nrow( dat.combinations ) # number of cores to make/use
cl <- makeSOCKcluster( cores ) # create that number of clusters

#Pulling in some variables from the outermost loop
exportVars <- c( 
  #functions:
  "create_model_dfs", 
  "calc_model_fit", 
  "bootstrap_nb", 
  "bootstrap_increments_cluster", 
  "cluster_wrapper",
  
  #necessary objects
  "dat.combinations", 
  "cores",
  "cl",
  "dir.name", #need to assign working directory within each cluster

  as.character(corpus.names),
  
  #Loop function arguments
  'training.dataset.size.increment',  
  'training.dataset.size.max',
  'num.increments',  
  'testing.dataset.size', 
  "num.bootstraps"
)
clusterExport( cl, exportVars ) #need to map strings to to objects in global environment

clusterEvalQ( cl, c( 
  library( caret ), 
  library( dplyr ), 
  library( quanteda), 
  library( quanteda.textmodels ),
  setwd( dir.name ), #may show up as old directory, I don't know why
  getwd() #shows the real directory value after setting it above
  
) )

#Confirm and check contents of within cluster environment
clusterEvalQ(cl[1], sort( names( as.list(.GlobalEnv)) ) )
```


## Running the bootstrapped classifier in parallel

Now that the global environment is ready and the clusters are ready, we can bootstrapping the algorithm across training dataset sizes in a distributed way to speed up the process from weeks to hours. 

I have wrapped the function in a time tracking function, following the suggestions from [this R-Bloggers post](https://www.r-bloggers.com/2017/05/5-ways-to-measure-running-time-of-r-code/).


```r
time.cluster <-system.time( 

  clusterApplyLB(
    cl = cl,
    x = 1:nrow(dat.combinations), 
    fun = cluster_wrapper,
    #arguments
    dat.combinations=dat.combinations, 
    training.dataset.size.increment = training.dataset.size.increment,
    num.increments = num.increments,
    testing.dataset.size = testing.dataset.size
  )

) #end system.time wrapper

time.cluster
```

Once done, stop the clusters and close the connections to free up the cores for other processing tasks. 


```r
stopCluster(cl) # stop using clusters
closeAllConnections() #as a double-check
```




