<?php


$lines = file('3methods8seats');

$set = array();


foreach ($lines as $line) {
		$parts = explode(' ',$line);
		$filename = $parts[0];
		$filename = array_pop(explode('/',$filename));
		$method = $parts[5];
		$result = $parts[3];
		if (!isset($set[$filename])) {
				$set[$filename] = array();
		}
		$set[$filename][$method] = $result;
}

print "filename,approval,borda,stv\n";
foreach($set as $f => $res) {
		print $f.",".$res['APPROVAL'].",".$res['BORDA'].",".$res['STV']."\n";
}
