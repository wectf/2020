<?php
error_reporting(0);
require_once "Helpers.inc";
$_action = $_POST["action"];

switch ($_action){
    case "login":
        login();
        break;
    case "register":
        register();
        break;
    case "user_notes":
        user_notes();
        break;
    case "get_note":
        get_note();
        break;
    case "add_note":
        add_note();
        break;
}

function login(){
    $username = $_POST["username"];
    $password = $_POST["password"];
    $u = new \Objects\User();
    $u->__init_with_content($username, $password);
    $u->__login();
    result(serialize($u));
}

function register(){
    $username = $_POST["username"];
    $password = $_POST["password"];
    $u = new \Objects\User();
    $u->__init_with_content($username, $password);
    $u->__register();
    result(serialize($u));
}

function user_notes(){
    $user_obj = get_user_obj($_POST["user"]);
    result($user_obj->__get_notes());
}


function get_note(){
    $note_token = $_POST["token"];
    $note = new \Objects\Note();
    $note->__init_with_token($note_token, true);
    $note->__echo();
}


function add_note(){
    $content = $_POST["content"];
    $user_obj = get_user_obj($_POST["user"]);
    $note = new \Objects\Note();
    $note->__init_with_content($user_obj, $content);
    $note->__save();
    $note->__echo();
}

