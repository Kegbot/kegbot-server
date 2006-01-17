<?
   include('includes/main-functions.php');
   include('includes/session.php');

   function updateUser($uid,$vars) {
      $fields = Array('username','weight','gender');

      foreach ($fields as $field) {
         $q = "UPDATE `users` SET `{$field}`='{$vars[$field]}' WHERE `id`='$uid' LIMIT 1";
         mysql_query($q);
      }
      $_SESSION['drinker'] = loadDrinker($uid);
   }

   if (!$_SESSION['loggedin']) {
      header("Location:/login.php");
   }
   $drinker = $_SESSION['drinker'];
   updateUser($drinker->id,$HTTP_POST_VARS);
   header("Location:account.php");
?>
