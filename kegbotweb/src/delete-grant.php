<?
   require_once('includes/allclasses.php');
   require_once('includes/loggedin-required.php');
   require_once('includes/admin-required.php');
   require_once('includes/main-functions.php');

   function deleteGrant($id) {
      $q = "UPDATE `grants` SET `status`='deleted' WHERE `id`='$id' LIMIT 1";
      mysql_query($q);
   }

   deleteGrant($_GET['g']);
   Header("Location: edit-user.php?u={$_GET['u']}");
?>
