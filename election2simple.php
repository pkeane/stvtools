<?php

$filename = 'elections/2002_election.json';
//$filename = '2005_election.json';

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

print json_encode($new_ballots);
