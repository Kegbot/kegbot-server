<?
include_once('includes/allclasses.php');
include_once('includes/session.php');
include_once('includes/loggedin-required.php');
$drinker = $_SESSION['drinker'];
postTag($drinker->id,$_POST['message']);
$_SESSION['oneshot_msg'] = "tag posted!";
Header("Location: account.php");
exit;

