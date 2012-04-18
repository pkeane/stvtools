<?php

ini_set('display_errors',1);
ini_set('display_startup_errors',1);
error_reporting(E_ALL);


function printFormattedPairs($pairs) {
		foreach ($pairs as $cand => $beat) {
				foreach ($beat as $loser => $num) {
						print "$cand preferred to $loser on $num ballots\n";
				}
		}
}

function processBallotSet($filepath,$ballot_set_name,$pairs) {
		global $PRINT;
		$data = json_decode(file_get_contents($filepath),1);

		foreach ($data as $ballot) {
				$pairs = runBallot($pairs,$ballot);
		}

		//printFormattedPairs($pairs);
		$cands = array_keys($pairs);
		asort($cands);

		$new_cands  = array();
		foreach ($cands as $cc) {
				$new_cands[$cc]['beat'] = array();
				$new_cands[$cc]['lost_to'] = array();
				$new_cands[$cc]['tied'] = array();
		}
		foreach ($cands as $c1) {
				foreach ($cands as $c2) {
						if ($c1 != $c2) {
								if ($pairs[$c1][$c2] > $pairs[$c2][$c1]) {
										//	print "$c1 beats $c2\n";
										$new_cands[$c1]['beat'][] = $c2;
										$new_cands[$c2]['lost_to'][] = $c1;
								}
								if ($pairs[$c1][$c2] < $pairs[$c2][$c1]) {
										//	print "$c2 beats $c1\n";
								}
								if ($pairs[$c1][$c2] == $pairs[$c2][$c1]) {
										$new_cands[$c2]['tied'][] = $c1;
								}
						}
				}
		}
		$condorcets = array();
		foreach ($new_cands as $ocand => $result) {
				foreach ($result as $stat => $subcands) {
						//print "$ocand $stat ".count($subcands)." candidates\n"; 
						if ( 'lost_to' == $stat && 0 == count($subcands)) {
								print "$ocand is CONDORCET on ballot $ballot_set_name\n";
								$condorcets[] = "$ocand is CONDORCET on ballot $ballot_set_name\n";
						}
				}
		}
}

function runBallot($pairs,$ballot) {
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

function runElections() {
		$num_cands = 30;
		$cands = array();
		foreach (range(1,$num_cands) as $num) {
				$cands[] = 'cand'.$num;
		}
		$pairs = getAllPairs($cands);
		$result = array();
		$condorcets = array();
		foreach (range(0,100000) as $j) {
				$ballot_set_name = 'ballot_'.sprintf("%07d",$j);
				$dir = substr($ballot_set_name,-3);
				$filepath = 'sim_ballots/'.$dir.'/'.$ballot_set_name.'.json';
				processBallotSet($filepath,$ballot_set_name,$pairs);
		}
}

$aggregs = array();

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
