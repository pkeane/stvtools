<?php

$candidates = 30;
$seats = 12;

//foreach (new DirectoryIterator('elections') as $fileInfo) {
//		if($fileInfo->isDot()) {
//				continue;
//		} else {
$fn = 'sim_ballots_uneven/000/ballot_0000000.json'; 
$ballots = json_decode(file_get_contents($fn),1);
$seats = 12;
$ballots = evenBallotLength($ballots);
$candidates = count(getCandidates($ballots));
$num_ballots = count($ballots);
				//APPROVAL
				$approv = findApproval($ballots,$seats);
				$out = '';
				foreach ($approv as $eid => $tally) {
						$out .= $eid.",".$tally."\n";
				}
				//print json_encode($approv); exit;
				//$outfile = 'historical_approval/approval_'.$year.'.csv';
				//file_put_contents($outfile,$out);

				//BORDA
				$borda = findBorda($ballots,$seats,$candidates);
				$out = '';
				foreach ($borda as $eid => $tally) {
						$out .= $eid.",".$tally."\n";
				}
				print json_encode($borda); exit;
				//$outfile = 'historical_borda/borda_'.$year.'.csv';
				//file_put_contents($outfile,$out);
		//}
//}

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

function file2data($filename) {
		$data = json_decode(file_get_contents($filename),1);
		$ballots = $data['BALLOTS'];
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

function findApproval($data,$seats) {
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
		$slate = array();
		unset($tallies['-']);
		return getSlate($tallies,$slate,$seats);
}

function findBorda($data,$seats,$candidates) {
		$cands = $data[0];
		natsort($cands); 

		$tallies = array();
		foreach ($data as $ballot) {
				foreach (range(0,$candidates-1) as $num) {
						if (isset($ballot[$num])) {
								$cname = $ballot[$num];
								if (!isset($tallies[$cname])) {
										$tallies[$cname] = 0;
								}
								$tallies[$cname] += $candidates - $num;
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
		/*
		if (count($slate) > $seats) {	
				print "PROBLEM: slate is too big\n";
				exit;
		}
		 */
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

