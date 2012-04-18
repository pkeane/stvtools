<?php

foreach (range(0,100000) as $j) {
		$ballot_set_name = 'ballot_'.sprintf("%07d",$j);
		$dir = substr($ballot_set_name,-3);
		$filepath = 'sim_ballots/'.$dir.'/'.$ballot_set_name.'.json';
		findCondorcet($filepath);
}

//$filepath = 'sim_ballots/484/ballot_0000484.json';
//findCondorcet($filepath);

function findCondorcet($filename) {
		$data = json_decode(file_get_contents($filename));
		$cands = $data[0];
		natsort($cands); 

		$pairs = array();
		foreach ($cands as $c) {
				$new_cands = $cands;
				unset($new_cands[array_search($c,$new_cands)]);
				foreach ($new_cands as $nc) {
						$pairs[$c][$nc] = 0;
				}
		}

		foreach ($data as $ballot) {
				foreach ($cands as $cand1) {
						foreach ($cands as $cand2) {
								if ($cand1 != $cand2) {
										$cand1rank = array_search($cand1,$ballot);
										$cand2rank = array_search($cand2,$ballot);
										if ($cand1rank < $cand2rank) {
												$pairs[$cand1][$cand2] += 1;
										} 
								}
						}
				}
		}

		$tallies = array();
		foreach ($cands as $c1) {
				foreach ($cands as $c2) {
						if ($c1 != $c2) {
								if ($pairs[$c1][$c2] > $pairs[$c2][$c1]) {
										$tallies[$c1]['beat'][] = $c2;
										$tallies[$c2]['lost_to'][] = $c1;
								}
								if ($pairs[$c1][$c2] < $pairs[$c2][$c1]) {
										//	print "$c2 beats $c1\n";
								}
								if ($pairs[$c1][$c2] == $pairs[$c2][$c1]) {
										$tallies[$c2]['tied'][] = $c1;
								}
						}
				}
		}

		ksort($tallies);

		//print_r($tallies);

		$has_condorcet = 0;
		foreach ($cands as $cand) {
				if (!isset($tallies[$cand]['lost_to']) && !isset($tallies[$cand]['tied'])) {
						print "$cand is Condorcet Winner in $filename\n";
						$has_condorcet = 1;
						/*
						$approval_winners = findApproval($filename);
						if (1 == count($approval_winners)) {
						print $approval_winners[0]." is Approval Winner\n";
						} else {
								print "Approval Winners:";
								print_r($approval_winners);
						}
						print "\n\n";
						 */
				}
		}

		if (!$has_condorcet) {
				//print "NO Condorcet Winner in $filename\n";
		}
}

function findApproval($filename) {
		$seats = 12;
		$data = json_decode(file_get_contents($filename));
		$cands = $data[0];
		natsort($cands); 

		$tallies = array();
		foreach ($data as $ballot) {
				foreach (range(0,$seats-1) as $num) {
						if (isset($ballot[$num])) {
								$cname = $ballot[$num];
								if (!isset($tallies[$cname])) {
										$tallies[$cname] = 0;
								}
								$tallies[$cname] += 1;
						}
				}
		}
		arsort($tallies);
		$highest = max($tallies);
		$winners = array();
		foreach ($tallies as $cand => $score) {
				if ($highest == $score) {
						$winners[] = $cand;
				}
		}
		return $winners;
}
