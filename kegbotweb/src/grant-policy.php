<?
   require_once('includes/allclasses.php');
   require_once('includes/loggedin-required.php');
   require_once('includes/admin-required.php');
   require_once('includes/main-functions.php');
   require_once('includes/units.php');

   function grantPolicy($pid, $did, $exp, $eoz, $edate) {
      $etime = 0;
      $evol = 0;
      if (!strcmp($exp, "volume")) {
         $evol = ounces_to_volunits($eoz);
      }
      if (!strcmp($exp, "time")) {
         $etime = strtotime($edate);
      }
      $q = "INSERT INTO `grants` (`status`,`user_id`,`expiration`,`policy_id`,`exp_volume`,`exp_time`,`exp_drinks`,`total_volume`,`total_drinks`) VALUES ('active','$did','$exp','$pid','$evol','$etime',0,0,0)";
      mysql_query($q);
   }

   foreach ($_POST['drinker'] as $did) {
      grantPolicy($_POST['policy'],
         $did,
         $_POST['exptype'],
         $_POST['expounces'],
         $_POST['expdate']);
   }
   Header('Location: admin-info.php');
?>
