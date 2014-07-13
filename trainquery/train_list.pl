#!/usr/bin/perl -w

use strict;

my $s = do { local $/; <> };
$s =~ s/^var //;
$s =~ s/},{/},\n{/g;
$s =~ s/{"station_train_code":"([^(]+)\([^-]+-[^)]+\)","train_no":"([^"]+)"}/"$1": "$2"/g;
$s =~ s/".":\[//mg;
$s =~ s/\]//mg;

print $s
