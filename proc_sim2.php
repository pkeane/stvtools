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
		$seats = 8;
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

function getSlate($tallies,$slate,$seats) {
		if (count($slate) >= $seats) {
				return $slate;
		}
		arsort($tallies);
		$highest = max($tallies);
		$winners = array();
		foreach ($tallies as $cand => $score) {
				if ($highest == $score) {
						$slate[] = $cand;
						unset($tallies[$cand]);
				}
		}
		return getSlate($tallies,$slate,$seats);
}
