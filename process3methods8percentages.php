<?php


$lines = file('3methods8percentages');

$set = array();


foreach ($lines as $line) {
		$parts = explode(' ',$line);
$filename = $parts[0];
		$filename = array_pop(explode('/',$filename));
		$method = $parts[5];
		$percentage = trim($parts[9]);
		if (!isset($set[$filename])) {
				$set[$filename] = array();
		}
		if ('NOT' == $percentage) {
				$percentage = 0;
		}
		$set[$filename][$method] = $percentage;
}

print "filename,approval,borda,stv\n";
foreach($set as $f => $res) {
		print $f.",".$res['APPROVAL'].",".$res['BORDA'].",".$res['STV']."\n";
}
