### Putnam PDF Splitter and Uploader

Created by Po-Shen Loh to streamline the scanning/splitting process for
Carnegie Mellon University's ~200 Putnam Competition participants in 2021.

### Usage instructions

## Copy list of PIN's from AoPS Putnam Supervisor Portal

1. Go to https://artofproblemsolving.com/contests/putnam/portal and log in.

2. In the **Students** section, select everything in the table (not
   including the header line starting with "PIN"), and paste into a text
   file like `aops-students-list.txt`. The Google Chrome web browser does
   the copy and paste in a way where the pasted result is tab-separated.

3. Open a spreadsheet program, import the tab-separated file, and save as a
   comma-separated file named like `putnam-registrants.csv`. That should
   have the key property that the first column of that CSV file contains
   the PIN numbers. 

## Copy list of `user_id`'s from AoPS Putnam Supervisor Portal

1. Right-click on any line in the **Student Submissions** area, which is
   where you would normally left-click and upload files. Select "Inspect"
   in the drop-down menu.

2. Google Chrome's DevTools pops up. You'll see lots of lines like:

```
<tr class="ecole-clickable edit-upload-user-id-164606">
```

3. Scroll up to the enclosing header `<tbody>`, and right-click on it.
   Select Copy > Copy outerHTML.

4. Paste the result in a text editor. It should go from `<tbody>` to
   `</tbody>`. Save the file as something like `aops-user-id.html`.

5. Extract the `PIN` <> `user_id` mapping with the Perl script in this
   repo:

./extract-aops-user-id.pl < aops-user-id.html > aops-user-id.csv

## Physically scan in student papers with a bulk scanner

This is about half of the labor-intensive work, but fortunately it is much
easier because you don't need to separately scan in separate submissions
one at a time. At CMU, we just used the department copy machine's bulk
double-sided scanning feature, which ate up pages like candy, and emailed
PDF files to us, with up to 100 pages per file.

In order to make this process more robust, we distributed cover sheets to
each student for each half of the exam:

* [putnam-cover-sheet.docx](putnam-cover-sheet.docx)

Then, the scanning person could check to make sure that all pages were
present, and in the right order. To boost efficiency, the scanning person
combined the papers in order from multiple student envelopes, separated by
our student cover sheets, such that they accumulated stacks of
approximately (but less than or equal to) 50 pieces of paper. Each of these
stacks became a PDF file.


## Create a control file which expresses what to do with all of the scanned PDF files.

This is the second half of the labor-intensive work. It's easier if you use
two monitors at the same time. Create a single `control.txt` file (possibly
with multiple people working in parallel, who then concatenate their
results), with the following format:

# Control file format

Suppose the control file looks like this:

```
a/FILENAME1.pdf
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

b/FILENAME2.pdf
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

This specifies that there are 2 PDF files called `a/FILENAME1.pdf` and
`b/FILENAME2.pdf`, and each of them is organized as listed in the lines
following it. Paths can be supplied like above, or if the PDF files are in
the current directory, no paths are required.

This control file says that in `a/FILENAME1.pdf`, the first 2 sides of
paper should be ignored (perhaps because they're a cover sheet), and then
the next 10 sides of paper correspond to PIN number 283293, and the first 3
sides are for A1 (with the 4th side blank), followed by 4 sides for A2,
followed by 2 sides for A4.  And then there are 2 sides to ignore (perhaps
for the next cover sheet).  And then there are 8 sides corresponding to PIN
382948, except that they're out of order: sides 3 and 4 come first for A1,
followed by sides 2 and 1 for A1. Then A2 is in order, with sides 1, 2, 3,
with the 4th side blank.  Then the same file contains instructions for how
to split apart `b/FILENAME2.pdf`.

It is possible to have as many PDF files specified in this control file as
you want. We had around 20 at CMU in 2021.

The program will generate a shell script that automatically outputs a whole
bunch of PDF files like:

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

To reduce typos, it is recommended to run the Python program in the next
section after specifying each PDF file, because that automatically checks
for invalid and duplicate PIN's, and skipped pages.


## Run the PDF splitter

This Python program uses the control file to create a shell script which
will conduct all of the PDF file splitting and merging:

```
./putnam-split.py control.txt putnam-registrants.csv out commands.sh
```

Where:

* `control.txt` is formatted like the example in this repo;
* `putnam-registrants.csv` is the CSV spreadsheet obtained by copy-pasting
  out of the Putnam supervisor portal, where the first column contains the
  PIN numbers; and
* `out` is the directory prefix that will contain the output of `pdftk`
  when the output shell script (`commands.sh`) is run. In the above
  example, this would create or overwrite files `out/283293A1.pdf` ...
  `out/293832B1.pdf`.

The reason why this program doesn't directly run the `pdftk` commands is
because it is quite useful to run it frequently while creating the control
file, taking advantage of its internal error-checking.

Finally, when you have finished creating the full control file, and this
Python program has executed with no errors, invoke the resulting shell
script, and sit back and enjoy as it automatically splits apart the PDF
files.

```
./commands.sh
```

(If you want, you could look at the commands first before running, for a
sanity check.)


## Run the PDF uploader

This part is still under development, but it invokes the endpoint 

```
https://artofproblemsolving.com/m/contests/dropzone_problem_upload.php
```

with a POST payload like:

```
client_updated_at: 2021-12-06 18:26:45
contest_id: 50
segment_id: 2
problem_id: 1284
round_id: 62
display_problem_id: B6
registration_id: 314159
user_id: 271828
force_create_grading_rows: true
file: (binary)
```

The POST payload is sent in the `WebKitFormBoundary` format.

Execute it like:

```
./upload-all.py aops-user-id.csv out done
```

Where:

* `aops-user-id.csv` is the CSV mapping `PIN` to `user_id` created in an
  earlier section;
* `out` is where the individual contestant-solution PDF's were stored by
  the previous shell script; and
* After each individual PDF is uploaded from `out`, it is moved to `done`.

The reason for the `done/` directory is so that if there is any network
error or interruption, this program can be safely invoked again without
worrying about losing or duplicating work.
