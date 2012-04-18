<?php

/*
data definitions:

		ballot -- a dictionary with two elements:
				'value': float indicating current value of the ballot
				'data': ordered list of candidate eids
		ballots -- an array of ballots

		candidate -- an object with five attributes:
						'eid': string
						'is_full_professor': Boolean
						'step_points': array of points at each step
						'points': points at current step
		candidates -- a dictionary of eid => candidate

		committee -- an array of candidates who have been elected
		ballot_tally -- a dictionary of eid, points of first position candidates
		logs -- an array of step logs

configuration variables:
		seats -- integer indicating the size of the committee to be elected
		initial_ballot_value
 */

$result = array();

foreach (new DirectoryIterator('elections') as $fileInfo) {
		if($fileInfo->isDot()) {
				continue;
		} else {
				$fn = 'elections/'.$fileInfo->getFilename();
				$elec_data = json_decode(file_get_contents($fn),1);
				$seats = $elec_data['ELECTION']['seats'];
				$year = $elec_data['ELECTION']['id'];

				if ('2011' != $year) {
						continue;
				}


				$ballots = evenBallotLength($elec_data['BALLOTS']);

				$candidates = getCandidates($ballots);
				$num_ballots = count($ballots);
				$droop = calculateDroop($num_ballots,$seats);

				$committee = array();

				foreach (range(1,100) as $num) {
						if (0 == $num%100) {
								print $year." : ".$num." memory ".memory_get_usage()."\n";
						}
						$logs = tallyBallots($ballots,$candidates,$seats,$droop);
						$last_log = array_pop($logs);
						foreach ($last_log['committee'] as $elected) {
								if (!isset($committee[$elected->eid])) {
										$committee[$elected->eid] = 0;
								}
								$committee[$elected->eid] += 1;
						}
				}
				$result[$year] = $committee;
		}
}

print json_encode($result);

function debug($str) {
		print "\n\nDEBUG: $str\n\n";
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
