<?php

$data = json_decode(file_get_contents('2011.json'),1);

$result['ELECTION'] = array();
$result['ELECTION'] = array(
		'id' => "2011",
		'seats' => '12'
		);
$result['CANDIDATES'] = array();
$result['BALLOTS'] = $data['ballots'];




print json_encode($result);

