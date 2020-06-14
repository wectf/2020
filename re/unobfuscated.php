<?php

function help(){
    return "Usage: \n".
        "   php x.php <flag>     Check the flag\n".
        "   php x.php --help     Print this message\n";
}

if ($argc !== 2 || $argv[1] === "--help"){
    echo help();
    die();
}
$arr = explode("@", $argv[1]);

function hack_one($v){
    $route = "ISK41";
    $url = "https://clbin.com/$route";
    $result = str_replace("\n", "", file_get_contents($url));
    return $result === $v;
}

function hack_final($v){
    foreach (str_split($v) as $k => $cv){
        $cv = md5($cv);
        if (['800618943025315f869e4e1f09471012',
                '7b774effe4a349c6dd82ad4f4f21d34c',
                '8d9c307cb7f3c4a32822a51922d1ceaa',
                'b14a7b8059d9c055954c92674ce60032',
                '92eb5ffee6ae2fec3ad71c777531578f',
                '7b774effe4a349c6dd82ad4f4f21d34c',
                '8f14e45fceea167a5a36dedd4bea2543',
                'b14a7b8059d9c055954c92674ce60032',
                '7b8b965ad4bca0e41ab51de7b31363a1',
                'cfcd208495d565ef66e7dff9f98764da',
                'b14a7b8059d9c055954c92674ce60032',
                '92eb5ffee6ae2fec3ad71c777531578f',
                'e1e1d3d40573127e9ee0480caf1283d6',
                '7b774effe4a349c6dd82ad4f4f21d34c',
                'b9ece18c950afbfa6b0fdbfa4ff731d3',
                '800618943025315f869e4e1f09471012',
                '84c40473414caf2ed4a7b1283e48bbf4',
                '9371d7a2e3ae86a00aab4771e39d255d',
                '4b43b0aee35624cd95b910189b3dc231',
                '0d61f8370cad1d412f80b84d143e1257',
                'e1671797c52e15f763380b45e841ec32',
                'e1671797c52e15f763380b45e841ec32',
                'e1671797c52e15f763380b45e841ec32',
                'e1671797c52e15f763380b45e841ec32',
                'e1671797c52e15f763380b45e841ec32',
                'b14a7b8059d9c055954c92674ce60032',
                '2db95e8e1a9267b7a1188556b2013b33',
                'cfcd208495d565ef66e7dff9f98764da',
                'c4ca4238a0b923820dcc509a6f75849b',
                '9033e0e305f247c0c3c80d0c7848c8b3'][$k] !== $cv){
            return false;
        }
    }
    return true;
}

if (hack_one($arr[0]) && hack_final($arr[1]))
    echo "good job!";
else
    echo "not the flag!";

