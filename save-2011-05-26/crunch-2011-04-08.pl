#!/usr/bin/perl

# Crunch sorting statistics

$itemcount = 0;

$minstepn = 1e6;
$maxstepn = 0;
$totaln = 0;

$minstepnlogn = 1e6;
$maxstepnlogn = 0;
$totalnlogn = 0;

$minstepn2 = 1e6;
$maxstepn2 = 0;
$totaln2 = 0;

$n = 0;
$savemethod = "";
$saveoldorder = "";
$saveneworder = "";

print "Method\tOld\tNew\tCount\tTrend\tAvg\tErr\n";

while (<>) {
  ($n, $method, $oldorder, $neworder, $step, $stepn, $stepnlogn, $stepn2) =
    split("\t", $_);
  if ($method eq $savemethod &&
      $oldorder eq $saveoldorder &&
      $neworder eq $saveneworder) {
    $itemcount++;
    $totaln += $stepn;
    if ($stepn < $minstepn) {
      $minstepn = $stepn
    }
    if ($stepn > $maxstepn) {
      $maxstepn = $stepn
    }
    $totalnlogn += $stepnlogn;
    if ($stepnlogn < $minstepnlogn) {
      $minstepnlogn = $stepnlogn
    }
    if ($stepnlogn > $maxstepnlogn) {
      $maxstepnlogn = $stepnlogn
    }
    $totaln2 += $stepn2;
    if ($stepn2 < $minstepn2) {
      $minstepn2 = $stepn2
    }
    if ($stepn2 > $maxstepn2) {
      $maxstepn2 = $stepn2
    }
  } elsif ($itemcount > 0) {
    $avgn = $totaln / $itemcount;
    $errn = ($maxstepn - $minstepn) / $avgn;
    $avgnlogn = $totalnlogn / $itemcount;
    $errnlogn = ($maxstepnlogn - $minstepnlogn) / $avgnlogn;
    $avgn2 = $totaln2 / $itemcount;
    $errn2 = ($maxstepn2 - $minstepn2) / $avgn2;
    print "$savemethod\t$saveoldorder\t$saveneworder\t$itemcount";

    if ($itemcount == 1) {
      print "\tUnknown\t$avgn\t$errn\n";
    } elsif ($errn <= $errnlogn && $errn <= $errn2) {
      print "\tLinear\t$avgn\t$errn\n";
    } elsif ($errnlogn <= $errn && $errnlogn <= $errn2) {
      print "\tNlogN\t$avgnlogn\t$errnlogn\n";
    } elsif ($errn2 <= $errn && $errn2 <= $errnlogn) {
      print "\tQuadratic\t$avgn2\t$errn2\n";
    }

    $itemcount = 0;

    $minstepn = 1e6;
    $maxstepn = 0;
    $totaln = 0;

    $minstepnlogn = 1e6;
    $maxstepnlogn = 0;
    $totalnlogn = 0;

    $minstepn2 = 1e6;
    $maxstepn2 = 0;
    $totaln2 = 0;
  }
  $savemethod = $method;
  $saveoldorder = $oldorder;
  $saveneworder = $neworder;
}
