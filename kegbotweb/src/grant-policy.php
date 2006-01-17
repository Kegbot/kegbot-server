<?
   require_once('includes/allclasses.php');
   require_once('includes/loggedin-required.php');
   require_once('includes/admin-required.php');
   require_once('includes/main-functions.php');

   function grantPolicy($pid,$did,$exp,$eoz,$edate) {
      if ($exp == 'ounces') {
         $etime= 0;
      }
      if ($exp == 'time') {
         $eoz = 0;
         $etime = strtotime($edate);
      }
      $q = "INSERT INTO `grants` (`user_id`,`expiration`,`policy_id`,`exp_volume`,`exp_time`) VALUES ('$did','$exp','$pid','$eoz','$etime')";
      mysql_query($q);
   }

   foreach ($_POST['drinker'] as $did) {
      grantPolicy($_POST['policy'],$did,$_POST['exptype'],$_POST['expounces'],$_POST['expdate']);
   }
   Header('Location: admin-info.php');
?>
