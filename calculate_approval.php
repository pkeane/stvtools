<?php

function getApproval($result,$filepath) {
		$cands = array();
		$data = json_decode(file_get_contents($filepath),1);
		$seats = (int) $data['ELECTION']['seats'];
		foreach ($data['BALLOTS'] as $ballot) {
				foreach (range(0,$seats-1) as $num) {
						if (isset($ballot[$num])) {
								$cname = $ballot[$num];
								if (!isset($cands[$cname])) {
										$cands[$cname] = 0;
								}
								$cands[$cname] += 1;
						}
				}
		}
		arsort($cands);
		$cands = array_slice($cands,0,$seats);
		$result[$data['ELECTION']['id']] = $cands;
		return $result;
}



$result = array();

foreach (new DirectoryIterator('elections') as $fileInfo) {
		if($fileInfo->isDot()) {
				continue;
		} else {
				$result = getApproval($result,'elections/'.$fileInfo->getFilename());
		}
}

ksort($result);
print json_encode($result);
