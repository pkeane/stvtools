<?php

$candidates = 30;
$seats = 8;

foreach (file('new_condorcet_simulation_count') as $line) {
		$parts = explode(' ',$line);
		$winner = $parts[0];
		$file = trim(array_pop($parts));

		//APPROVAL
		$approv = findApproval($file,$seats);
		//print_r($approv); exit;
		$committee = array();
		foreach ($approv as $eid => $tally) {
				$committee[] = $eid.":".$tally;
		}
		print $file." condorcet:".$winner." approval:".join(',',$committee);
		if (in_array($winner,array_keys($approv))) {
				$place = array_search($winner,array_keys($approv))+1;
				$perc = $approv[$winner];
				if (1 == count($approv)) {
						$flag = "EQUAL";
				} else {
						$flag = "YES IN APPROVAL SET - place: $perc";
				}
		} else {
				$flag = "NO IN APPROVAL SET - place: 0";
		}
		print " ".$flag."\n";

		//BORDA
		$borda = findBorda($file,$seats,$candidates);
		$committee = array();
		foreach ($borda as $eid => $tally) {
				$committee[] = $eid.":".$tally;
		}
		print $file." condorcet:".$winner." borda:".join(',',$borda);
		if (in_array($winner,array_keys($borda))) {
				$place = array_search($winner,array_keys($borda))+1;
				$perc = $borda[$winner];
				if (1 == count($borda)) {
						$flag = "EQUAL";
				} else {
						$flag = "YES IN BORDA SET - place: $perc";
				}
		} else {
				$flag = "NO IN BORDA SET - place: 0";
		}
		print " ".$flag."\n";
}

function findApproval($filename,$seats) {
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
		$slate = array();
		return getSlate($tallies,$slate,$seats);
}

function findBorda($filename,$seats,$candidates) {
		$data = json_decode(file_get_contents($filename));
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

