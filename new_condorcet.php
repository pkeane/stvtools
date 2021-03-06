<?php

ini_set('display_errors',1);
ini_set('display_startup_errors',1);
error_reporting(E_ALL);

function getBallotPairs($cands,$ballot,$pairs) {
		$i = 0;
		foreach ($ballot as $placed_cand) {
				$j = 0;
				foreach ($ballot as $cand) {
						if ($placed_cand != $cand) {
								if ($i < $j) {
										//record a "win"
										$pairs[$placed_cand][$cand] += 1;
								}
								if ($j < $i) {
										//	$pairs[$cand][$placed_cand] += 1;
								}
						} 
						$j++;
				}
				$i++;
		}
		//cands not on ballot
		$missing = array();
		foreach ($cands as $miss) {
				if (!in_array($miss,$ballot)) {
						$missing[] = $miss;
				}
		}
		foreach ($missing as $m) {
				foreach ($ballot as $c) {
						$pairs[$c][$m] += 1;
				}
		}
		return $pairs;
};

function getAllPairs($cands) {
		$pairs = array();
		foreach ($cands as $outercand) {
				foreach ($cands as $innercand) {
						if (!isset($pairs[$innercand])) {
								$pairs[$innercand] = array();
						}
						if ($outercand != $innercand) {
								$pairs[$innercand][$outercand] = 0;
						}
				}
		}
		return $pairs;
}

function runBallots($year,$cands,$ballots) {
		$cprobs = array();
		$final_probs = array();
		$pairs = getAllPairs($cands);
		foreach ($ballots as $b) {
				$pairs = getBallotPairs($cands,$b,$pairs);
		}

		foreach ($ballots as $ballot) {
				foreach ($cands as $I) {
						$cprobs[$I] = array();
						foreach ($cands as $J) {
								if ($I != $J) {
										$cprobs[$I][$J] = '';
										$ballots_with_neither = array();
										foreach ($ballots as $bal) {
												if (!in_array($I,$bal) and !in_array($J,$bal)) {
														$ballots_with_neither[] = $bal;
												}
										}

										//per Tse-min algorithm
										$V = count($ballots);
										$M = floor($V/2)+1; 
										$C = count($cands);

										$R = count($ballots) - count($ballots_with_neither);
										$S = count($ballots_with_neither);
										$T = $pairs[$I][$J];


										$IbeatJ = $pairs[$I][$J];
										$JbeatI = $pairs[$J][$I];
										$prob = $IbeatJ/($IbeatJ+$JbeatI);

										$Q = $prob;

										$k_range = $M-$T-1;


										if (($M-$S <= $T) && ($T < $M)) {
												$sum = 0;
												foreach (range(0,$k_range) as $k) {
														$sum += binomial($S,$Q,$k);
												}
												$new_prob = 1-$sum;
										}

										if ($T+$S < $M) {
												$new_prob = 0;
										}

										if ($T >= $M) {
												$new_prob = 1;
										}

										$cprobs[$I][$J] = $new_prob;

										global $PRINT;
										if ($PRINT) {
												print "\n----------------------\n";
												print "I is $I\n";
												print "J is $J\n";
												print "V is $V\n";
												print "M is $M\n";
												print "C is $C\n";
												print "R is $R\n";
												print "S is $S\n";
												print "T is $T\n";
												print "Q is $Q\n";
												print "k range is $k_range\n";
												print "calculated probability is $new_prob\n";
										}
								} // I != J
						} // foreach J
				} //foreach I
				foreach ($cprobs as $I => $J_array) {
						$final_probs[$I] = array_product($J_array);
				}
		}
		return $final_probs;
}

function binomial($S,$Q,$k) {
		$b_coeff = binomial_coeff($S,$k);
		return $b_coeff*pow($Q,$k)*pow((1-$Q),$S-$k);
}

function binomial_coeff($n,$k) {
		return fact($n)/(fact($k)*fact($n-$k));
}

function fact($int){
		if($int<2)return 1;
		for($f=2;$int-1>1;$f*=$int--);
		return $f;
}

function getCandidates($filepath) {
		$cands = array();
		$data = json_decode(file_get_contents($filepath),1);
		foreach ($data['BALLOTS'] as $ballot) {
				foreach ($ballot as $cand) {
						$cands[$cand] = 1;
				}
		}
		return array_keys($cands);
}


function runElections() {
		$years = array();
		$condorcets = array();
		foreach (new DirectoryIterator('elections') as $fileInfo) {
				if($fileInfo->isDot()) {
						continue;
				} else {
						$filepath = 'elections/'.$fileInfo->getFilename();
						$cands = getCandidates($filepath); 
						$data = json_decode(file_get_contents($filepath),1);
						$year = $data['ELECTION']['id'];
						print $year."\n";
						$ballots = $data['BALLOTS'];
						$cprobs = runBallots($year,$cands,$ballots);
						$years[$year]  = $cprobs;
				}
		}
		return $years;
}


$PRINT = 0;

$years = runElections();

$json_result = json_encode($years);

file_put_contents('result_'.time().'.json',$json_result);

print $json_result;
print "\n\n\n";
