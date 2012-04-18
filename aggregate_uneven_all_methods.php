<?php

print "Condorcet:\n";
$cond_data = json_decode(file_get_contents('000_cond.json'),1);
ksort($cond_data);
print_r($cond_data);


print "STV:\n";
$stv_data = json_decode(file_get_contents('000_stv.json'),1);
ksort($stv_data);
print_r($stv_data);

print "Approval\n";
$AV_data = json_decode(file_get_contents('000_AV.json'),1);
ksort($AV_data);
print_r($AV_data);

print "Borda\n";
$BC_data = json_decode(file_get_contents('000_BC.json'),1);
ksort($BC_data);
print_r($BC_data);

calculateBordaProb($cond_data,$BC_data);

function calculateBordaProb($cond_data,$BC_data) {
		$total_prob = 0;
		$denom = 0;
		foreach($cond_data as $c_eid => $c_prob) {
				if ($c_prob) {
						$bprob = $BC_data[$c_eid]/100;
						$total_prob += $bprob*$c_prob;
						$denom += $c_prob;
				}
		}
		print $total_prob."\n";
		print $denom."\n";
}
