<?php

foreach (file('new_condorcet_simulation_count') as $line) {
		$parts = explode(' ',$line);
		$winner = $parts[0];
		$file = trim(array_pop($parts));
		$approv = findApproval($file);
		print $file." condorcet:".$winner." approval:".join(',',$approv);
		if (in_array($winner,$approv)) {
				if (1 == count($approv)) {
						$flag = "EQUAL";
				} else {
						$flag = "IN SET";
				}
		} else {
				$flag = "NO";
		}
		print " ".$flag."\n";
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

function flip($p = .5) {
		if (mt_rand(1,1000000000) <= ($p*1000000000)) {
				return 1;
		} else {
				return 0;
		}
}


