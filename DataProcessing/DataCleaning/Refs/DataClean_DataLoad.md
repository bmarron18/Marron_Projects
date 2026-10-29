<!--
compile to pdf
  ==> Open Linux terminal in the directory where the .Rmd file is located
  ==> Run the one set of following lines at the Linux command line
  ==> Note that must process .tex file with XeLaTex

#################
new file name
#################

RMDFILE=DataClean_DataLoad &&
Rscript -e "require(knitr); require(markdown); require(formatR); knit('$RMDFILE.Rmd', '$RMDFILE.md')" &&
pandoc --from=markdown --output=$RMDFILE.pdf $RMDFILE.md --latex-engine=xelatex

OR

RMDFILE=Background_DataClean_DataLoad_20180407  &&
Rscript -e "require(knitr); require(markdown); require(formatR); knit('$RMDFILE.Rmd', '$RMDFILE.md')" &&
pandoc --from=markdown --output=$RMDFILE.tex $RMDFILE.md --latex-engine=xelatex --standalone
-->

<!--

https://opensource.com/article/17/2/command-line-tools-data-analysis-linux

-->


<!--
Origin Date:	20180817
-->


---
title:  |
        | Data Cleaning and Data Loading into R
author: |
        | Bruce D. Marron
        | Project No. 2018NWDS006
        | \copyright  NW Data Science, LLC, Portland, Oregon 97214
        | \date{\today}


geometry: scale=0.85
header-includes:
   - \usepackage{booktabs}
   - \usepackage{verbatim}
---

## Data Clean I
Output of datasets from Excel often contain spurious quotes, misplaced commas, non-ASCII characters, $ characters, and % characters. The dataset needs to be cleaned to fit the format of a simple comma-separated file. Simple comma separated files are kept as proprietary datasets. Note that there are Linux/Unix vs. Microsoft issues with regards to end-of-line formats as well as with character set encodings in text files:

End-of-line
* Linux/Unix uses ASCII octal 012 (LF)
* Microsoft uses ASCII octal 012 + octal 015 (CRLF)

Character set
* Linux/Unix uses UTF-8 ASCII
* Microsoft uses WINDOWS-1252 (a non-ISO extended-ASCII)

It is possible to export UTF-8 encoded text file directly from Excel. See this article https://donatstudios.com/CSV-An-Encoding-Nightmare.


Can convert an .xlsx file directly to a .csv.
Example:
```
$ ssconvert Items_sold.xlsx Items_sold.csv
```



### Get info on file
The 'file' command gives general info. The output "ASCII text, with very long lines,
with CRLF line terminators" is a Windows text file.  In modern times, ASCII is now a subset of UTF-8, not its own scheme. UTF-8 is backwards compatible with ASCII. The 'dos2unix --info' command gives the following information in this order: number of DOS line breaks, number of Unix line breaks, number of Mac line breaks, byte order mark, text or binary, file name. The 'dos2unix -idu' command gives just the number of DOS line breaks, the number of Unix line breaks.

### Change file formats, if needed
The 'iconv' command will change the ASCII character set from WINDOWS-1252 to UTF-8 and create a new file as output. The 'dos2unix' command will change the end-of-line format from CRLF to LF. A check of the changes is provided.

NB. May get " Non-ISO extended-ASCII text, with very long lines"  from Microsoft Excel. Assume it is WINDOWS-1258 encoding.


Example1:
\begin{verbatim}
$ file LastChampionData*
LastChampionData_20181120_v2.csv: ASCII text, with very long lines,
with CRLF line terminators

$ dos2unix LastChampionData*
dos2unix: converting file LastChampionData_20181120_v2.csv to Unix format...

$ file LastChampionData*
LastChampionData_20181120_v2.csv: ASCII text, with very long lines

$ file --mime-encoding LastChampionData*
LastChampionData_20181120_v2.csv: us-ascii

$ iconv -f us-ascii -t UTF-8 LastChampionData_20181120_v2.csv -o LastChampionData_20181120_v3.csv

$ file --mime-encoding LastChampionData_20181120_v3.csv
LastChampionData_20181120_v3.csv: us-ascii
\end{verbatim}


Example2:
\begin{verbatim}
$ file ROIs_FOR_BRUCE_07_28_2018.csv
$ dos2unix --info ROIs_FOR_BRUCE_07_28_2018.csv
$ dos2unix -idu ROIs_FOR_BRUCE_07_28_2018.csv
$ iconv -f WINDOWS-1252 -t UTF-8 ROIs_FOR_BRUCE_07_28_2018.csv -o ROI.csv
\end{verbatim}


Example3:
\begin{verbatim}
#!/bin/sh

TO='utf-8'

for i in <name-files \*>.txt
do
    FROM=$(file -b --mime-encoding $i)
    iconv -f $FROM -t $TO $i -o $i
done
\end{verbatim}



### Set field separators correctly and character clean (CC) a .csv file
The code below ensures that a copy of the original file (<name-of-file>.csv) is kept and new, character cleaned (CC) version is created (CC_<name-of-file>.csv)

Example:
\begin{verbatim}
1. Use 'awk' to

   * remove commas inside quotes (in titles or in numbers) then remove the quotes
$ awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) }1' /
 LastChampionData_20181120_v3.csv > CC_LastChampionData.csv

   * remove $ and % and / characters
$ awk 'BEGIN{FS=","} ; {gsub(/\$|%|\//,"",$0)}1' CC_LastChampionData.csv > tmp.csv
$ mv tmp.csv CC_LastChampionData.csv


2a. EITHER use 'tr' to

   * remove all non-printable ASCII characters (garbage characters)== !(octal 11-15 || 40-176)).
   * NB. 'tr' uses backslash to denote an octal number.
$ tr -cd '\11-\15\40-\176' < CC_LastChampionData.csv > temp.csv
$ mv temp.csv CC_LastChampionData.csv


2b. OR use 'iconv' to

   * remove all non-UTF8 characters
$ iconv -f utf-8 -t utf-8 -c file.txt

\end{verbatim}


### Remove spaces and set column names correctly
Visually inspect the data:
\begin{verbatim}
$ column -t -s "," CC_LastChampionData.csv > dataviz.csv
\end{verbatim}

\bigskip
Remove spaces in column names:
\begin{verbatim}
$ sed 's/[[:space:]]*,[[:space:]]*/,/g' CC_LastChampionData.csv > temp.csv
$ mv temp.csv CC_LastChampionData.csv
\end{verbatim}

### Open .csv in Mousepad and condense each name by hand.
After condensation, the field names can be copied and then listed to run Product 1 and Product 2. See example below.


## Load the data into R
1. Data must be located in a directory named, "data" to run Product 1 and Product 2.

2. If sep = "" (the default for read_table2) the separator is ‘white space’,
that is one or more spaces, tabs, newlines or carriage returns

3. You cannot safely convert factors directly to numeric, as.character() must be applied first. Check each column with is.factor() then coerce to numeric as necessary.

4. It is a historical anomaly that R has two names for its floating-point vectors,
double and numeric


### Option 1: Use R "Import dataset" GUI then re-name to "data"
Sample code:
```  
> library(readr)
> data <- read_csv("data/CC_LastChampion.csv", col_types = cols(`DVD Units` =
col_double(), `Max. Screens` = col_double(), `Video Units` = col_double()))
```



###Option 2: Import to R then transform
==> locate data file
```
> data_path = file.path(getwd(), "data")
> datafile = file.path(data_path, "DomROI.txt")
> data <- readr::read_table2(datafile, col_names = FALSE)
```


==> check on data type
```
> sapply(data, class)
```

==> transform
```
> data <- transform(data, DVD_Units = as.numeric("DVD Units"),
                Max_Screens = as.numeric("Max. Screens"),
                Video_Units = as.numeric ("Video Units"))
```

## Example of an initial field name list for data processing in Product 1 and Product 2:

```
Title,Distributor,ReleaseDate,
MaxScreens,
OpenGross,
PSA,
Budget,
PrintsAds,
TotalCosts,
BoxOfficeGross,
Rentals,
VideoUnits,
DVDUnits,
VideoRevenue,
DomesticAncillaries,
DomesticVoD,
DomesticROI,
ForeignBoxOfficeRevenue,
ForeignRentals,
ForeignHomeVideo,
ForeignAncillaries,
IntlRevenue,
TotalGlobalRevenue,
DistributionFees,
IncomeAfterDistFees,
LibraryValue,
GlobalROI
```



***
\copyright  NW Data Science, LLC, Portland, Oregon 97214
