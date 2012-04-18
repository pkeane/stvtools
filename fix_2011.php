<?php

$fn2010 = 'elections/2010_election.json';
$fn2011 = 'elections/2011_election.json';

$data2010 = json_decode(file_get_contents($fn2010),1);
$data2011 = json_decode(file_get_contents($fn2011),1);

$ballots2010 = $data2010['BALLOTS'];
$ballots2011 = $data2011['BALLOTS'];

$cands2010 = getCandidates($ballots2010);
$cands2011 = getCandidates($ballots2011);

foreach ($cands2010 as $c) {
		if (!in_array($c,$cands2011)) {
				//print "$c NOT in 2011\n";
		}
}

$missing_eids = array();
foreach ($cands2011 as $c) {
		if (!in_array($c,$cands2010)) {
			 $missing_eids[] = $c;	
		}
}

$fac2011 = array();
$fac2010 = $data2010['CANDIDATES'];
foreach ($fac2010 as $faccand) {
		if (in_array($faccand['EID'],$cands2011)) {
				$fac2011[] = $faccand;
		}
}

foreach ($missing_eids as $miss) {
		$sub = array();
		$sub['Full'] = 'Yes';
		$sub['Name'] = $miss;
		$sub['EID'] = $miss;
		$fac2011[] = $sub;
}

//print_r($fac2011);
$data2011['CANDIDATES'] = $fac2011;

print json_encode($data2011); exit;

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
