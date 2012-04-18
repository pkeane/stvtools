<?php


$file = $argv[1];

$data = json_decode(file_get_contents($file),1);

ksort($data);

print json_encode($data);

