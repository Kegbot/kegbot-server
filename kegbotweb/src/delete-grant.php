<?
   require_once('includes/allclasses.php');
   require_once('includes/loggedin-required.php');
   require_once('includes/admin-required.php');
   require_once('includes/main-functions.php');

   deleteGrant($_GET['g']);
   Header("Location: edit-user.php?u={$_GET['u']}");
?>
