<?php

$file = 'hist_stv.json';


$data = json_decode(file_get_contents($file),1);
ksort($data);
print_r($data);
