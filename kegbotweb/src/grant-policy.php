<?
   require_once('includes/allclasses.php');
   require_once('includes/loggedin-required.php');
   require_once('includes/admin-required.php');
   require_once('includes/main-functions.php');
   require_once('includes/units.php');

   foreach ($_POST['drinker'] as $did) {
      grantPolicy($_POST['policy'],
         $did,
         $_POST['exptype'],
         $_POST['expounces'],
         $_POST['expdate']);
   }
   Header('Location: admin-info.php');
?>
