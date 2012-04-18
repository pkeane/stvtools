<?php



function testFloor($V) { 
		if ($V%2) { // is odd
				$res = ($V+1)/2;
		} else { // is even
				$res = ($V/2)+1;
		}

		if ($res == floor($V/2)+1) {
				print "OK for $V\n";
		} else {
				print "NOT OK for $V\n";
		}

}


foreach (range(0,100) as $v) {
		testFloor($v);
}
