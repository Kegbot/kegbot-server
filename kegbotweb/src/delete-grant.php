<?
   require_once('includes/allclasses.php');
   require_once('includes/loggedin-required.php');
   require_once('includes/admin-required.php');
   require_once('includes/main-functions.php');

   function updateGrant($id, $status) {
      $q = "UPDATE `grants` SET `status`='$status' WHERE `id`='$id' LIMIT 1";
      mysql_query($q);
   }

   updateGrant($_GET['g'], $_GET['action']);
   Header("Location: edit-user.php?u={$_GET['u']}");
?>
