<?php
// In PHP versions earlier than 4.1.0, $HTTP_POST_FILES should be used instead
// of $_FILES.
include_once('includes/allclasses.php');
include_once('includes/session.php');
include_once('includes/loggedin-required.php');

$uploaddir = "/data/kegbot/htdocs/userpics/{$cfg['edition']}";
$drinker = $_SESSION['drinker'];

$ext = $_FILES['userfile']['type'];
list($bogus, $ext) = split("/",$ext);

$basefile = $uploaddir. '/' . $drinker->username;
$uploadfile = "$basefile.$ext";
$newfile = "$basefile.jpg";


#chgrp($userdir,"www-data");
#chmod($userdir,0775);
if (!move_uploaded_file($_FILES['userfile']['tmp_name'], $uploadfile)) {
   $_SESSION['oneshot_msg'] = "<b>error!</b> the file upload failed. hmm, that shouldn't happen..";
   Header("Location: account.php");
   exit;
}
exec("convert $uploadfile $newfile");
$_SESSION['oneshot_msg'] = "success - image uploaded to $newfile";
Header("Location: account.php");
?>
