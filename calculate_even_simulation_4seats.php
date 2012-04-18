<?php


$PRINT = 0;
$start = microtime(1);
$iters = 100000;
$seats = 4;

foreach (range(0,$iters) as $j) {
		$ballot_set_name = 'ballot_'.sprintf("%07d",$j);
		$dir = substr($ballot_set_name,-3);
		$filepath = 'sim_ballots/'.$dir.'/'.$ballot_set_name.'.json';
		print "working on $filepath\n";
		checkIsFile($filepath);
		$ballots = json_decode(file_get_contents($filepath),1);
		$ballots = evenBallotLength($ballots);

		$dir_path = $seats.'seats_even/'.$dir;
		if (!is_dir($dir_path)) {
				mkdir($dir_path);
		}

		$result_path = $dir_path.'/'.$ballot_set_name.'.json';

		if (is_file($result_path)) {
				continue;
		}
		//check out 
		file_put_contents($result_path,'-');


		$result = array();

		$result['condorcet'] = findCondorcet($filepath);

		$result['approv'] = findApproval($ballots,$seats);

		$result['borda'] = findBorda($ballots,$seats);

		$result['stv'] = findStv($ballots,$seats);

		$result_json = json_encode($result);

		file_put_contents($result_path,$result_json);

		$now = microtime(1);
		$num_done = $j+1;
		$per_iter = ($now-$start)/$num_done;
		$left_to_do = $iters - $num_done;
		$time_remaining = round(($per_iter*$left_to_do)/60);
		print $j." iterations completed ";
		print $time_remaining." minutes to go\n";
}


function findCondorcet($filepath) {
		$ballots = json_decode(file_get_contents($filepath),1);
		$cands = getCandidates($ballots); 
		$cprobs = runBallots($cands,$ballots);
		arsort($cprobs);
		return $cprobs;
}

function debug($str) {
		print "\n\nDEBUG: $str\n\n";
}

function checkIsFile($path) {
		if (is_file($path)) {
				return true;
		} else {
				print "NOOOOOOOO!!!!! ".$path." is NOT a file!\n";
				exit;
		}
}


/**** STV ***/

function findStv($ballots,$seats) {
		$candidates = getCandidates($ballots);
		$num_ballots = count($ballots);
		$droop = calculateDroop($num_ballots,$seats);
		$committee = array();
		foreach (range(1,100) as $num) {
				$logs = tallyBallots($ballots,$candidates,$seats,$droop);
				$last_log = array_pop($logs);
				foreach ($last_log['committee'] as $elected) {
						if (!isset($committee[$elected->eid])) {
								$committee[$elected->eid] = 0;
						}
						$committee[$elected->eid] += 1;
				}
		}
		return $committee;
}


class StvCandidate {
		public $eid;
		public $step_points = array();
		public $points = 0;

		public function __construct($eid) {
				$this->eid = $eid;
		}
}

class StvBallot {
		public $value;
		public $data = array();

		public function __construct($ballot) {
				$this->data = $ballot;
				$this->value = 100;
		}
}

function evenBallotLength($ballots) {
		$lengths = array();
		foreach ($ballots as $bal) {
				$lengths[] = count($bal);
		}
		$stdlength =  max($lengths);
		$new_ballots = array();
		foreach ($ballots as $bal) {
				$need = $stdlength  - count($bal);
				if ($need) {
						$a = array_fill(count($bal),$need,'-');
						$new_ballot = array_merge($bal,$a);
						$new_ballots[] = $new_ballot;
				} else {
						$new_ballots[] = $bal;
				}
		}
		return $new_ballots;
}

function calculateDroop($num_ballots,$seats) {
		return floor(($num_ballots*100)/($seats+1))+1;
}

function getCandidates($ballots) {
		$cands = array();
		foreach($ballots as $ballot) {
				foreach($ballot as $cand) {
						$cands[$cand] = 1;
				}
		}
		$candidates = array_keys($cands);
		natsort($candidates);
		return array_values($candidates);
}

function tallyBallots($ballots,$candidates,$seats,$droop) {
		$config['seats'] = $seats;
		$stv_ballots = array();
		foreach ($ballots as $ballot) {
				$stv_ballot = new StvBallot($ballot);
				$stv_ballots[] = $stv_ballot;
		}
		$stv_candidates = array(); 
		foreach ($candidates as $cand) {
				$stv_cand  = new StvCandidate($cand);
				$stv_candidates[$cand] = $stv_cand;
		}	
		//print_r($stv_candidates); exit;
		$logs = array();
		$committee = array();
		list($stv_ballots,$stv_candidates,$committee,$logs) = runStep($stv_ballots,$stv_candidates,$committee,$config,$droop,$logs);
		return $logs;
}

function runStep($stv_ballots,$stv_candidates,$committee,$config,$droop,$logs,$step_count=0) {
		/*
		 * This is the "master" function.  It can be called once, and will recurse
		 * until committee is full, outputting resulting data
		 * */

		$seats = $config['seats'];
		$log = array();
		$log['step_count'] = $step_count+1;
		//debug($log['step_count']);
		$ballot_tally = getBallotTally($stv_ballots); 
		$no_votes = array();
		foreach (array_keys($stv_candidates) as $eid) { 
				if (!isset($ballot_tally[$eid])) {
						$no_votes[] = $eid;
				}	
		}
		sort($no_votes);
		$log['no_votes'] = $no_votes; 
		arsort($ballot_tally);
		$log['ballot_tally'] = $ballot_tally;
		$log['droop'] = $droop;
		$log['tie_breaks'] = array(); 
		# exit condition
		if (count($committee) == $config['seats'] ) {
				return array($stv_ballots,$stv_candidates,$committee,$logs);
		} else {
				$stv_candidates = setCandidatePoints($stv_candidates,$ballot_tally,$log['step_count']);
				list($stv_candidates,$stv_ballots,$committee,$log) = electOrEliminateOne($stv_candidates,$stv_ballots,$committee,$config,$droop,$log);
				$log['committee'] = cloneArray($committee); 
				$logs[] = $log;
				# recursion
				return runStep($stv_ballots,$stv_candidates,$committee,$config,$droop,$logs,$log['step_count']);
		}
}

function cloneArray($arr) {
		$new_arr = array();
		foreach ($arr as $elem) {
				$new_arr[] = clone($elem);
		}
		return $new_arr;
}

function getBallotTally($stv_ballots) {
		// tally the points for each eid in ballot's first position
		$tally = array();
		foreach ($stv_ballots as $stv_ballot) { 
				$eid = $stv_ballot->data[0];
				if ('-' != $eid) {
						if (!isset($tally[$eid])) {
								$tally[$eid] = 0;
						}
						$tally[$eid] += $stv_ballot->value;
				}
		}
		return $tally;
}

function setCandidatePoints($stv_candidates,$ballot_tally,$step_count) {
		foreach ($stv_candidates as $eid => $stv_c) {
				if (isset($ballot_tally[$eid])) {
						$stv_c->points = $ballot_tally[$eid];
						$stv_c->step_points[$step_count] = $ballot_tally[$eid];
				} else {
						$stv_c->points = 0;
						$stv_c->step_points[$step_count] = 0;
				}
		}
		return $stv_candidates;
}

function electOrEliminateOne($stv_candidates,$stv_ballots,$committee,$config,$droop,$log) {
		// determine ONE candidate to elect or eliminate
		$seats = $config['seats'];
		if (count($stv_candidates)) {
				list($winner,$log) = getWinner($stv_candidates,$log);
				if ($winner->points >= $droop) {
						list($stv_ballots,$log) = allocateSurplus($stv_ballots,$winner,$droop,$log);
						$committee[] = $winner; 
						$surplus = $winner->points - $droop;
						$log['report'] = "added ".$winner->eid." to committee and distributed surplus of ".$surplus;
						unset($stv_candidates[$winner->eid]);
				} else {
						#nobody has at least droop
						list($loser,$log) = getLoser($stv_candidates,$stv_ballots,$log);
						$log['report'] = "removed ".$loser->eid." from ballot";
						unset($stv_candidates[$loser->eid]);
						$stv_ballots = purgeBallotsOfEid($stv_ballots,$loser->eid);
				}
		}
		list($committee,$log) = autofillCommittee($stv_candidates,$stv_ballots,$committee,$config,$log);
		return array($stv_candidates,$stv_ballots,$committee,$log);
}

function highToLowPoints($a, $b) {
		if ($a->points == $b->points) {
				return 0;
		}
		return ($a->points > $b->points) ? -1 : 1;
}

function lowToHighPoints($a, $b) {
		if ($a->points == $b->points) {
				return 0;
		}
		return ($a->points < $b->points) ? -1 : 1;
}

function getWinner($stv_candidates,$log) {
		uasort($stv_candidates,'highToLowPoints');
		$sorted_cands = array_values($stv_candidates);
		if (count($stv_candidates) > 1 && $sorted_cands[0]->points == $sorted_cands[1]->points) {
				#we have a tie
				$tied_candidates = array();
				$highest_score = $sorted_cands[0]->points;
				foreach ($sorted_cands as $scand) {
						if ($highest_score == $scand->points) {
								//$tied_candidates[$scand->eid] = $scand;
								$tied_candidates[] = $scand;
						}
				}
				list($winner,$log) = breakMostPointsTie($tied_candidates,$stv_candidates,$log,0);
		} else {
				#clear winner
				$winner = $sorted_cands[0];
		}
		return array($winner,$log); 
}

function getLoser($stv_candidates,$stv_ballots,$log) {
		uasort($stv_candidates,'lowToHighPoints');
		$sorted_cands = array_values($stv_candidates);
		if (count($stv_candidates) > 1 && $sorted_cands[0]->points == $sorted_cands[1]->points) {
				#we have a tie
				$tied_candidates = array();
				$lowest_score = $sorted_cands[0]->points;
				foreach ($sorted_cands as $scand) {
						if ($lowest_score == $scand->points) {
								$tied_candidates[] = $scand;
						}
				}
				list($loser,$log) = breakLowestPointsTie($tied_candidates,$stv_candidates,$stv_ballots,$log,0);
		} else {
				#clear loser
				$loser = $sorted_cands[0];
		}
		return array($loser,$log); 
}

function autofillCommittee($stv_candidates,$stv_ballots,$committee,$config,$log) {
		/* fills remaining seats automatically when number
		 * of candidates left standing equals the number of open
		 * seats
		 */
		$additions = array(); 
		$seats = $config['seats'];
		if ($seats - count($committee) == count(getBallotTally($stv_ballots))) {
				foreach(getBallotTally($stv_ballots) as $eid => $tally) {
						$committee[] = $stv_candidates[$eid];
						$additions[] = $eid;
				}
		}
		$log['autofill'] = ', '.join($additions);
		return array($committee,$log);
}

function allocateSurplus($stv_ballots,$winner,$droop,$log) {
		# equivalent to schwartz t - q
		$surplus = $winner->points - $droop;
		$count = 0.0;
		$t_prime_value = 0.0;
		# get count of x-ballots
		foreach ($stv_ballots as $ballot) {
				# if winner is in first place on ballot AND
				# there is a 'next' candidate to give points to
				# count corresponds to schwartz p. 13 t'
				if ($winner->eid == $ballot->data[0] and '-' != $ballot->data[1]) {
						$count = $count + 1;
						$t_prime_value += $ballot->value;
				}
		}

		$log['t_prime'] = $t_prime_value;
		$log['winner_points'] = $winner->points; 

		$beneficiaries = array(); 

		if ($t_prime_value && $surplus) {
				$allocation = $surplus/$t_prime_value;
		} else {
				$allocation = 0;
		}

		# allocate surplus
		foreach ($stv_ballots as $ballot) {
				if ($winner->eid == $ballot->data[0] and '-' != $ballot->data[1]) {
						$ballot->value = $ballot->value * $allocation;
						$bene = $ballot->data[1];
						if (isset($beneficiaries[$bene])) {
								$beneficiaries[$bene] += $ballot->value;
						} else {
								$beneficiaries[$bene] = $ballot->value ;
						}
				}
		}

		arsort($beneficiaries);

		$log['beneficiaries'] = $beneficiaries;
		$log['allocation'] = $allocation;

		#remove winner from ballots
		$stv_ballots = purgeBallotsOfEid($stv_ballots,$winner->eid);
		return array($stv_ballots,$log);
}

function purgeBallotsOfEid($stv_ballots,$eid) {
		foreach ($stv_ballots as $ballot) {
				if (in_array($eid,$ballot->data)) {
						$place = array_search($eid,$ballot->data);
						unset($ballot->data[$place]);
						#keep ballots same length
						$ballot->data[] = '-';
				}
				//reset numeric keys
				$ballot->data = array_values($ballot->data);
		}
		return $stv_ballots;
}

function breakMostPointsTie($tied_candidates,$stv_candidates,$log,$run_count) {
		//returns ONE candidate; 'run_count' is incremented w/ each pass
		if ($run_count) {
				$log['tie_breaks'][] = ' tie between: '.join(',',array_keys($tied_candidates)).' at step '.$run_count;
		}
		# per schwartz p. 7, we only need to check historical
		# steps through step k (current) - 1 (e.g., first round go
		# straight random. run_count is zero indexed, so we add 1
		if ($log['step_count'] == $run_count+1) {
				$r = mt_rand(0,count($tied_candidates)-1);
				$log['tie_breaks'][] = '*** coin toss ***';
				/*
				if (!isset($tied_candidates[$r])) {
						print "----".$r."---\n\n";
						print_r($tied_candidates); exit;
				}
				 */
				return array($tied_candidates[$r],$log);
		}

		$historical_step_points = array(); 
		# create eid => points dictionary for [run_count] historical step
		foreach ($tied_candidates as $cand) {
				//step points are 1-based ('cause we use step_count)
				if (is_float($cand->step_points[$run_count+1])) {
						$historical_step_points[$cand->eid] = (string)$cand->step_points[$run_count+1];
				} else {
						$historical_step_points[$cand->eid] = $cand->step_points[$run_count+1];
				}
		}
		arsort($historical_step_points);
		$highest = max($historical_step_points);
		$score_freq = array_count_values($historical_step_points);
		if ($score_freq[$highest] == 1) { 
				# clear winner
				$highest_eid = array_shift(array_keys($historical_step_points));
				return array($stv_candidates[$highest_eid],$log);
		} else {
				#we have a tie
				$new_tied_candidates = array(); 
				foreach ($historical_step_points as $eid => $score) {
						if ($highest == $score) {
								$new_tied_candidates[] = $stv_candidates[$eid];
						}
				}
				# recursion
				return breakMostPointsTie($new_tied_candidates,$stv_candidates,$log,$run_count+1);
		}
}

function breakLowestPointsTie($tied_candidates,$stv_candidates,$stv_ballots,$log,$run_count) {
		//returns ONE candidate; 'run_count' is incremented w/ each pass
		if ($run_count) {
				$log['tie_breaks'][] = ' tie between: '.join(',',array_keys($tied_candidates)).' at step '.$run_count;
		}
		// per schwartz p. 7, we only need to check historical
		// steps through step k (current) - 1 (e.g., first round go
		// straight random. run_count is zero indexed, so we add 1
		// what we are checking here is whether this is out first
		// pass in first step OR if in an historical pass, that we
		// only do as many passes as steps which occurred - 1
		if ($log['step_count'] == $run_count+1) {
				# for lowest, if points = 0, no further processing is necessary
				# because no historical review is necessesary
				# because the cand never got any points in a prev step 
				if  (0 == $tied_candidates[0]->points) {
						$r = mt_rand(0,count($tied_candidates)-1);
						$log['tie_breaks'][] = '*** coin toss ***';
						return array($tied_candidates[$r],$log);
				} else {
						/*
						"...we examine the ballots (at step k) on which the surviving
						tied candidates are ranked first and select those tied candidates
						with the lowest second-preference vote total in this subset of
						ballots, then those among the latter candidates with the lowest
						third-preference total, etc.  Only then do we break any remaining
						tie randomly."
						 */
						$considered_ballots = array(); 
						$tied_eids = array(); 
						foreach ($tied_candidates as $tc) {
								$tied_eids[] = $tc->eid;
						}
						foreach ($stv_ballots as $ballot) {
								# "on which the surviving tied candidates are ranked first..."
								if (in_array($ballot->data[0],$tied_eids)) {
										$considered_ballots[] = $ballot; 
								}
						}
						# thus begins process of looking down the ballot
						return secondPreferenceLowTiebreak($tied_candidates,$stv_candidates,$considered_ballots,$log);
				}
		}

		$historical_step_points = array(); 
		# create eid => points dictionary for [run_count] historical step
		foreach ($tied_candidates as $cand) {
				if (is_float($cand->step_points[$run_count+1])) {
						$historical_step_points[$cand->eid] = (string)$cand->step_points[$run_count+1];
				} else {
						$historical_step_points[$cand->eid] = $cand->step_points[$run_count+1];
				}
		}
		asort($historical_step_points);
		$lowest = min($historical_step_points);
		$score_freq = array_count_values($historical_step_points);
		if ($score_freq[$lowest] == 1) { 
				# clear loser 
				$lowest_eid = array_shift(array_keys($historical_step_points));
				return array($stv_candidates[$lowest_eid],$log);
		} else {
				#we have a tie
				$new_tied_candidates = array(); 
				foreach ($historical_step_points as $eid => $score) {
						if ($lowest == $score) {
								$new_tied_candidates[] = $stv_candidates[$eid];
						}
				}
				# recursion
				return breakLowestPointsTie($new_tied_candidates,$stv_candidates,$stv_ballots,$log,$run_count+1);
		}
}

function secondPreferenceLowTiebreak($tied_candidates,$stv_candidates,$stv_ballots,$log,$depth=1) {
		if ($depth == count($stv_ballots[0]->data)) {
				$r = mt_rand(0,count($tied_candidates)-1);
				$log['tie_breaks'][] = '*** coin toss ***';
				return array($tied_candidates[$r],$log);
		} else {
				$log['tie_breaks'][] = '** considering points at preference number '.$depth+1;
				# log['tie_breaks'].append(' tie between: '+', '.join(c.eid for c in tied_candidates))
		}

		$tallies = array();
		//tallies is an assoc array of eid => tally
		//a tally is ticked for each appearance on a ballot at 
		//$depth depth

		//give all tied cands a score of 0
		foreach ($tied_candidates as $cand) {
				$tallies[$cand->eid] = 0;
		}

		foreach ($stv_ballots as $ballot) {
				foreach ($tied_candidates as $cand) {
						if ($cand->eid == $ballot->data[$depth]) {
								$tallies[$cand->eid] += 1;
						}
				}
		}

		//$freq is a sorted list of tally frequencies
		//tally => frequency
		$freq = array_count_values($tallies);
		//sorted low (tally) to high
		ksort($freq);

		//everyone had the same tallies (even if 0)
		if (1 == count($freq)) {
				return secondPreferenceLowTiebreak($tied_candidates,$stv_candidates,$stv_ballots,$log,$depth+1);
		}

		//if freq is bigger than 1, there are multiple tally counts
		$lowest_tally = min($tallies);

		$new_tied_candidates = array(); 
		foreach ($tied_candidates as $cand) {
				if ($tallies[$cand->eid] == $lowest_tally) {
						$new_tied_candidates[] = $cand; 
				}
		}

		if (1 == count($new_tied_candidates)) {
				return array($new_tied_candidates[0],$log);
		} else {
				return secondPreferenceLowTiebreak($new_tied_candidates,$stv_candidates,$stv_ballots,$log,$depth+1);
		}
}

/**** Condorcet ****/

function getBallotPairs($cands,$ballot,$pairs) {
		$i = 0;
		foreach ($ballot as $placed_cand) {
				$j = 0;
				foreach ($ballot as $cand) {
						if ($placed_cand != $cand) {
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
};

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

function runBallots($cands,$ballots) {
		$cprobs = array();
		$final_probs = array();
		$pairs = getAllPairs($cands);
		foreach ($ballots as $b) {
				$pairs = getBallotPairs($cands,$b,$pairs);
		}

		$ballots_with_neither = array();
		foreach ($ballots as $ballot) {
				foreach ($cands as $I) {
						foreach ($cands as $J) {
								if ($I != $J) {
										if (!isset($ballots_with_neither[$I])) {
												$ballots_with_neither[$I] = array();
										}
										if (!isset($ballots_with_neither[$I][$J])) {
												$ballots_with_neither[$I][$J] = 0;
										}
										if (!in_array($I,$ballot) and !in_array($J,$ballot)) {
												$ballots_with_neither[$I][$J] += 1;
										}
								}
						}
				}
		}
		//print_r($ballots_with_neither);exit;

		foreach ($ballots as $ballot) {
				foreach ($cands as $I) {
						$cprobs[$I] = array();
						foreach ($cands as $J) {
								if ($I != $J) {
										$cprobs[$I][$J] = '';

										//per Tse-min algorithm
										$V = count($ballots);
										$M = floor($V/2)+1; 
										$C = count($cands);

										$R = count($ballots) - $ballots_with_neither[$I][$J];
										$S = $ballots_with_neither[$I][$J];
										$T = $pairs[$I][$J];


										$IbeatJ = $pairs[$I][$J];
										$JbeatI = $pairs[$J][$I];
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

										$cprobs[$I][$J] = $new_prob;

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
								} // I != J
						} // foreach J
				} //foreach I
				foreach ($cprobs as $I => $J_array) {
						$final_probs[$I] = round(array_product($J_array),4);
				}
		}
		return $final_probs;
}

function binomial($S,$Q,$k) {
		$b_coeff = binomial_coeff($S,$k);
		return $b_coeff*pow($Q,$k)*pow((1-$Q),$S-$k);
}

function binomial_coeff($n,$k) {
		return fact($n)/(fact($k)*fact($n-$k));
}

function fact($int){
		if($int<2)return 1;
		for($f=2;$int-1>1;$f*=$int--);
		return $f;
}

/****** AV and BC *******/

function findApproval($ballots,$seats) {
		$tallies = array();
		foreach ($ballots as $ballot) {
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
		$slate = array();
		unset($tallies['-']);
		return getSlate($tallies,$slate,$seats);
}

function findBorda($ballots,$seats) {
		$cand_list = getCandidates($ballots);
		$cand_num = count($cand_list);
		$tallies = array();
		foreach ($ballots as $ballot) {
				foreach (range(0,$cand_num-1) as $num) {
						if (isset($ballot[$num])) {
								$cname = $ballot[$num];
								if (!isset($tallies[$cname])) {
										$tallies[$cname] = 0;
								}
								$tallies[$cname] += $cand_num - $num;
						}
				}
		}
		$slate = array();
		unset($tallies['-']);
		return getSlate($tallies,$slate,$seats);
}

function getSlate($tallies,$slate,$seats) {
		if (count($slate) >= $seats) {
				return $slate;
		}
		arsort($tallies);
		$highest = max($tallies);
		$winners = array();
		$current_top_set = array();
		foreach ($tallies as $cand => $score) {
				if ($highest == $score) {
						$current_top_set[] = $cand;
				}
		}
		if (count($slate) + count($current_top_set) > $seats) {
				$num_needed = $seats - count($slate);
				//shuffle($current_top_set);
				//$to_add = array_slice($current_top_set,0,$num_needed);
				$percentage = round(100*($num_needed/count($current_top_set)),5);
				foreach ($current_top_set as $chosen) {
						$slate[$chosen] = $percentage;
						unset($tallies[$chosen]);
				}
		} else {
				foreach ($current_top_set as $chosen) {
						$slate[$chosen] = 100;
						unset($tallies[$chosen]);
				}
		}
		return getSlate($tallies,$slate,$seats);
}

