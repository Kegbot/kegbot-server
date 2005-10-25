<?
   include('includes/main-functions.php');
   include('includes/session.php');

   if (!$_SESSION['loggedin']) {
      header("Location:/login.php");
   }
   $drinker = $_SESSION['drinker'];
   updateUser($drinker->id,$HTTP_POST_VARS);
   header("Location:/account.php");
?>
