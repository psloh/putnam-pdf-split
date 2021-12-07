#!/usr/bin/perl
use strict;
use warnings;

print "PIN,user_id\n";

my $userId;

while (<>) {
  if ($_ =~ /<tr.*user-id-(\d+)/) {
    $userId = $1;
  }
  if ($_ =~ /<td class="centered">(\d+)<\/td>/) {
    print "$1,$userId\n";
  }
}
