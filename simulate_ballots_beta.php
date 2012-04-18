<?php

foreach (array(4,8,12) as $seats) {
		makeBallots($seats);
}

function makeBallots($seats) {
		$outdir = 'sim_ballots_beta'.$seats;
		$voters = 40;
		$cands = 30;
		foreach (range(1,100000) as $j) {
				$name = 'len_'.sprintf("%07d",$j);
				$dir = substr($name,-3);
				$filename = $seats.'seat_lengths/'.$dir.'/'.$name;
				print "working on $filename\n";
				$lengths = array();
				foreach (file($filename) as $line) {
						$lengths[] = trim($line);
				}

				$ball_set = create_ballot_set($voters,$cands,$seats,$lengths);
				$ballot_set_json = json_encode($ball_set);
				$ballot_name = 'ballot_'.sprintf("%07d",$j);
				if (!file_exists($outdir.'/'.$dir)) {
						mkdir($outdir.'/'.$dir);
				}
				$filename = $outdir.'/'.$dir.'/'.$ballot_name.'.json';
				print $filename."\n";
				file_put_contents($filename,$ballot_set_json);
		}
}

function create_ballot_set($voters,$cands,$seats,$lengths) {
		$cand_array = array();
		foreach (range(1,$cands) as $num) {
				$cand_array[] = 'cand'.$num;
		}

		$ballots = array();
		foreach ($lengths as $ballot_length) {
				shuffle($cand_array);
				$ballots[] = array_slice($cand_array,0,$ballot_length);
		}
		return $ballots;
}

