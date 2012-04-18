<?php

print_r(getData());


function getData() {
		$lengths = array();
		$cands = array();
		$mean = 0;
		foreach (range(1,100000) as $j) {
				$ballot_set_name = 'ballot_'.sprintf("%07d",$j);
				$dir = substr($ballot_set_name,-3);
				$filepath = 'sim_ballots_uneven/'.$dir.'/'.$ballot_set_name.'.json';
				print "working on $filepath\n";
				checkIsFile($filepath);
				$ballots = json_decode(file_get_contents($filepath),1);
				foreach ($ballots as $bal) {
						$lengths[] = count($bal);
						foreach ($bal as $vote) {
								if (!isset($cands[$vote])) {
										$cands[$vote] = 0;
								}
								$cands[$vote] += 1;
						}
				}

				if (0 == $j%10000) {
						$sum = array_sum($lengths);
						$mean = $sum/count($lengths);
						$sd = sd($lengths);
				}

				if ($mean) {
						print "MEAN IS ".$mean."\n";
						print "STANDARD DEVIATION IS ".$sd."\n";
				}
		}
		$max_votes = max($cands);
		$min_votes = min($cands);

		$results = array();
		$results['seats_on_slate'] = $seats;
		$results['ballot_sets_count'] = 100000;
		$results['ballot_length_average'] = $mean;
		$results['ballot_length_standard_deviation'] = $sd;
		$results['max_candidate_votes'] = $max_votes;
		$results['min_candidate_votes'] = $min_votes;
		return $results;
}

function mean($array) {
		$sum = array_sum($array);
		$mean = $sum/count($array);
		return $mean;
}

function checkIsFile($path) {
		if (is_file($path)) {
				return true;
		} else {
				print "NOOOOOOOO!!!!! ".$path." is NOT a file!\n";
				exit;
		}
}

// Function to calculate square of value - mean
function sd_square($x, $mean) { return pow($x - $mean,2); }


// Function to calculate standard deviation (uses sd_square)    
function sd($array) {
		// square root of sum of squares devided by N-1
		return sqrt(array_sum(array_map("sd_square", $array, array_fill(0,count($array), (array_sum($array) / count($array)) ) ) ) / (count($array)-1) );
}

