<?php

ini_set('display_errors',1);
ini_set('display_startup_errors',1);
error_reporting(E_ALL);


function flip($p = .5) {
		if (mt_rand(1,1000000000) <= ($p*1000000000)) {
				return 1;
		} else {
				return 0;
		}
}

function printFormattedPairs($pairs) {
		foreach ($pairs as $cand => $beat) {
				foreach ($beat as $loser => $num) {
						print "$cand preferred to $loser on $num ballots\n";
				}
		}
}

function printFormattedResult($new_cands) {
		foreach ($new_cands as $year => $result) {
				foreach ($result as $cand => $set) {
						foreach ($set as $stat => $subcands) {
								print "$cand $stat ".count($subcands)." candidates\n"; 
						}						
				}
		}
}

function rerunForNeitherOnBallot($cands,$pairs,$ballots) {
		$old_pairs = $pairs;
		$new_pairs = $pairs;
		foreach ($ballots as $ballot) {
				$cands_missing_on_this_ballot = array();
				foreach ($cands as $miss) {
						if (!in_array($miss,$ballot)) {
								$cands_missing_on_this_ballot[] = $miss;
						}
				}
				foreach ($cands_missing_on_this_ballot as $I) {
						foreach ($cands_missing_on_this_ballot as $J) {
								if ($I != $J) {

										$ballots_with_neither = array();
										foreach ($ballots as $bal) {
												if (!in_array($I,$bal) and !in_array($J,$bal)) {
														$ballots_with_neither[] = $bal;
												}
										}

										//per Tse-min algorithm
										$V = count($ballots);
										$M = floor($V/2)+1; 
										$C = count($cands);

										$R = count($ballots) - count($ballots_with_neither);
										$S = count($ballots_with_neither);
										$T = $old_pairs[$I][$J];


										$IbeatJ = $old_pairs[$I][$J];
										$JbeatI = $old_pairs[$J][$I];
										$prob = $IbeatJ/($IbeatJ+$JbeatI);

										$Q = $prob;

										$k_range = $M-$T-1;


										if (($M-$S <= $T) && ($T < $M)) {
												$sum = 0;
												foreach (range(0,$k_range) as $k) {
														$sum += binomial($S,$Q,$k);
												}
												$new_prob = 1-$sum;
										}

										if ($T+$S < $M) {
												$new_prob = 0;
										}

										if ($T >= $M) {
												$new_prob = 1;
										}

										global $PRINT;
										if ($PRINT) {
												print "\n----------------------\n";
												print "I is $I\n";
												print "J is $J\n";
												print "V is $V\n";
												print "M is $M\n";
												print "C is $C\n";
												print "R is $R\n";
												print "S is $S\n";
												print "T is $T\n";
												print "Q is $Q\n";
												print "k range is $k_range\n";
												print "calculated probability is $new_prob\n";
										}

										if (flip($new_prob)) {
												$new_pairs[$I][$J] += 1;
										} else {
										//		$new_pairs[$J][$I] += 1;
										}
								}
						}
				}
		}
		return $new_pairs;
}

function binomial($S,$Q,$k) {
		$b_coeff = binomial_coeff($S,$k);
		return $b_coeff*pow($Q,$k)*pow((1-$Q),$S-$k);
}

/*
function binomial_coeff($n, $k) {
		$j = $res = 1;
		if($k < 0 || $k > $n)
				return 0;
		if(($n - $k) < $k)
				$k = $n - $k;
		while($j <= $k) {
				$res *= $n--;
				$res /= $j++;
		}
		return $res;
}
 */

function binomial_coeff($n,$k) {
		return fact($n)/(fact($k)*fact($n-$k));
}

function fact($int){
  if($int<2)return 1;
  for($f=2;$int-1>1;$f*=$int--);
  return $f;
}

function getResults($result,$filepath) {
		global $PRINT;
		$cands = getCandidates($filepath); 
		$pairs = getAllPairs($cands);
		$data = json_decode(file_get_contents($filepath),1);
		$year = $data['ELECTION']['id'];

		if ($PRINT) {
				print "\n\n ----- $year -----\n\n";
		}
		
		foreach ($data['BALLOTS'] as $ballot) {
				$pairs = runBallot($cands,$pairs,$ballot);
		}
		$pairs = rerunForNeitherOnBallot($cands,$pairs,$data['BALLOTS']);

		//printFormattedPairs($pairs);
		$new_cands[$year]  = array();
		foreach ($cands as $cc) {
				$new_cands[$year][$cc]['beat'] = array();
				$new_cands[$year][$cc]['lost_to'] = array();
				$new_cands[$year][$cc]['tied'] = array();
		}
		foreach ($cands as $c1) {
				foreach ($cands as $c2) {
						if ($c1 != $c2) {
								if ($pairs[$c1][$c2] > $pairs[$c2][$c1]) {
										//	print "$c1 beats $c2\n";
										$new_cands[$year][$c1]['beat'][] = $c2;
										$new_cands[$year][$c2]['lost_to'][] = $c1;
								}
								if ($pairs[$c1][$c2] < $pairs[$c2][$c1]) {
										//	print "$c2 beats $c1\n";
								}
								if ($pairs[$c1][$c2] == $pairs[$c2][$c1]) {
										$new_cands[$year][$c2]['tied'][] = $c1;
								}
						}
				}
		}
		//print "\n\n ----- $year Summary -----\n\n";
		//printFormattedResult($new_cands);
		return $new_cands;
}

function runBallot($cands,$pairs,$ballot) {
		$i = 0;
		foreach ($ballot as $placed_cand) {
				$j = 0;
				foreach ($ballot as $cand) {
						if ($placed_cand != $cand) {
								//print "$i $placed_cand === $j $cand\n";
								if ($i < $j) {
										//record a "win"
										$pairs[$placed_cand][$cand] += 1;
								}
								if ($j < $i) {
										//	$pairs[$cand][$placed_cand] += 1;
								}
						} 
						$j++;
				}
				$i++;
		}
		//cands not on ballot
		$missing = array();
		foreach ($cands as $miss) {
				if (!in_array($miss,$ballot)) {
						$missing[] = $miss;
				}
		}
		foreach ($missing as $m) {
				foreach ($ballot as $c) {
						$pairs[$c][$m] += 1;
				}
		}
		return $pairs;
}


function getAllPairs($cands) {
		$pairs = array();
		foreach ($cands as $outercand) {
				foreach ($cands as $innercand) {
						if (!isset($pairs[$innercand])) {
								$pairs[$innercand] = array();
						}
						if ($outercand != $innercand) {
								$pairs[$innercand][$outercand] = 0;
						}
				}
		}
		return $pairs;
}

function getCandidates($filepath) {
		$cands = array();
		$data = json_decode(file_get_contents($filepath),1);
		foreach ($data['BALLOTS'] as $ballot) {
				foreach ($ballot as $cand) {
						$cands[$cand] = 1;
				}
		}
		return array_keys($cands);
}


function runElections() {
		$result = array();
		$condorcets = array();
		foreach (new DirectoryIterator('elections') as $fileInfo) {
				if($fileInfo->isDot()) {
						continue;
				} else {
						$result = getResults($result,'elections/'.$fileInfo->getFilename());
						foreach ($result as $year => $cands) {
								$condorcet = '[none]';
								foreach ($cands as $cand => $set) {
										if (0 == count($set['lost_to'])) {
												$condorcet = $cand;
										}
								}
								$condorcets[$year] = $condorcet;
						}
				}
		}
		return $condorcets;
}

$aggregs = array();

/*
$yes = 0;
$no  = 0;
foreach (range(0,100000) as $i) {
		if (flip(.75)) {
				$yes++;
		} else {
				$no++;
		}
}
print "yes: ".$yes."\n";
print "no: ".$no."\n";

 */

$PRINT = 0;

$start = microtime(1);

$iters = 100;

foreach (range(0,$iters) as $i) {
		$now = microtime(1);
		$num_done = $i+1;

		$per_iter = ($now-$start)/$num_done;

		$left_to_do = $iters - $num_done;

		$time_remaining = round(($per_iter*$left_to_do)/60);

		if (0 == $i%5) {
				print $i." iterations completed ";
				print $time_remaining." minutes to go\n";
		}


		$condorcets = runElections();
		foreach ($condorcets as $y => $cw) {
				if (!isset($aggregs[$y])) {
						$aggregs[$y] = array();
				}
				if (!isset($aggregs[$y][$cw])) {
						$aggregs[$y][$cw] = 0;
				}
				$aggregs[$y][$cw] += 1;
		}
}

ksort($aggregs);
$json_result = json_encode($aggregs);

file_put_contents('result_'.time().'.json',$json_result);

print $json_result;
print "\n\n\n";
