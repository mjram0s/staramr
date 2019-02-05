# Version 0.4.0

* Add campylobacter support.
* Fix `read_table` deprecation warnings by replacing `read_table` with `read_csv`.

# Version 0.3.0

* Exclusion of `aac(6')-Iaa` from results by default. Added ability to override this with `--no-exclude-genes` or pass a custom list of genes to exclude from results with `--exclude-genes-file`.

# Version 0.2.2

* Fix issue where `staramr` crashes if an input contig id is a number.

# Version 0.2.1

* Minor
    * Updating default ResFinder/PointFinder databases to version from July 2018.
    * Fix regex extracting gene/variant/accession values from ResFinder/PointFinder databases.
    * Fixing a few entries in table mapping genes to phenotypes.
    * Print stderr for errors with `makeblastdb`

# Version 0.2.0

* Major
    * Inclusion of predicted resistances to antimicrobial drugs thanks to gene/drug mappings from the NARMS/CIPARS Molecular Working Group. Resistance predictions are microbiological resistances and not clinical resistances (issue #4, #6).
    * Adding a `staramr db restore-default` command to restore the default `staramr` database (issue #3).
    * Switched to using BLAST Tabular data + pandas to read BLAST results (issue #10).
    * Inverted direction of BLAST (we now BLAST the AMR gene files against the input genomes).
* Minor
    * Less verbose messages when encountering errors parsing the command-line options.
    * Able to support adding options after a list of files (e.g., `staramr search *.fasta -h` will print help docs).
    * Switched to including negative AMR results (samples with no AMR genes) by default.  Must now use parameter `--exclude-negatives` to exclude them (issue #2).
    * Only print 2 decimals in Excel output (issue #5).
    * Automatically adjust Excel cells to better fit text (issue #7).
    * Many other coding improvements (issue #11, #13 and others).

# Version 0.1.0

* Initial release.  Supports batch scanning against the ResFinder and PointFinder databases.
