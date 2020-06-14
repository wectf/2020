<?php
// a safe csp :)>
header("content-security-policy", "default-src 'none';script-src 'none'; font-src 'self' ;connect-src 'self';style-src 'self' https://stackpath.bootstrapcdn.com/;frame-ancestors 'none'; base-uri 'self'; form-action 'self';");
// login function for admin
function login()
{
	$token = @$_GET["token"];
	if (hash_equals($token, getenv("ADMIN_TOKEN"))){
		header("Location: /");
		setcookie("admin_token", $token, time() + 600000, "/");
	} else {
		die("Incorrect token");
	}
}

// check whether current user is logged in
function is_logged_in()
{
	return @hash_equals($_COOKIE["admin_token"], getenv("ADMIN_TOKEN"));
}

// search the secret from vault
function search_secret($limit=-1)
{
    // construct secret array
	$secret_arr = [];

	if (is_logged_in()){
		array_push($secret_arr, str_repeat(getenv("FLAG"), 100)); // shou: [TODO] add more of my secret here!!
	} else {
		array_push($secret_arr, str_repeat("we{demoflag}", 100));
	}
	// apply filters
	if ($limit > 0){
		if ($limit > count($secret_arr)){
			trigger_error("Limit is greater than length of array!", E_USER_WARNING);
		} else {
			$secret_arr = array_splice($secret_arr, 0, $limit);
		}
	}
	// search from array
	$needle = @$_GET["needle"];
	$needle_len = strlen($needle);
	$result = [];
	foreach ($secret_arr as $v) {
		$loc = @strpos($v, $needle);
		if ($loc === false){
			continue;
		}
		// highlight the matched part
		$first_part = substr($v, 0, $loc);
		$second_part = substr($v, $loc, $needle_len);
		$third_part = substr($v, $loc + $needle_len);
		array_push($result, $first_part . "<strong>$second_part</strong>" . $third_part . "<br>");
	}
	return $result;
}


switch (@$_GET["_action"]) {
	case "login":
		login();
		break;
	case "search_html":
		$result = search_secret(@$_GET["limit"]);
		foreach ($result as $v) {
			echo "$v<br>";
		}
		break;
	case "search_json":
		header('Content-Type: application/json');
		echo json_encode(
			array("result" => search_secret(@$_GET["limit"]))
		);
		die();
		break;
	case 'highlight_file':
	    // show source code of this file
		highlight_file(__FILE__);
		die();
		break;
	default:
		if (is_logged_in()){
			echo "<h1>Welcome Admin!</h1><br>";
		}
		break;
}

?>

<!DOCTYPE html>
<html>
<head>
	<title>Flag Vault</title>
	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">

</head>
<body class="container">
	<br>
	<div class="alert alert-primary" role="alert">
	  Real secret reveals when you logged in, but you can <a href="/?_action=highlight_file">reveal source code</a> now!
	  <br>
	  <a href="https://uv.wectf.io">Report Issue</a>
	</div>
	<label>Admin Login</label>
	<form action="/">
		<input name="token" placeholder="admin token" class="form-control" />
		<input name="_action" value="login" hidden="" />
		<br>
		<input type="submit" class="btn btn-primary" />		
	</form>
	<br>
	<label>What secret would you like to search?</label>
	<form action="/">
		<input name="needle" class="form-control" />
		<input name="_action" value="search_html" hidden="" />
		<br>
		<input type="submit" value="Search" class="btn btn-secondary" />		
	</form>
</body>
</html>
