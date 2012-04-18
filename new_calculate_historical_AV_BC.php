<?php

foreach (new DirectoryIterator('elections') as $fileInfo) {
		if($fileInfo->isDot()) {
				continue;
		} else {
				$fn = 'elections/'.$fileInfo->getFilename();
				$elec_data = json_decode(file_get_contents($fn),1);
				$seats = $elec_data['ELECTION']['seats'];
				$year = $elec_data['ELECTION']['id'];
				$ballots = file2data($fn);
				//$candidates = count($elec_data['CANDIDATES']);
				//APPROVAL
				/*
				$approv = findApproval($ballots,$seats);
				$out = '';
				foreach ($approv as $eid => $tally) {
						$out .= $eid.",".$tally."\n";
				}
				$outfile = 'historical_approval/approval_'.$year.'.csv';
				file_put_contents($outfile,$out);
				 */

				//BORDA
				$borda = findBorda($ballots,$seats);
				$out = '';
				foreach ($borda as $eid => $tally) {
						$out .= $eid.",".$tally."\n";
				}
				$outfile = 'new_historical_borda/borda_'.$year.'.csv';
				file_put_contents($outfile,$out);
		}
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

