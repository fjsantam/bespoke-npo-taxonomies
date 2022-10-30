---
title: "Step 03: Classification with Bootstrapping"
author: "Francisco J. Santamarina; Eric J. van Holm"
date: "September 06, 2021"
output:
  html_document:
    keep_md: true
    df_print: paged
    theme: readable
    highlight: tango
    toc: yes
    toc_float: yes
    code_fold: hide
---



In this tutorial document, we will review the third step, performing classification of nonprofit mission statements with bootstrapping and multiple training dataset sizes.

*Additional information on replication steps and data for this project can be found [on this GitHub page](https://fjsantam.github.io/bespoke-npo-taxonomies/)*

# Introduction

Now that the [data has been merged and refined](https://fjsantam.github.io/bespoke-npo-taxonomies/step-02-merge-and-refine-data.html), we can begin to classify the data via application of our machine learning algorithm, Naive Bayes. 

Let's load the libraries that we will be using.


```{.r .fold-show}
library( e1071 ) # for our algorithms
library( caret ) # for our confusion matrix
library( quanteda ) # for text analysis
library( pander ) # for attractive tables in rmarkdown
library( ggplot2 ) # for visualizations
library( scales ) # for visualizations
library( dplyr ) # for data wrangling
library( DT ) # for datatables
```

We will be repeating this process three times, once for each of the cleaned datasets ("minimal", "standard", and "custom"). This guide will walk through one in detail, then present the other two as single code chunks, before finally outputting an RData file with all three datasets present. 

To apply the Naive Bayes classifier to our corpus objects, we need to load a dedicated package. Given the size of the data and the amount of time necessary to run our bootstrapping approach of 100 draws on each training dataset size, from 4,000 to 80,000 in increments of 4,000, we will use parallel computing methods. These also require dedicated packages, in addition to the general ones we loaded earlier.


```{.r .fold-show}
library( quanteda.textmodels ) # naive bayes now here as of Mar 2020
library( parallel ) # for detectCores
library( snow ) # for parallel processing
```


# Writing the Functions

To make the analysis more manageable, we will create functions to structure our distributed computing approach. The final output will be a combination of nested functions, represented in this simple diagram:

* Each cluster runs a unique combination of prediction class (tax-exempt purpose code or NTEE code) and dataset ("minimal", "standard", "custom")
* In a given cluster,
  + For each increment, `bootstrap_increments_cluster()` (function #4) runs
    + For each bootstrap, `bootstrap_nb()` (function #3) runs
      + `create_model_dfs()` (function #1), which creates the training and testing datasets (or dataframes) used by
      + `calc_model_fit()` (function #2), which trains (or fits) the model to the provided training data and tests its accuracy on the testing data.
* `cluster_wrapper()` (function #5) runs this tree of functions across all clusters and unique combinations.



## 1. create_model_dfs

The first function returns two objects, `dfm.train` and `dfm.test`. It creates the dataframes used in our model, one for training the algorithm and one for testing its performance against the ground-truth answer keys that we created earlier. 


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


## 2. calc_model_fit

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
  
    # for the test set, only keep the values stored in the training set;
  # necessary to have congruent matrices when creating predictions 
  
  #dfm.predict.ready <- dfm_select( x = dfm.test, pattern = dfm.train, selection="keep" ) #deprecated, cannot use dfms as patterns anymore
  dfm.predict.ready <- dfm_select( x = dfm.test, 
                                   pattern = featnames(dfm.train), #pull out the names from the dfm
                                   selection="keep" ) 
  #dfm.predict.ready <- dfm_match( x = dfm.test, features = dfm.train ) #problematic because adds feature names not present in x
  # see here for guidance: https://quanteda.io/reference/dfm_match.html
  
  #makes a vector of the variable string from the identified dfm object
  actual_class <- docvars( dfm.predict.ready, prediction.class ) 
  
  #given the model, predict the likelihood of the data from the test set being a given value 
  predicted_class <- predict( nb.fitted.model, 
                              newdata = dfm.predict.ready, 
                              force = TRUE # See post by Katie Killick, Oct. 2 '19 at https://stackoverflow.com/questions/44136757/quanteda-package-naive-bayes-how-can-i-predict-on-different-featured-test-data
                              ) 
  
  # a is rows
  # b is columns, 
  # https://www.statmethods.net/stats/frequencies.html
  
  tab_class <- prop.table( table( predicted_class, actual_class  ) )
  
  
  #create proportion table, entries as fraction of marginal table
  ##### PLEASE CONFIRM ORDERING OF ROWS AND COLUMNS: 
  ###### Given the language used in confusionMatrix help, 
  ###### it seems as though predictions should be rows and reality should be columns
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


## 3. bootstrap_nb

The third function calculates the predictive accuracy of the model repeatedly, for a given training dataset size, and stores those results in a list. This function returns a list that contains the bootstrapped results, `bs.results.list`, for a given training dataset size.


```r
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


## 4. bootstrap_increments_cluster

The fourth function iterates `bootstrap_nb()` across training dataset sizes, based on the number of increments: maximum training dataset size, in our case 80,000 observations, divided by the number of observations that we want to increment the training dataset size by, in our case 4,000 observations. This function returns the object `results.list` which reports the bootstrapped results by the number of increments (or level of the training dataset size). This function was slightly modified from a previous project to function in a cluster computing/distributed environment. 


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

## 5. cluster_wrapper

The fifth function wraps together the previous functions and distribute them across processing clusters. In detail, it allows us to distribute the processing of the previous functions per the combination of tax-exempt or NTEE purpose code (a.k.a., prediction class or p.class) and the dataset ("minimal", "standard", "custom"). This distribution is the linchpin of the cluster computing method presented in the next section. This function saves the output as an .RDS file containing all performance statistics of each bootstrap and each increment by combination of p.class and corpus, meaning that the final output will be 66 unique files.


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


# Preparing the Environment

The next section assumes that you have all three corpus objects in the global environment, for example by importing the `dat-corpus-all.RData` object created earlier.


```{.r .fold-show}
load( "data/dat-corpus-all.RData" )
```

## Global Environment

Establish some variables and parameters in the global environment of the active, current R session. 

### Identifying combinations

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


### Create dedicated folder

Create a dedicated folder for the output of the clustered computations. It will be created inside of your working directory. This step is so that the 66 output files are in a recognized folder, and not mixed with the other files in your working directory.


```r
dir.name <- paste0("BOOTS-100K.Parallel.Method ",format(Sys.time(), '%Y-%m-%d') )
dir.create( dir.name )
setwd( dir.name )
```


### Function arguments

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

## Parallel Computing

We need to establish some global environment parameters for parallel computing, as well as export parameters from the global environment to the parallel, distributed environments. The code below assumes that you have access to 3 corpus objects x 22 p.classes = 66 processing cores. It thus creates 66 separate clusters. If you do not have 66 clusters, then that is not a problem. Looking at the documentation for package `snow`, we can see that `clusterApplyLB()`, the function that establishes the computing cluster and calls `cluster_wrapper()`, will just recycle nodes until all 66 jobs (each job being a unique combination of corpus object and p.class) have been run across the available nodes. The text below is quoted from the description of `clusterApplyLB()` on page 2 of [the documentation for the package `snow`](https://cran.r-project.org/web/packages/snow/snow.pdf).

> If the length p of seq is greater than the number of cluster nodes n, then the first n jobs are placed in order on the n nodes. When the first job completes, the next job is placed on the available node; this continues until all jobs are complete. Using clusterApplyLB can result in better cluster utilization than using clusterApply. However, increased communication can reduce performance. Furthermore, the node that executes a particular job is nondeterministic, which can complicate ensuring reproducibility in simulations.

For this approach to parallel computing to work, certain objects must exist within each cluster: the functions created earlier, the corpus objects and other objects imported and wrangled earlier, the libraries that we are calling for our functions, and the name of the directory where output should be saved. We also want to establish random number streams to assist in reproducibility. The author of `snow`, Luke Tierney, has provided [some guidance](http://homepage.stat.uiowa.edu/~luke/classes/295-hpc/notes/snow.pdf) on how to achieve this.

The final line in the code chunk below produces an output allowing us to review if anything is missing.


```r
cores <- nrow( dat.combinations ) # number of cores to make/use
cl <- makeSOCKcluster( cores ) # create that number of sessions/nodes

clusterSetupRNG( cl, seed = 42 ) # set random numbers
# Use the line below to see each node has random numbers:
#clusterCall(cl, runif, 3)
# Use the lines below to confirm that each node's 
# first 3 random numbers are distinct
## hold <- unlist( clusterCall(cl, runif, 3) ) #create vector of values
## dim(hold[duplicated(hold)])[1] #output should be NULL: no duplicates

#Exporting some variables from the parent session or node to the child sessions/nodes
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

clusterEvalQ( cl, c( #evaluate the following expressions on each cluster node
  library( caret ), 
  library( dplyr ), 
  library( quanteda), 
  library( quanteda.textmodels ),
  setwd( dir.name ), #may show up as old directory, I don't know why
  getwd() #shows the real directory value after setting it above
  
) )

#Review and check contents of within cluster environment
#Example below for the first node:
clusterEvalQ(cl[1], sort( names( as.list(.GlobalEnv)) ) )
```


# Running the bootstrapped classifier in parallel

Now that the global environment is ready and the clusters are ready, we can bootstrapping the algorithm across training dataset sizes in a distributed way to speed up the process from weeks to hours. 

I have wrapped the function in the time tracking function `system.time()`, following the suggestions from [this R-Bloggers post](https://www.r-bloggers.com/2017/05/5-ways-to-measure-running-time-of-r-code/).


```{.r .fold-show}
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


```{.r .fold-show}
stopCluster(cl) # stop using clusters
closeAllConnections() #as a double-check
```

For context, this process was replicated on September 4, 2021, on a [terminal server hosted by the University of Washington's Center for Studies in Demography and Ecology](https://csde.washington.edu/computing/resources/#Sim_Details). The server had 1024GB of RAM, 2.40 GHz Intel Xeon CPUs, and 40 cores (20 physical and 40 logical; [see here](https://stat.ethz.ch/R-manual/R-devel/library/parallel/html/detectCores.html) for more info on the function used to determine this from within R). It was running Windows Server 2019 (64-bit) Standard Edition.

After running the code above with the identified dataset, the output for object `time.cluster` was:


```r
user <- 1.41
system <- 0.82
elapsed <- 33464.31
time.cluster <- as.data.frame( cbind(user, system, elapsed) )
print( time.cluster, row.names = F)
```

```
##  user system  elapsed
##  1.41   0.82 33464.31
```

Referring back to [the R-Bloggers post](https://www.r-bloggers.com/2017/05/5-ways-to-measure-running-time-of-r-code/) and citing William Dunlap's explanations quoted there, 

* "user" = "CPU time spent by the current process (i.e., the current R session)" 
* "system" = CPU time spent by the operating system on related operations
* "elapsed" = count of seconds required to execute the function

Focusing on the value in "elapsed" here, to run the classifier on our dataset given our function arguments took:

| Unit | Time Elapsed | Hours Minutes Seconds |
| :---- | :------------: | ---------------------: |
| Seconds | 33,464.31 | | 
| Minutes | 557.739 | 557 minutes, 44.31 seconds |
| Hours | 9.296 | 9 hours 17 minutes 44.37 seconds |

<div align="right">*Simple converter [here](https://www.calculatorsoup.com/calculators/time/decimal-to-time-calculator.php)*</div>

***

Once this last step is done, we will proceed to [Step 4: Combine the Bootstrap Output Files](https://fjsantam.github.io/bespoke-npo-taxonomies/step-04-combine-bootstrap-output-files.html). 


