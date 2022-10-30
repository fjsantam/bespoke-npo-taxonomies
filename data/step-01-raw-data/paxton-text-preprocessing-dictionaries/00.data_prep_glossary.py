#-------------------------------------------------------------------------------------------#
# sample Python script for performing spelling and other corrections based on glossary
# (after temporarily removing geonames, spellchecking, eyeballing, etc.)
#
## DATA:        xx
## OUTPUT:      xx
#
## AUTHORS:     Pamela Paxton and Nicholas E. Reith
## DATE:        14 March 2019
## UPDATED:     14 March 2019
#
#-------------------------------------------------------------------------------------------#

# Note: script is only a suggestion for how to use the glossary to clean mission statements.
#      It is not a complete program
# Note: prior to using the glossary we undertook other basic cleaning. 
#      The cleaning we undertook included:
# - Strip all extra white space, especially at beginning and end
# - Convert all to lower case
# - Add spaces around some punctuation
# - Remove other non-essential punctuation
# You can use our "cleantext" protocol as below or skip this step and move to glossary below
# However, please note that some of the corrections (especially the bottom 355 in the glossary)
# depend on this protocol, e.g.,  'under - represent' to 'underrepresent'

def cleantext(x):
    x = x.str.strip()  # Remove extra white space
    x = x.str.lower() # Convert to lower
    x = x.str.replace('\t',' ') # Replace tabs with spaces
    x = x.str.replace(';',' ;; ') # semicolon = 2 semicolons
    x = x.str.replace('\[sc\]', ' ;; ') # semicolon = 2 semicolons
    x = x.str.replace('\,',' ; ') # comma = semicolon
    x = x.str.replace('\[c\]',' ; ') # comma = semicolon
    x = x.str.replace('\[dq\]',' " ') # double quote with spaces
    x = x.str.replace('\[sq\]', " ' ") # single quote with spaces
    x = x.str.replace("\`", " ' ") # weird apostrophe as apostrophe with spaces
    x = x.str.replace("\'", " ' ") # apostrophe with spaces
    x = x.str.replace('\_', ' \_ ') # underscore with spaces
    x = x.str.replace('\-', ' - ') # dash with spaces
    x = x.str.replace(':', ' : ') # colon with spaces
    x = x.str.replace('!', ' ! ') # exclamation mark with spaces
    x = x.str.replace('?', ' ? ') # question mark with spaces
    x = x.str.replace('\.', ' . ') # period with spaces
    x = x.str.replace('(', ' ( ') # paren with spaces
    x = x.str.replace(')', ' ) ') # paren with spaces
    x = x.str.replace('@', ' @ ') # at with spaces
    x = x.str.replace('\$', ' $ ') # dollar with spaces
    x = x.str.replace('\*', ' * ') # asterisk with spaces
    x = x.str.replace('\&', ' & ') # and with spaces
    x = x.str.replace('\#', ' # ') # hash with spaces
    x = x.str.replace('\%', ' % ') # percent with spaces
    x = x.str.replace('\+', ' + ') # plus with spaces
    x = x.str.replace('([0-9]+)', r' \1 ') # all digits/numbers with spaces
    x = x.str.replace(r'[^0123456789abcdefghijklmnopqrstuvwxyz;"\'_\-:!?\.()@$*&#%+ ]', ' ') # replace any characters other than these with a space
    x = " " + x + " " # Add space at beginning and end
    x = x.str.replace('([ ]+)', ' ') # replace multiple spaces with 1
    return(x)


# Apply cleaning function above to mission, replace 'mission' with your variable name
df['mission'] = cleantext(df['mission']) 


#
# Next
# Correcting misspelled words and other patterns
#

# Getting glossary to correct words
gloss = pd.DataFrame(pd.read_csv('glossaryv1.csv', header=0, sep=',', \
    index_col=None, dtype='unicode')) # Import data

# Adding spaces to beginning and end of glossary
gloss['word'] = ' ' + gloss['word'] + ' '
gloss['fix'] = ' ' + gloss['fix'] + ' '

gloss.reset_index(inplace=True)

# Applyinng gloss corrections
def correctgloss(x,g):
    for i in range(0,g['index'].max()):
        print(str(i) + ': ' + str(g.iloc[i,1]) + ' -> ' + str(g.iloc[i,2]))
        x = x.str.replace(g.iloc[i,1],g.iloc[i,2])
    return x

df['mission'] = correctgloss(df['mission'],gloss)

