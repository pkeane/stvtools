<?php

$basedir = '12seats_beta';

$files = array();
$iters = 100000;

foreach (range(0,$iters) as $j) {
		$ballot_set_name = 'ballot_'.sprintf("%07d",$j);
		$dir = substr($ballot_set_name,-3);
		$filepath = $basedir.'/'.$dir.'/'.$ballot_set_name.'.json';
		if (is_file($filepath)) {
				$contents = file_get_contents($filepath);
				if ('-' != $contents) {
						$files[] = $filepath;
				}
		}
}

print "\"total condorcet prob\",filename,approval,borda,stv\n";

foreach ($files as $file) {
		$data = json_decode(file_get_contents($file),1);
		$cprob = condProb($data);
		//if ($cprob) {
				print "$cprob,";
				print join(',',processFile($file));
				print "\n";
		//}
}

function processFile($file) {
		$res = array();
		$res[] = $file;
		$data = json_decode(file_get_contents($file),1);
		foreach (array('approv','borda','stv') as $method) {
				$res[] = calculateProb($data,$method);
		}
		return $res;
}


function condProb($data) {
		$cond_data = $data['condorcet'];
		$tot = 0;
		foreach($cond_data as $c_eid => $c_prob) {
						$tot += $c_prob;
		}
		return $tot;
}

function calculateProb($data,$method) {
		$cond_data = $data['condorcet'];
		$method_data = $data[$method];
		$total_prob = 0;
		$denom = 0;
		foreach($cond_data as $c_eid => $c_prob) {
				if ($c_prob) {
						if (isset($method_data[$c_eid])) {
								$mprob = $method_data[$c_eid]/100;
								$total_prob += $mprob*$c_prob;
						}
						$denom += $c_prob;
				}
		}
		if (!$denom) {
				return 0;
		}
		return round($total_prob/$denom,5);
}
