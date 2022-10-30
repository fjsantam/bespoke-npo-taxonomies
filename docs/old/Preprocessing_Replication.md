---
title: "Preprocessing Steps: Creating DFMs for Mission Statements"
author: "Francisco J. Santamarina; Eric J. van Holm"
date: "March 24, 2021"
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



*Additional information on replication steps and data for this project can be found [on this GitHub page](https://fjsantam.github.io/bespoke-npo-taxonomies/)*

This version of the tutorial uses the complete 2018 and 2019 approved 1023-EZ filings shared by the IRS, [located here](https://www.irs.gov/charities-non-profits/exempt-organizations-form-1023ez-approvals). The 2018 and 2019 files contain information such as mission statements and NTEE codes. The cleaned versions of the files, which we will be importing, have an additional column (Nteebasic) that just reports the first letter of the three-digit NTEE code, as well as have had applications with no mission statements (a blank value in that field) removed.


```r
library(quanteda)
```

#Preprocessing data on organization name and mission statement

Call in both datasets


```r
dat_2018 <- read.csv( "https://dataverse.harvard.edu/api/access/datafile/4468213", stringsAsFactors=F )

dat_2019 <- read.csv( "https://dataverse.harvard.edu/api/access/datafile/4468211", stringsAsFactors=F )
```

Reducing to the necessary columns and dropping any repeating observations, as determined by the unique combination of EIN, Year, and Mission values.


```r
dat_2018_2 <- dat_2018[ !duplicated( dat_2018[ , c( "EIN", "Year", "Mission" ) ] ),]
dat_2019_2 <- dat_2019[ !duplicated( dat_2019[ , c( "EIN", "Year", "Mission" ) ] ),]
```

Return a matrix showing the difference in values.


```r
dropOutput <- data.frame( 
  rbind( 
    cbind( nrow( dat_2018), nrow (dat_2019) ),
    cbind( nrow( dat_2018_2), nrow (dat_2019_2) )
  ), 
  row.names = c("Original Values", "Unique Values")
)

colnames( dropOutput ) <- c( "2018 Data", "2019 Data" )

print( "Comparison of the original count of values and the unique count of values" )
```

```
## [1] "Comparison of the original count of values and the unique count of values"
```

```r
dropOutput
```

<div data-pagedtable="false">
  <script data-pagedtable-source type="application/json">
{"columns":[{"label":[""],"name":["_rn_"],"type":[""],"align":["left"]},{"label":["2018 Data"],"name":[1],"type":["int"],"align":["right"]},{"label":["2019 Data"],"name":[2],"type":["int"],"align":["right"]}],"data":[{"1":"49912","2":"56144","_rn_":"Original Values"},{"1":"49290","2":"54782","_rn_":"Unique Values"}],"options":{"columns":{"min":{},"max":[10]},"rows":{"min":[10],"max":[10]},"pages":{}}}
  </script>
</div>


The 1023-EZ form contains text information which includes organizational name, which we will combine with the mission. We will starting by combining the two years' worth of data.


```r
mp <- rbind( dat_2018_2, dat_2019_2)
mp$text <- paste( mp$Orgname1, mp$Orgname2, mp$Mission )
mp.lim <- mp[, c("EIN", "text")]
```


In addition, we need to ensure that all variables are characters in order to change to corpus.


```r
mp.lim <- data.frame(lapply(mp.lim, as.character), stringsAsFactors=FALSE)
```

Convert data to a corpus using 'corpus' command from quanteda. `text_field` indicates which column holds the text data we want to analyze. Also creates a label for each listing in order to ensure the data is labeled through to the end of the analysis.



```r
mp.corp <- corpus(mp.lim,  text_field = "text")
```

We can look at the corpus to see how it's structured.


```r
mp.corp #return the first few values and characteristics of the corpus
```

```
## Corpus consisting of 104,072 documents and 1 docvar.
## text1 :
## "KATHYS PLACE A CENTER COR GRIEVING  CHILDREN A NONPROFIT COR..."
## 
## text2 :
## "HOUSTON CHAPTER OF THE GOSPEL MUSIC WORKSHOP OF AMERICA The ..."
## 
## text3 :
## "PALM LEAF MANAGEMENT INC   The specific purpose of this corp..."
## 
## text4 :
## "ELECTROMAGNETIC SAFETY ALLIANCE   This organization is organ..."
## 
## text5 :
## "BERLIN BAMBINO LEAGUE   Non Profit youth baseball organizati..."
## 
## text6 :
## "BRENTWOOD HISTORICAL SOCIETY   Our mission is to educate peo..."
## 
## [ reached max_ndoc ... 104,066 more documents ]
```

```r
summary(mp.corp)[1:10,]
```

<div data-pagedtable="false">
  <script data-pagedtable-source type="application/json">
{"columns":[{"label":[""],"name":["_rn_"],"type":[""],"align":["left"]},{"label":["Text"],"name":[1],"type":["chr"],"align":["left"]},{"label":["Types"],"name":[2],"type":["int"],"align":["right"]},{"label":["Tokens"],"name":[3],"type":["int"],"align":["right"]},{"label":["Sentences"],"name":[4],"type":["int"],"align":["right"]},{"label":["EIN"],"name":[5],"type":["chr"],"align":["left"]}],"data":[{"1":"text1","2":"42","3":"53","4":"3","5":"01-0641212","_rn_":"1"},{"1":"text2","2":"42","3":"51","4":"2","5":"01-0665025","_rn_":"2"},{"1":"text3","2":"34","3":"41","4":"1","5":"01-0749880","_rn_":"3"},{"1":"text4","2":"20","3":"21","4":"1","5":"01-0937599","_rn_":"4"},{"1":"text5","2":"27","3":"29","4":"1","5":"02-0450817","_rn_":"5"},{"1":"text6","2":"38","3":"50","4":"1","5":"02-0464649","_rn_":"6"},{"1":"text7","2":"20","3":"20","4":"1","5":"02-0480459","_rn_":"7"},{"1":"text8","2":"31","3":"34","4":"1","5":"02-0652330","_rn_":"8"},{"1":"text9","2":"38","3":"42","4":"1","5":"02-0660962","_rn_":"9"},{"1":"text10","2":"12","3":"12","4":"1","5":"02-0700674","_rn_":"10"}],"options":{"columns":{"min":{},"max":[10]},"rows":{"min":[10],"max":[10]},"pages":{}}}
  </script>
</div>

## Preprocessing steps before identifying Ngrams. 

We can do many of these steps quickly while converting to a document feature matrix later, but want to do them explicitly before identifying Ngrams. We make the text lower case, break into tokens, and remove stopwords.

Additional steps are inspired by those included in Pam Paxton's [mission glossary](https://www.pamelapaxton.com/990missionstatements) and [sample Python implementation code](https://www.pamelapaxton.com/s/00data_prep_glossary.py).

We will be using the "glue" package to trim leading and trailing white spaces, when present.  



```r
library( glue )

mp.corp2 <- trim( mp.corp ) # Remove leading and trailing white spaces when present

mp.corp2 <- tolower(mp.corp2) # Convert all characters to lower case

mp.corp2 <- gsub( "'", " ", mp.corp2) # Convert neutral quotation mark to space, as it may not be captured in functions below

print( "Example output after basic pre-processing:")
```

```
## [1] "Example output after basic pre-processing:"
```

```r
mp.corp2[2]
```

```
## [1] "houston chapter of the gospel music workshop of america the houston chapter of the gospel music workshop of america is a performing arts organization, which values a high standard of musical excellence, and dance. in order to achieve this purpose, this organization holds regular monthly rehearsals."
```

```r
mp.corp3 <- tokens(mp.corp2, 
                   remove_punct = TRUE, # Removes all characters in the Unicode class "Punctuation" [P]
                   remove_numbers = TRUE, # Removes tokens that are only numbers, leaves numbers if at start of words, ex. 2day
                   remove_symbols = TRUE, # Removes all characters in the Unicode class "Symbol" [S]
                   remove_separators = TRUE, #Removes all characters in the Unicode classes  "Separator" [Z] and "Control" [C]
                   split_hyphens = FALSE # Do not split words that are connected by hyphenation. "Self-aware" should be "selfaware"
                   )

#For more information about unicode classes, see here: https://en.wikipedia.org/wiki/Unicode_character_property#General_Category
#For more information on the arguments in the function token(), see here: https://quanteda.io/reference/tokens.html

print( "Example output after advanced pre-processing:")
```

```
## [1] "Example output after advanced pre-processing:"
```

```r
mp.corp3[2]
```

```
## Tokens consisting of 1 document.
## text2 :
##  [1] "houston"  "chapter"  "of"       "the"      "gospel"   "music"   
##  [7] "workshop" "of"       "america"  "the"      "houston"  "chapter" 
## [ ... and 34 more ]
```

```r
mp.corp4 <- tokens_remove( tokens(mp.corp3), 
                           c(
                             stopwords("english"), # Remove common English stopwords
                             "nbsp" # Remove any non-breaking spaces
                             ), 
                           padding  = F # Do not leave an empty string where tokens had previously existed
                           )

#For more information about English stopwords, see here: https://rdrr.io/cran/stopwords/man/stopwords.html

print( "Example output after final pre-processing to remove unwanted tokens:")
```

```
## [1] "Example output after final pre-processing to remove unwanted tokens:"
```

```r
mp.corp4[2]
```

```
## Tokens consisting of 1 document.
## text2 :
##  [1] "houston"  "chapter"  "gospel"   "music"    "workshop" "america" 
##  [7] "houston"  "chapter"  "gospel"   "music"    "workshop" "america" 
## [ ... and 17 more ]
```

# Creating the "standard" dataset 

The standard dataset consists of removing unnecessary white space, characters, common stopwords, and using a combination of automated stemming and creating ngrams. Ngrams are combinations of words that we want to treat as a single type, or class of token. Instead of treating "non profit" as "non" and "profit", we actually want to treat it as a single type. We will do so in the following steps. 

## Ngrams

We will now look at Ngrams, specifically for combinations of 2 and 3 words. We will export the lists that were produced to look over to decide what we want to capture into a dictionary. This code can be updated once we have a larger list. 

This section is broken out by ngram length, 3 words followed by 2. 

## 3-gram, or ngram of length 3


```r
myNgram3 <- tokens(mp.corp4) %>%
  tokens_ngrams(n = 3) %>%
  dfm()

myNgram3miss.df <- textstat_frequency(myNgram3)
print( "Let's look at the top 10:")
```

```
## [1] "Let's look at the top 10:"
```

```r
myNgram3miss.df[ 1:10 ]
```

<div data-pagedtable="false">
  <script data-pagedtable-source type="application/json">
{"columns":[{"label":[""],"name":["_rn_"],"type":[""],"align":["left"]},{"label":["feature"],"name":[1],"type":["chr"],"align":["left"]},{"label":["frequency"],"name":[2],"type":["dbl"],"align":["right"]},{"label":["rank"],"name":[3],"type":["int"],"align":["right"]},{"label":["docfreq"],"name":[4],"type":["dbl"],"align":["right"]},{"label":["group"],"name":[5],"type":["chr"],"align":["left"]}],"data":[{"1":"organized_exclusively_charitable","2":"1097","3":"1","4":"1097","5":"all","_rn_":"1"},{"1":"organization_s_mission","2":"1062","3":"2","4":"1060","5":"all","_rn_":"2"},{"1":"internal_revenue_code","2":"860","3":"3","4":"857","5":"all","_rn_":"3"},{"1":"c_internal_revenue","2":"766","3":"4","4":"765","5":"all","_rn_":"4"},{"1":"inc_mission_provide","2":"764","3":"5","4":"764","5":"all","_rn_":"5"},{"1":"section_c_internal","2":"722","3":"6","4":"721","5":"all","_rn_":"6"},{"1":"charitable_educational_purposes","2":"670","3":"7","4":"668","5":"all","_rn_":"7"},{"1":"exclusively_charitable_educational","2":"653","3":"8","4":"653","5":"all","_rn_":"8"},{"1":"corporation_organized_exclusively","2":"629","3":"9","4":"629","5":"all","_rn_":"9"},{"1":"improve_quality_life","2":"608","3":"10","4":"607","5":"all","_rn_":"10"}],"options":{"columns":{"min":{},"max":[10]},"rows":{"min":[10],"max":[10]},"pages":{}}}
  </script>
</div>

```r
topfeatures(myNgram3, n = 100 )
```

```
##    organized_exclusively_charitable              organization_s_mission 
##                                1097                                1062 
##               internal_revenue_code                  c_internal_revenue 
##                                 860                                 766 
##                 inc_mission_provide                  section_c_internal 
##                                 764                                 722 
##     charitable_educational_purposes  exclusively_charitable_educational 
##                                 670                                 653 
##   corporation_organized_exclusively                improve_quality_life 
##                                 629                                 608 
##                   s_mission_provide                high_school_students 
##                                 568                                 524 
##                 gospel_jesus_christ     exclusively_charitable_purposes 
##                                 519                                 492 
##    charitable_religious_educational                  inc_organization_s 
##                                 480                                 476 
##              within_meaning_section     educational_scientific_purposes 
##                                 462                                 444 
##              foundation_inc_provide                   meaning_section_c 
##                                 443                                 435 
##        provide_financial_assistance              foundation_inc_mission 
##                                 428                                 420 
##    exclusively_charitable_religious           provide_financial_support 
##                                 412                                 411 
##           inc_corporation_organized        specific_purpose_corporation 
##                                 383                                 360 
##             purposes_within_meaning        organizations_qualify_exempt 
##                                 360                                 339 
##            inc_purpose_organization    religious_educational_scientific 
##                                 335                                 332 
##  making_distributions_organizations distributions_organizations_qualify 
##                                 311                                 311 
##        qualify_exempt_organizations                  youth_young_adults 
##                                 307                                 307 
##      science_technology_engineering                 low_income_families 
##                                 302                                 301 
##     operated_exclusively_charitable      organized_operated_exclusively 
##                                 297                                 281 
##         parent_teacher_organization                 raise_funds_support 
##                                 277                                 273 
##         purposes_including_purposes  organization_organized_exclusively 
##                                 263                                 262 
##           including_purposes_making       purposes_making_distributions 
##                                 259                                 257 
##         foundation_inc_organization          amateur_sports_competition 
##                                 251                                 244 
##             inc_organization_formed                 exemption_section_c 
##                                 240                                 237 
##        exempt_organizations_section                     inc_raise_funds 
##                                 233                                 230 
##             non_profit_organization             mission_provide_support 
##                                 229                                 228 
##             inc_purpose_corporation                    booster_club_inc 
##                                 227                                 226 
##         qualified_exemption_section             organizations_section_c 
##                                 223                                 220 
##          revenue_code_corresponding            inc_mission_organization 
##                                 213                                 206 
##        purpose_organization_provide                 inc_provide_support 
##                                 205                                 203 
##          code_corresponding_section                  purposes_section_c 
##                                 199                                 197 
##        corresponding_section_future            inc_organization_provide 
##                                 197                                 192 
##      corporation_organized_operated      educational_purposes_including 
##                                 192                                 190 
##             school_parents_teachers                enhance_quality_life 
##                                 188                                 186 
##             inc_provide_educational       scientific_purposes_including 
##                                 183                                 183 
##         mission_provide_educational   charitable_educational_scientific 
##                                 177                                 176 
##               inc_provide_financial         purpose_corporation_provide 
##                                 176                                 175 
##               provide_food_clothing         organization_formed_provide 
##                                 175                                 174 
##     educational_charitable_purposes                    federal_tax_code 
##                                 167                                 167 
##                booster_club_support                  future_federal_tax 
##                                 163                                 162 
##                 mission_raise_funds          foundation_mission_provide 
##                                 161                                 161 
##              section_future_federal        mission_organization_provide 
##                                 161                                 160 
##           volunteer_fire_department          shall_operated_exclusively 
##                                 160                                 157 
##                inc_specific_purpose                  middle_high_school 
##                                 154                                 151 
##         enhance_support_educational         inc_non-profit_organization 
##                                 150                                 148 
##      support_educational_experience                high_school_football 
##                                 146                                 145 
##                 high_school_seniors        activities_including_limited 
##                                 145                                 144 
##                foundation_s_mission          relationships_among_school 
##                                 144                                 144 
##       fostering_relationships_among                among_school_parents 
##                                 143                                 142 
##                     vincent_de_paul                       inc_s_mission 
##                                 141                                 141
```

Let's see what the distribution of frequency values looks like. We will cap the y-axis at 100, to make it easier to see how many ngrams have frequencies that are less unique. Looking at the rightmost bin, only two ngrams appear more than 1,000 times each.  


```r
h1 <- hist( myNgram3miss.df$frequency , ylim = c(0, 100) )
text(h1$mids,h1$counts,labels=h1$counts, adj=c(0.5, -0.5))
```

![](Preprocessing_Replication_files/figure-html/unnamed-chunk-11-1.png)<!-- -->

```r
# Code from: https://www.datamentor.io/r-programming/histogram/
```

As seen in the histogram above, there is a big jump from just under 100 to the previous value. This roughly corresponds to the frequency values of less than 150. I'll go ahead and export a list of the ngrams of length 3 that appear at least 150 times, then reconcile them - identifying tokens that should be considered as multi-word tokens. I'll do this outside of R.


```r
write.csv( x = myNgram3miss.df[myNgram3miss.df$frequency >= 150 ],
            file = "~/ngrams_3count.csv",
            col.names = TRUE )
```

## 2-gram, or ngram of length 2

Let's repeat this process for ngrams of length 2.


```r
myNgram2 <- tokens(mp.corp4) %>%
  tokens_ngrams(n = 2) %>%
  dfm()

myNgram2miss.df <- textstat_frequency(myNgram2)
print( "Let's look at the top 10:")
```

```
## [1] "Let's look at the top 10:"
```

```r
myNgram2miss.df[ 1:10 ]
```

<div data-pagedtable="false">
  <script data-pagedtable-source type="application/json">
{"columns":[{"label":[""],"name":["_rn_"],"type":[""],"align":["left"]},{"label":["feature"],"name":[1],"type":["chr"],"align":["left"]},{"label":["frequency"],"name":[2],"type":["dbl"],"align":["right"]},{"label":["rank"],"name":[3],"type":["int"],"align":["right"]},{"label":["docfreq"],"name":[4],"type":["dbl"],"align":["right"]},{"label":["group"],"name":[5],"type":["chr"],"align":["left"]}],"data":[{"1":"high_school","2":"5116","3":"1","4":"4055","5":"all","_rn_":"1"},{"1":"inc_provide","2":"4288","3":"2","4":"4287","5":"all","_rn_":"2"},{"1":"foundation_inc","2":"3943","3":"3","4":"3654","5":"all","_rn_":"3"},{"1":"inc_mission","2":"3861","3":"4","4":"3860","5":"all","_rn_":"4"},{"1":"mission_provide","2":"3123","3":"5","4":"3119","5":"all","_rn_":"5"},{"1":"s_mission","2":"2407","3":"6","4":"2400","5":"all","_rn_":"6"},{"1":"raise_funds","2":"2161","3":"7","4":"2130","5":"all","_rn_":"7"},{"1":"inc_organization","2":"2142","3":"8","4":"2142","5":"all","_rn_":"8"},{"1":"booster_club","2":"1912","3":"9","4":"1528","5":"all","_rn_":"9"},{"1":"exclusively_charitable","2":"1841","3":"10","4":"1839","5":"all","_rn_":"10"}],"options":{"columns":{"min":{},"max":[10]},"rows":{"min":[10],"max":[10]},"pages":{}}}
  </script>
</div>

```r
topfeatures(myNgram2, n = 100 )
```

```
##               high_school               inc_provide            foundation_inc 
##                      5116                      4288                      3943 
##               inc_mission           mission_provide                 s_mission 
##                      3861                      3123                      2407 
##               raise_funds          inc_organization              booster_club 
##                      2161                      2142                      1912 
##    exclusively_charitable           provide_support    charitable_educational 
##                      1841                      1616                      1600 
##                 section_c              quality_life     organized_exclusively 
##                      1552                      1548                      1502 
##     corporation_organized            organization_s               life_skills 
##                      1491                      1374                      1340 
##             mental_health                low_income      educational_purposes 
##                      1314                      1287                      1220 
##              jesus_christ       provide_educational         financial_support 
##                      1216                      1205                      1204 
##               inc_purpose         provide_financial       charitable_purposes 
##                      1193                      1160                      1152 
##                  club_inc      purpose_organization               raise_money 
##                      1130                      1125                      1113 
##      financial_assistance               inc_promote            ministries_inc 
##                      1099                      1067                      1065 
##      individuals_families      organization_provide       organization_formed 
##                      1055                      1034                      1033 
##        community_outreach       purpose_corporation             united_states 
##                      1008                      1001                       988 
##        foundation_provide   non-profit_organization              young_adults 
##                       978                       944                       942 
##          internal_revenue      educational_programs              revenue_code 
##                       910                       905                       866 
##         community_service     community_development             food_clothing 
##                       851                       848                       840 
##         provide_education        foundation_mission         elementary_school 
##                       822                       805                       804 
##             special_needs            general_public              youth_sports 
##                       792                       792                       789 
##        provide_assistance                c_internal           local_community 
##                       783                       781                       779 
##           inc_corporation         including_limited            educate_public 
##                       774                       765                       764 
##             middle_school                non_profit           improve_quality 
##                       763                       760                       723 
##           raise_awareness           school_students   charitable_organization 
##                       717                       714                       710 
##              mission_help              young_people    organization_dedicated 
##                       702                       700                       698 
##           school_district         children_families           association_inc 
##                       689                       679                       678 
##               inc_support      charitable_religious educational_opportunities 
##                       668                       656                       652 
##              provide_safe           law_enforcement           performing_arts 
##                       651                       647                       645 
##          specific_purpose    nonprofit_organization     religious_educational 
##                       640                       639                       637 
##      mission_organization             animal_rescue                center_inc 
##                       630                       617                       616 
##            youth_baseball    educational_scientific          support_services 
##                       615                       611                       610 
##      provide_scholarships            youth_football         domestic_violence 
##                       610                       595                       577 
##                  new_york            within_meaning              provide_free 
##                       575                       573                       572 
##     organization_provides             raising_funds                 men_women 
##                       572                       563                       554 
##       scientific_purposes            less_fortunate              gospel_jesus 
##                       547                       547                       539 
##           mission_promote 
##                       537
```

Histogram of frequency values:


```r
h2 <- hist( myNgram2miss.df$frequency , ylim = c(0, 100) )
text(h2$mids,h2$counts,labels=h2$counts, adj=c(0.5, -0.5))
```

![](Preprocessing_Replication_files/figure-html/unnamed-chunk-14-1.png)<!-- -->

```r
# Code from: https://www.datamentor.io/r-programming/histogram/
```

The big jump here roughly corresponds to the frequency values of less than 600. I'll go ahead and export a list of the ngrams of length 2 that appear at least 600 times, then reconcile them outside of R.


```r
write.csv( x = myNgram2miss.df[myNgram2miss.df$frequency >= 600 ],
            file = "~/ngrams_2count.csv",
            col.names = TRUE )
```

We can see the top candidates and others with the data created. Now create a dictionary in order to identify and transform those combinations of words into a single ngram


```r
# Read in the ngram combinations identified in the exported lists
ngrams3_dict <- dictionary( list( internal_revenue_code=c('internal revenue code'),
                                  high_school_students=c('high school students'),
                                  youth_young_adults=c('youth young adults'),
                                  low_income_families=c('low income families'),
                                  parent_teacher_organization=c('parent teacher organization'),
                                  amateur_sports_competition=c('amateur sports competition'),
                                  nonprofit_organization=c('non profit organization'),
                                  federal_tax_code=c('federal tax code'),
                                  volunteer_fire_department=c('volunteer fire department'),
                                  middle_high_school=c('middle high school') ))

ngrams2_dict <- dictionary(list( high_school=c('high school'),
                                 section_c=c('section c'),
                                 quality_life=c('quality life'),
                                 organizations=c('organization s'),
                                 life_skills=c('life skills'),
                                 mental_health=c('mental health'),
                                 low_income=c('low income'),
                                 financial_assistance=c('financial assistance'),
                                 individuals_families=c('individuals families'),
                                 community_outreach=c('community outreach'),
                                 united_states=c('united states'),
                                 young_adults=c('young adults'),
                                 internal_revenue=c('internal revenue'),
                                 revenue_code=c('revenue code'),
                                 community_service=c('community service'),
                                 community_development=c('community development'),
                                 elementary_school=c('elementary school'),
                                 special_needs=c('special needs'),
                                 general_public=c('general public'),
                                 youth_sports=c('youth sports'),
                                 provide_assistance=c('provide assistance'),
                                 c_internal=c('c internal'),
                                 local_community=c('local community'),
                                 middle_school=c('middle school'),
                                 nonprofit=c('non profit'),
                                 school_students=c('school students'),
                                 charitable_organization=c('charitable organization'),
                                 young_people=c('young people'),
                                 school_district=c('school district'),
                                 children_families=c('children families'),
                                 law_enforcement=c('law enforcement'),
                                 specific_purpose=c('specific purpose'),
                                 nonprofit_organization=c('nonprofit organization','non-profit organization'), 
                                 animal_rescue=c('animal rescue'), 
                                 youth_baseball=c('youth baseball'), 
                                 support_services=c('support services') ))
                           
mp.corp5 <- tokens_compound(mp.corp4, pattern = ngrams3_dict)
mp.corp6 <- tokens_compound(mp.corp5, pattern = ngrams2_dict)
mp.corp7 <- sapply(mp.corp6, paste, collapse=c(" ", "  "))
```

converting to a document frequency matrix as a final step, and removing stems.


```r
mp.dfm <- dfm(mp.corp7,
                   stem = T)
mp.dfm
```

```
## Document-feature matrix of: 104,072 documents, 59,695 features (100.0% sparse).
##        features
## docs    kathi place center cor griev children nonprofit corpor provid
##   text1     1     1      1   1     1        3         1      1      4
##   text2     0     0      0   0     0        0         0      0      0
##   text3     0     0      0   0     0        0         0      1      1
##   text4     0     0      0   0     0        0         0      0      0
##   text5     0     0      0   0     0        1         0      0      0
##   text6     0     0      0   0     0        0         0      0      0
##        features
## docs    support_servic
##   text1              1
##   text2              0
##   text3              0
##   text4              0
##   text5              0
##   text6              0
## [ reached max_ndoc ... 104,066 more documents, reached max_nfeat ... 59,685 more features ]
```

```r
topfeatures(mp.dfm, 20)
```

```
##    provid       inc      educ communiti     organ   support   mission     youth 
##     43410     39291     37702     32035     24073     23361     18524     16416 
##   foundat    promot   program    purpos      help    servic   develop  children 
##     15749     15208     14698     13302     13034     12822     11634     11305 
##    famili     activ      need    assist 
##     11042     10842     10256      9846
```

As seen in the output above "sparse" refers to the number of cells that have zero counts, per the documentation on the [quanteda website](https://quanteda.io/reference/sparsity.html). The value that we get above suggest a massive number of cells in our document frequency matrix that have zero counts, which we can narrow in on:


```r
sparsity( mp.dfm)
```

```
## [1] 0.9997087
```

If we try to convert the DFM to a data frame, we will have a total cell count of:


```r
prod(dim(mp.dfm))
```

```
## [1] 6212578040
```

We will follow the guidance on [this Stack Overflow page](https://stackoverflow.com/questions/58302449/what-does-the-cholmod-error-problem-too-large-means-exactly-problem-when-conv) to trim down the number of features that do not appear frequently or in many documents. We will use basic values, such as the term must appear at least 100 times and in at least 100 documents. If I didn't do this step, my instance of R and computer wouldn't let me convert the dfm to a data frame - not enough space in my RAM.


```r
mp.dfm2 <- dfm_trim(mp.dfm, min_docfreq = 100, min_termfreq = 100, verbose = TRUE)
mp.dfm2
```

```
## Document-feature matrix of: 104,072 documents, 1,855 features (99.2% sparse).
##        features
## docs    place center children nonprofit corpor provid support_servic famili
##   text1     1      1        3         1      1      4              1      1
##   text2     0      0        0         0      0      0              0      0
##   text3     0      0        0         0      1      1              0      0
##   text4     0      0        0         0      0      0              0      0
##   text5     0      0        1         0      0      0              0      0
##   text6     0      0        0         0      0      0              0      0
##        features
## docs    death parent
##   text1     1      1
##   text2     0      0
##   text3     0      0
##   text4     0      0
##   text5     0      0
##   text6     0      0
## [ reached max_ndoc ... 104,066 more documents, reached max_nfeat ... 1,845 more features ]
```

```r
print( "Previous cell count: ")
```

```
## [1] "Previous cell count: "
```

```r
prod(dim(mp.dfm))
```

```
## [1] 6212578040
```

```r
print( "New cell count: ")
```

```
## [1] "New cell count: "
```

```r
prod(dim(mp.dfm2))
```

```
## [1] 193053560
```

```r
print( "Percent Change, (new - old) / old):")
```

```
## [1] "Percent Change, (new - old) / old):"
```

```r
(prod(dim(mp.dfm2)) - prod(dim(mp.dfm)) ) / prod(dim(mp.dfm))
```

```
## [1] -0.9689254
```

Now converting the DFM to a data frame and combining with corpus and original data.


```r
mp.dfm.df <- convert(mp.dfm2, to = "data.frame")
mp.corpus.df <- as.data.frame(mp.corp7)

colnames(mp.corpus.df) <- "Corpus"


full.data <- cbind(mp, mp.corpus.df)
full.data2 <- cbind(full.data, mp.dfm.df)
```

Export the full dataset with **standard** cleaning:


```r
write.csv( x = full.data2,
            file = "~/full_data_standard_cleaning.csv",
            col.names = TRUE )
```

# Creating the "minimal" dataset: No n-grams or stemming

If you recall, mp.corp2 is a version of the corpus with minimal pre-processing done:
* leading and lagging white space was removed
* all text was put in lower case
* certain quotation marks were changed into spaces

We will generate a DFM using this mostly unprocessed dataset, and with no stemming.


```r
mp.dfm_basic <- dfm(mp.corp2,
                   stem = F)
mp.dfm_basic
```

```
## Document-feature matrix of: 104,072 documents, 75,315 features (100.0% sparse).
##        features
## docs    kathys place a center cor grieving children nonprofit corporation we
##   text1      1     1 3      1   1        1        3         1           1  3
##   text2      0     0 2      0   0        0        0         0           0  0
##   text3      0     0 0      0   0        0        0         0           1  0
##   text4      0     0 0      0   0        0        0         0           0  0
##   text5      0     0 1      0   0        0        1         0           0  0
##   text6      0     0 1      0   0        0        0         0           0  0
## [ reached max_ndoc ... 104,066 more documents, reached max_nfeat ... 75,305 more features ]
```

```r
topfeatures(mp.dfm_basic, 20)
```

```
##       and        to         ,       the         .        of        in       for 
##    186629    158015    155407    141363    118045     96231     55651     52581 
##       inc        is         a   provide community      with   support       our 
##     39276     38975     38686     30862     28973     21731     20335     20260 
##   through   mission     youth        by 
##     18625     17952     17576     17326
```

Repeating some of the same steps as before to address sparsity:


```r
mp.dfm_basic2 <- dfm_trim(mp.dfm_basic, min_docfreq = 100, min_termfreq = 100, verbose = TRUE)
mp.dfm_basic2
```

```
## Document-feature matrix of: 104,072 documents, 2,425 features (99.0% sparse).
##        features
## docs    place a center children nonprofit corporation we provide support
##   text1     1 3      1        3         1           1  3       3       2
##   text2     0 2      0        0         0           0  0       0       0
##   text3     0 0      0        0         0           1  0       1       0
##   text4     0 0      0        0         0           0  0       0       0
##   text5     0 1      0        1         0           0  0       0       0
##   text6     0 1      0        0         0           0  0       0       0
##        features
## docs    services
##   text1        2
##   text2        0
##   text3        0
##   text4        0
##   text5        0
##   text6        0
## [ reached max_ndoc ... 104,066 more documents, reached max_nfeat ... 2,415 more features ]
```

```r
print( "Previous cell count: ")
```

```
## [1] "Previous cell count: "
```

```r
prod(dim(mp.dfm_basic))
```

```
## [1] 7838182680
```

```r
print( "New cell count: ")
```

```
## [1] "New cell count: "
```

```r
prod(dim(mp.dfm_basic2))
```

```
## [1] 252374600
```

```r
print( "mp.dfm_basic2 Change, (new - old) / old):")
```

```
## [1] "mp.dfm_basic2 Change, (new - old) / old):"
```

```r
(prod(dim(mp.dfm_basic2)) - prod(dim(mp.dfm_basic)) ) / prod(dim(mp.dfm_basic))
```

```
## [1] -0.9678019
```


Now converting the mostly unprocessed DFM to a data frame and combining with corpus and original data


```r
mp.dfm_basic.df <- convert(mp.dfm_basic2, to = "data.frame")


#mp.corpus.df <- as.data.frame(mp.corp7)
#colnames(mp.corpus.df) <- "Corpus"
#full.data <- cbind(mp, mp.corpus.df)

full.data2_basic <- cbind(full.data, mp.dfm_basic.df)
```


Export the full, mostly unprocessed dataset with **minimal** cleaning:


```r
write.csv( x = full.data2,
            file = "~/full_data_minimal_cleaning.csv",
            col.names = TRUE )
```


# Creating the "custom" dataset using NPO-sector dictionary and stemming

Pam Paxton and her team have created a [nonprofit mission statement glossary and stemmer](https://www.pamelapaxton.com/990missionstatements). As compared to the custom glossary/dictionary and default stemming methods used above, let alone the minimal processing, below implements those two sector-wide and sector-specific tools.*This approach will not include the ngram consolidation.




```r
glossary <- read.csv("~/glossaryv1.csv",
            col.names = TRUE )
```

We will use the glossary to clean up misspellings during the pre-processing, after the minimal steps are done.


```r
library( glue )

mp.corp2 <- trim( mp.corp ) # Remove leading and trailing white spaces when present

mp.corp2 <- tolower(mp.corp2) # Convert all characters to lower case

mp.corp2 <- gsub( "'", " ", mp.corp2) # Convert neutral quotation mark to space, as it may not be captured in functions below

print( "Example output after basic pre-processing:")
```

```
## [1] "Example output after basic pre-processing:"
```

```r
mp.corp2[2]
```

```
## [1] "houston chapter of the gospel music workshop of america the houston chapter of the gospel music workshop of america is a performing arts organization, which values a high standard of musical excellence, and dance. in order to achieve this purpose, this organization holds regular monthly rehearsals."
```

I leverage a function that creates a custom dictionary of stems to apply the spelling corrections. 

https://cran.r-project.org/web/packages/corpus/vignettes/stemmer.html


```r
#library( textclean )
#mp.corp2.alt <- mgsub(mp.corp2, glossary$word, glossary$fix)


library( corpus )

stemmer_glossary <- new_stemmer( glossary$word, glossary$fix) # Orienting the misspelled word as the term and fix as the stem
mp.corp2.alt <- text_tokens( x = mp.corp2, stemmer = stemmer_glossary )

print( "Example output after cleaning up spelling errors:")
```

```
## [1] "Example output after cleaning up spelling errors:"
```

```r
mp.corp2.alt[2]
```

```
## [[1]]
##  [1] "houston"      "chapter"      "of"           "the"          "gospel"      
##  [6] "music"        "workshop"     "of"           "america"      "the"         
## [11] "houston"      "chapter"      "of"           "the"          "gospel"      
## [16] "music"        "workshop"     "of"           "america"      "is"          
## [21] "a"            "performing"   "arts"         "organization" ","           
## [26] "which"        "values"       "a"            "high"         "standard"    
## [31] "of"           "musical"      "excellence"   ","            "and"         
## [36] "dance"        "."            "in"           "order"        "to"          
## [41] "achieve"      "this"         "purpose"      ","            "this"        
## [46] "organization" "holds"        "regular"      "monthly"      "rehearsals"  
## [51] "."
```



```r
mp.corp3.alt <- tokens(mp.corp2.alt, 
                   remove_punct = TRUE, # Removes all characters in the Unicode class "Punctuation" [P]
                   remove_numbers = TRUE, # Removes tokens that are only numbers, leaves numbers if at start of words, ex. 2day
                   remove_symbols = TRUE, # Removes all characters in the Unicode class "Symbol" [S]
                   remove_separators = TRUE, #Removes all characters in the Unicode classes  "Separator" [Z] and "Control" [C]
                   split_hyphens = FALSE # Do not split words that are connected by hyphenation. "Self-aware" should be "selfaware"
                   )

#For more information about unicode classes, see here: https://en.wikipedia.org/wiki/Unicode_character_property#General_Category
#For more information on the arguments in the function token(), see here: https://quanteda.io/reference/tokens.html

print( "Example output after advanced pre-processing:")
```

```
## [1] "Example output after advanced pre-processing:"
```

```r
mp.corp3.alt[2]
```

```
## Tokens consisting of 1 document.
## text2 :
##  [1] "houston"  "chapter"  "of"       "the"      "gospel"   "music"   
##  [7] "workshop" "of"       "america"  "the"      "houston"  "chapter" 
## [ ... and 34 more ]
```

```r
mp.corp4.alt <- tokens_remove( tokens(mp.corp3.alt), 
                           c(
                             stopwords("english"), # Remove common English stopwords
                             "nbsp" # Remove any non-breaking spaces
                             ), 
                           padding  = F # Do not leave an empty string where tokens had previously existed
                           )

#For more information about English stopwords, see here: https://rdrr.io/cran/stopwords/man/stopwords.html

print( "Example output after final pre-processing to remove unwanted tokens:")
```

```
## [1] "Example output after final pre-processing to remove unwanted tokens:"
```

```r
mp.corp4.alt[2]
```

```
## Tokens consisting of 1 document.
## text2 :
##  [1] "houston"  "chapter"  "gospel"   "music"    "workshop" "america" 
##  [7] "houston"  "chapter"  "gospel"   "music"    "workshop" "america" 
## [ ... and 17 more ]
```

```r
#Skipping ngrams
mp.corp6.alt <- sapply(mp.corp4.alt, paste, collapse=c(" ", "  "))
```

Now to import the customer stemmers. 




```r
stems_paxton <- read.csv("~/Mission_Stemmer_v1.csv",
            col.names = TRUE )
```

We need to modify it to treat any blanks in the source file as indicating no change, rather an indicating a true blank (i.e., remove).


```r
for( i in 1:nrow(stems_paxton)){
  if( stems_paxton[ i, "Stem" ] == "" ){
    stems_paxton[ i, "Stem" ] <- stems_paxton[ i, "word" ]
  }
  
}
```

Now to implement the stemmer.


```r
stemmer_paxton <- new_stemmer( stems_paxton$word, stems_paxton$Stem) 
mp.corp6.alt <- text_tokens( x = mp.corp6.alt, stemmer = stemmer_paxton )

print( "Example output after cleaning up spelling errors:")
```

```
## [1] "Example output after cleaning up spelling errors:"
```

```r
mp.corp6.alt[2]
```

```
## $text2
##  [1] "houston"      "chapter"      "gospel"       "music"        "workshop"    
##  [6] "america"      "houston"      "chapter"      "gospel"       "music"       
## [11] "workshop"     "america"      "perform_"     "arts"         "organization"
## [16] "values"       "high"         "standard"     "music"        "excellence"  
## [21] "dance"        "order"        "achieve"      "purpose"      "organization"
## [26] "hold"         "regular"      "month"        "rehearsals"
```

```r
#Collapse down again
mp.corp7.alt <- sapply(mp.corp6.alt, paste, collapse=c(" ", "  "))


mp.dfm <- dfm(mp.corp7.alt,
                   stem = F)
mp.dfm
```

```
## Document-feature matrix of: 104,072 documents, 71,278 features (100.0% sparse).
##        features
## docs    kathys place center cor grieving children nonprofit corporate provide
##   text1      1     1      1   1        1        3         1         1       3
##   text2      0     0      0   0        0        0         0         0       0
##   text3      0     0      0   0        0        0         0         1       1
##   text4      0     0      0   0        0        0         0         0       0
##   text5      0     0      0   0        0        1         0         0       0
##   text6      0     0      0   0        0        0         0         0       0
##        features
## docs    support
##   text1       2
##   text2       0
##   text3       0
##   text4       0
##   text5       0
##   text6       0
## [ reached max_ndoc ... 104,066 more documents, reached max_nfeat ... 71,268 more features ]
```

```r
topfeatures(mp.dfm, 20)
```

```
##      provide          inc      educate    community      support organization 
##        40751        39282        37238        35911        23152        21772 
##        youth      mission   foundation       school      promote      service 
##        18133        17981        15968        15863        14300        14241 
##      program      purpose       family         help     children         need 
##        13931        13862        13091        12979        12014        11047 
##     activity      student 
##         9821         8963
```

Repeating some of the same steps as before to address sparsity:


```r
mp.dfm2 <- dfm_trim(mp.dfm, min_docfreq = 100, min_termfreq = 100, verbose = TRUE)
mp.dfm2
```

```
## Document-feature matrix of: 104,072 documents, 1,865 features (99.2% sparse).
##        features
## docs    place center children nonprofit corporate provide support service
##   text1     1      1        3         1         1       3       2       3
##   text2     0      0        0         0         0       0       0       0
##   text3     0      0        0         0         1       1       0       0
##   text4     0      0        0         0         0       0       0       0
##   text5     0      0        1         0         0       0       0       0
##   text6     0      0        0         0         0       0       0       0
##        features
## docs    family death
##   text1      1     1
##   text2      0     0
##   text3      0     0
##   text4      0     0
##   text5      0     0
##   text6      0     0
## [ reached max_ndoc ... 104,066 more documents, reached max_nfeat ... 1,855 more features ]
```

```r
print( "Previous cell count: ")
```

```
## [1] "Previous cell count: "
```

```r
prod(dim(mp.dfm))
```

```
## [1] 7418044016
```

```r
print( "New cell count: ")
```

```
## [1] "New cell count: "
```

```r
prod(dim(mp.dfm2))
```

```
## [1] 194094280
```

```r
print( "mp.dfm_basic2 Change, (new - old) / old):")
```

```
## [1] "mp.dfm_basic2 Change, (new - old) / old):"
```

```r
(prod(dim(mp.dfm2)) - prod(dim(mp.dfm)) ) / prod(dim(mp.dfm))
```

```
## [1] -0.9738348
```


Now converting the mostly unprocessed DFM to a data frame and combining with corpus and original data


```r
mp.dfm.df <- convert( mp.dfm2, to = "data.frame" )


mp.corpus.df <- as.data.frame( mp.corp7.alt )
colnames( mp.corpus.df ) <- "Corpus"
full.data <- cbind( mp, mp.corpus.df )

full.data2 <- cbind( full.data, mp.dfm.df )
```


Export the full dataset with **customized** cleaning:


```r
write.csv( x = full.data2,
            file = "~/full_data_custom_cleaning.csv",
            col.names = TRUE )
```
