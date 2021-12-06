#!/bin/sh
set -eux
mkdir -p out/
pdftk 4197_001.pdf cat 5 output out/535762A1.pdf
pdftk 4197_001.pdf cat 3 output out/535762A2.pdf
pdftk 4197_001.pdf cat 7 output out/535762A3.pdf
pdftk 4197_001.pdf cat 25 output out/535799A1.pdf
pdftk 4197_001.pdf cat 27 28 output out/535799A2.pdf
pdftk 4197_001.pdf cat 31 32 33 output out/535802A1.pdf
pdftk 4197_001.pdf cat 35 36 output out/535802A3.pdf
pdftk 4197_001.pdf cat 37 output out/535802A5.pdf
pdftk 4197_001.pdf cat 41 output out/535982A1.pdf
pdftk 4197_001.pdf cat 43 output out/535982A2.pdf
pdftk 4197_001.pdf cat 45 output out/535982A5.pdf
pdftk 4197_001.pdf cat 47 output out/535982A6.pdf
pdftk 4197_001.pdf cat 11 12 output out/647127A1.pdf
pdftk 4197_001.pdf cat 13 15 output out/647127A2.pdf
pdftk 4197_001.pdf cat 17 output out/647127A3.pdf
pdftk 4197_001.pdf cat 19 output out/647127A5.pdf
pdftk 4197_001.pdf cat 21 output out/647127A6.pdf
