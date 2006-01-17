<?
include_once('includes/allclasses.php');
include_once('includes/session.php');
include_once('includes/loggedin-required.php');
$drinker = $_SESSION['drinker'];

function postTag($drinkerid, $message) {
   $bac = getCurrentBAC($drinkerid);
   $posttime = time();
   $message = addslashes($message);
   $q = "INSERT INTO `wall` (`user_id`,`postdate`,`message`,`bac`) VALUES ('$drinkerid','$posttime','$message','$bac')";
   mysql_query($q);
}


postTag($drinker->id,$_POST['message']);
$_SESSION['oneshot_msg'] = "tag posted!";
Header("Location: account.php");
exit;

