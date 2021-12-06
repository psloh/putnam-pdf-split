# putnam-pdf-split

Created by Po-Shen Loh to streamline the scanning/splitting process for
Carnegie Mellon University's rather large number of Putnam Competition
submissions in 2021.

Run like this:

```
./putnam-split.py control.txt putnam-registrants.csv out > commands.sh
```

Where:

* `control.txt` is formatted like the example in this repo;
* `putnam-registrants.csv` is the CSV spreadsheet obtained by copy-pasting
  out of the Putnam supervisor portal, where the first column contains the
  PIN numbers; and
* `out` is the directory prefix that will contain the output of `pdftk`.

This writes a list of commands to standard output, which can be executed by
running:

```
. commands.sh
```

You can look at the commands first before running, for a sanity check.
