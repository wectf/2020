<?php


function error($info){
    echo json_encode(array(
        "success" => 0,
        "message" => $info,
        "result" => null,
    ));
    exit();
}

function result($info){
    echo json_encode(array(
       "success" => 1,
       "message" => "",
       "result" => $info,
    ));
}

function call($object){
    $object = null;
}

function get_user_obj($user_obj) : \Objects\User{
    return unserialize($user_obj);
}


function get_cursor(){
    $cursor = new mysqli(getenv("DB_HOST"), getenv("DB_UN"), getenv("DB_PW"), getenv("DB_NAME"));
    if ($cursor->connect_errno)
        error("System error, contact admin please");
    return $cursor;
}
