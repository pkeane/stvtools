<?php

$voters = 40;
$cands = 30;
$seats = 12;

function create_ballot_set($voters,$cands,$seats) {
		$cand_array = array();
		foreach (range(1,$cands) as $num) {
				$cand_array[] = 'cand'.$num;
		}

		$ballots = array();
		foreach (range(1,$voters) as $i) {
				shuffle($cand_array);
				$ballots[] = $cand_array;
		}
		return $ballots;
}

foreach (range(0,100000) as $j) {
		$ball_set = create_ballot_set($voters,$cands,$seats);
		$ballot_set_json = json_encode($ball_set);
		$ballot_name = 'ballot_'.sprintf("%07d",$j);
		$dir = substr($ballot_name,-3);
		if (!file_exists('sim_ballots/'.$dir)) {
				mkdir('sim_ballots/'.$dir);
		}
		$filename = 'sim_ballots/'.$dir.'/'.$ballot_name.'.json';
		print $filename."\n";
		file_put_contents($filename,$ballot_set_json);

}
