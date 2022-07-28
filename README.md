# bisect

How are programming errors distributed?

This repository contains scripts used for analysing repositories to determine 
how regressions are distributed between the release directly prior to the 
commit and the commit that fixes them.

It also contains the write-up of the analysis and results.

## Useful links

1. Scripts and LaTeX source: https://github.com/llewelld/bisect
2. Dataset: https://osf.io/h5sxv/

## Process

### 1 Obtain the dataset

You can either download the same dataset used for the write-up from the Open 
Science Framework or generate your own dataset from GitHub. The former requires 
downloading a single 1.1 GB archive, the latter collects the data using the 
GitHub API. Downloading the archive will be a lot quicker.

Follow 1a or 1b below depending on which route you prefer to take.

#### 1a. Download existing dataset

Visit [https://osf.io/settings/tokens](https://osf.io/settings/tokens) and 
create a new personal access token with **osf.full_read** scope. 

You can now download the full dataset. The archive is 1.1 GB in size (4.3 GB 
when decompressed), so may take some time to download on a slower connection.

```
cd bisect
curl -X "GET" \
	https://files.de-1.osf.io/v1/resources/h5sxv/providers/osfstorage/?zip= \
  -H "Authorization: Bearer <token>"  > results.zip
```

You should then unzip the result into the root of the project folder.
```
unzip results.zip
```

#### 1b. Collect data from GitHub

This will collect data about projects on GitHub.

```
Syntax: github-find <forks|updated> <language>

	Searches github for repositories containing the requested language
	bare clones them and analysis the history and diffs to discover
	regressions and their fixes.
	<forks|updated> : order based on number of forks or most recent update time.
	<language>      : the language to search for.
```

For info about the ordering, see:
https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories

These commands will output the following files:
```
./results/index.json
./results/{language}/data{xxxxx}.json
```

Example usage:
```
./github-find.py forks c
```

### 2. Analyse the data

This will analyse the data collected from projects on GitHub.

```
Syntax: analyse-bisect <input-directory> <output-file> <metric> [a1 a2 a3]

  Reads in details of commits for different projects and applies the
  bisect algorithm to them.
  <input-directory> : a directory containing json commit files to perform the 
                      bisect algorithm on.
  <output-file>     : a file to output the results to in json format.
  <metric>          : one of "commits", "lines" or "blocks".
  [a1 a2 a3]        : optional exponential polynomial coefficients 
                      $e^{a3 x^2 + a2 x + a1}$.
```
Example usage:
```
mkdir -d stats/c
./analysis-bisect results/c/ stats/c/commits.json commits
./analysis-bisect results/c/ stats/c/lines.json lines
./analysis-bisect results/c/ stats/c/blocks.json blocks
```

This will analyse the commit data extracted from github and output a set of
distances between a regression and its surrounding releases. It will also 
perform the bisect algorithm on the regressions and record how many steps
were required to discover the regression.

The input directory should be the output directory from step 1:
```
./results/{language}
```
The output file might then be something like:
```
./stats/{language}/{measure}.json
```

### 3. Perform regression tests

The regression tests will fit three different curve types to the histogram of
distances generated by the previous step.

```
Syntax: regression-nfold.py <input-file>

  Perform n-fold cross-validation regressions.
  <input-file>   : a preprocessed stats file in json format.
```
Example usage:
```
./regression-nfold.py stats/c/commits.json
./regression-nfold.py stats/c/lines.json	
./regression-nfold.py stats/c/blocks.json
```

The input directory should be the output directory from step 2.
```
./stats/{language}/{measure}.json
```

The coefficients from the various curves will be printed to stdout.

### 4. Apply the weighted bisect algorithm

This will apply the bisect algorithm to the same results, but this time using
a distance metric weighted based on the curves generated in step 3.

```
Syntax: analyse-bisect <input-directory> <output-file> <metric> [a1 a2 a3]

  Reads in details of commits for different projects and applies the
  bisect algorithm to them.
  <input-directory> : a directory containing json commit files to perform the 
                      bisect algorithm on.
  <output-file>     : a file to output the results to in json format.
  <metric>          : one of "commits", "lines" or "blocks".
  [a1 a2 a3]        : optional exponential polynomial coefficients 
                      $e^{a3 x^2 + a2 x + a1}$.
```

Note that this uses the same script as in step 2, but this time we supply the 
coefficients of the curves.

Example usage:
```
./analyse-bisect.py results/c/ stats/c/commits-weighted.json commits \
  10.62988956267997 -95.85165636436697 91.51799274623352
./analyse-bisect.py results/c/ stats/c/lines-weighted.json lines \
  11.080415518301999 -124.71439313216983 120.23301484877652
./analyse-bisect.py results/c/ stats/c/blocks-weighted.json blocks \
  10.872833015656356 -110.3757504329785 105.9173162006048
```

This process performs the bisect algorithm based on the data output in json 
format by `github-find` to the `results/{language}` directory. By convention 
this is then stored in a file `./stats/{language}/{filename}.json`

The coefficients added as command line parameters are most likely to be those 
output by the regression tests performed in step 3.

### 5. Perform uniformity tests

The uniformity tests give an indication of whether the distribution of 
regressions is uniform.

```
Syntax: statistics <input-directory> [bucket-min]

  Generate statistics for all json analysis files (generated by 
  analysis.py) in a given directory.
  <input-directory> : the directory to read analysis json files from.
  [bucket-min]      : minimum number of buckets to allow; defaults to 3.
```

This performs tests on the results from the bisect analysis, and the regression 
data. For example it will normalise the regression distance between the 
discovery and fix points and calculate the mean and standard deviation of the 
results.

It also performs a chi-squared test to determine whether the distribution of 
normalised fix distances is uniform.

```
./statistics stats/c 100
```

### 4. Generate graphs

This steps generates a number of graphs, as used in the write-up.

```
Syntax: graphs <input-dir> <output-dir> [count-start]

  Plots a histogram of reverts against distance.
  <input-dir>   : a directory containing preprocessed stats files 
                  commits.json, lines.json and blocks.json.
  <output-dir>  : directory to save the output PNGs to, in the form 
                  graph000.png, graph001.png, ...
  [count-start] : value to start the output filename enumeration 
                  from; defaults to 0.
```

The graphs generated will have filenames `graph000.png`, `graph001.png` with 
the filename number incrementing. The `count-start` parameter can be used to
start the filename number at a number higher than zero.

Example usage
```
./graphs.py stats/c/ writeup/figures/
./graphs.py stats/javascript/ writeup/figures/ 10
```

### 5. Perform significance tests

The significance tests takes the results from applying two different bisect
algorithm types and compares them.

```
Syntax: significance-test [-q] <input-base> <intput-test>

  Perform a Wilcoxon Signed Rank significance test on the two datasets.
  [-q]          : only output the results
  <input-base>  : a json file containing regressions and bisect steps
                  using the standard distance metric.
  <input-test>  : a json file containing regressions and bisect steps
                  using a weighted distance metric.
```

This will perform a Wilcoxon Signed Rank significance test on the two sets of
data. First a two-sided test, and following that a one-sided test.

The output provides more detail about what the results mean.

The two input files should be different sets of results output by the
`analyse-bisect.py` script in steps 2 and steps 4. Since this is a paired test
the files must both be for the same language (i.e. files generated from the
same raw data).

Example usage
```
./significance-tests.py stats/c/commits.json stats/c/commits-weighted.json
./significance-tests.py stats/c/commits.json stats/c/lines-weighted.json
./significance-tests.py stats/c/commits.json stats/c/blocks-weighted.json
```

The results will be in the form of a Z statistic and a p-value, printed to 
stdout.

## Process summary

The `run-regression.sh` script performs the full process, except from step 1.
Running the script may take a lot of time and generate a lot of (mostly
uninteresting) output.

The following summarises the process, using C as an example:
```
./github-find.py forks c++
./analyse-bisect.py results/c/ stats/c/commits.json commits
./regression-nfold.py stats/c/commits.json
./analyse-bisect.py results/c/ stats/c/commits-weighted.json commits \
  10.62988956267997 -95.85165636436697 91.51799274623352
./graphs.py stats/c/ writeup/figures/
./significance-tests.py -q stats/c/commits.json stats/c/commits-weighted.json
```

## Compile the LaTeX source

The Makefile in the `writeup` folder is set up to automatically build a pdf
file from the LaTeX source.

```
cd writeup
make
xdg-open bisect.pdf
```

## Notes

The following notes may be helpful in understanding how the results were 
generated. In many cases the python scripts for a repository can be performed 
at the console instead.

These steps are for illustrative purposes. They're not used in this form in the 
actual analysis.

### Find reverts
```
git log --format="%H" --grep "revert"
```

### Show commit for tag
```
git show --format="%H" 1.8.2 | head -1
git rev-list -n 1 1.8.2
```

### List latest tag before
```
git tag --contains dcda2c6 --sort=committerdate | head -1
git describe --tag dcda2c6
```

### List earliest tag after
```
git tag --no-contains dcda2c6 --sort=committerdate | tail -1
git describe --tag --contains dcda2c6
```

### Earliest commit
```
git rev-list --max-parents=0 HEAD
```

### Latest commit
```
# HEAD
```

### Commit revert refers to
```
$r = `git log --format="%b" $i | grep -o -E "[0-9a-f]{7}|[0-9a-f]{40}"`
```

Format <tag_before> <reverted> <reverting> <tag_after>

```
for i in `git log --format="%H" --grep "revert"`; do
	r=`git log --format="%b" -1 $i | grep -o -E "[0-9a-f]{7}|[0-9a-f]{40}"`
	if [ -n "$r" ]; then
		before=`git describe --tag --first-parent --abbrev=0 $r 2>/dev/null | cut -f1 -d"~"`
		after=`git describe --tag --first-parent --abbrev=0 --contains $r 2>/dev/null | cut -f1 -d"~"`
		below=`[ -z "$before" ] && echo \`git rev-list --max-parents=0 HEAD\` || echo $before`
		above=`[ -z "$after" ] && echo "HEAD" || echo $after`
		echo `git rev-list -n 1 $below` $r $i `git rev-list -n 1 $above`
	fi
done
```

