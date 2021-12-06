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

### Control file format

Suppose the control file looks like this:

```
FILENAME1.pdf
x
x
283293A1-1
2
3
x
A2-1
2
3
4
A4-1
2
x
x
382948A1-3
4
2
1
A2-1
2
3
x

FILENAME2.pdf
293842B1-1
2
3
4
5
x
B3-1
2
293832B1-1
2
3
x
```

This specifies that there are 2 PDF files called `FILENAME1.pdf` and
`FILENAME2.pdf`, and each of them is organized as listed in the lines
following it. Specifically, in `FILENAME1.pdf`, the first 2 sides of paper
should be ignored (perhaps because they're a cover sheet), and then the
next 10 sides of paper correspond to PIN number 283293, and the first 3
sides are for A1 (with the 4th side blank), followed by 4 sides for A2,
followed by 2 sides for A4. And then there are 2 sides to ignore (perhaps
for the next cover sheet). And then there are 8 sides corresponding to PIN
382948, except that they're out of order: sides 3 and 4 come first for A1,
followed by sides 2 and 1 for A1. Then A2 is in order, with sides 1, 2, 3,
with the 4th side blank.  Then the same file contains instructions for how
to split apart `FILENAME2.pdf`.

The program would automatically output a whole bunch of PDF files like:

```
283293A1.pdf
283293A2.pdf
283293A3.pdf
382948A1.pdf
382948A2.pdf
293842B1.pdf
293842B3.pdf
293832B1.pdf
```
