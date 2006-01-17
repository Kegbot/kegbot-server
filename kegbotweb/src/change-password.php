<?
   include_once('includes/allclasses.php');
   include_once('includes/session.php');
   include_once('includes/loggedin-required.php');
   include_once('includes/main-functions.php');
   $drinker = $_SESSION['drinker'];
   $newpass = $_POST['newpass'];
   $confirm = $_POST['confirm'];
   if (strcmp($newpass,$confirm)) {
      $_SESSION['oneshot_msg'] = "error! passwords do not match; no change";
   }
   else {
      updatePassword($drinker,$_POST['newpass']);
      $_SESSION['oneshot_msg'] = "password changed succesfully";
   }

   header("Location:account.php");
?>
