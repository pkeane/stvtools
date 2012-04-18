<?php




function binomial_coeff($n, $k) {

		$j = $res = 1;

		if($k < 0 || $k > $n)
				return 0;
		if(($n - $k) < $k)
				$k = $n - $k;

		while($j <= $k) {
				         $res *= $n--;
				        $res /= $j++;
				//$res = bcmul($res, $n--);
				//$res = bcdiv($res, $j++);
		}

		return $res;

}

print binomial_coeff(455,33);
