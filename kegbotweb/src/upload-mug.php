<?php
// In PHP versions earlier than 4.1.0, $HTTP_POST_FILES should be used instead
// of $_FILES.
include_once('includes/allclasses.php');
include_once('includes/session.php');
include_once('includes/loggedin-required.php');
$uploaddir = '/data/kegbot/htdocs/userpics/';
$drinker = $_SESSION['drinker'];
$userdir = $uploaddir . $drinker->id .'/';
$slot = $_POST['slot'];
$slot = "1";
if (!$slot) {
   $_SESSION['oneshot_msg'] = "<b>error!</b> you need to select a slot to uplaod this photo";
   Header("Location: account.php");
   exit;
}
$ext = $_FILES['userfile']['type'];
list($bogus, $ext) = split("/",$ext);
$uploadfile = $userdir. $slot . "." . $ext;

if (!is_dir($userdir)) {
   mkdir($userdir);
   chgrp($userdir,"www-data");
   chmod($userdir,0775);
}
if (move_uploaded_file($_FILES['userfile']['tmp_name'], $uploadfile)) {
   $_SESSION['oneshot_msg'] = "success - image upload to slot $slot";
   Header("Location: account.php");
   exit;
} else {
   $_SESSION['oneshot_msg'] = "<b>error!</b> the file upload failed. hmm, that shouldn't happen..";
   Header("Location: account.php");
   exit;
}
?>
