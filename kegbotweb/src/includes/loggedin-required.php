<?
   include_once('includes/session.php');
   if (!isset($_SESSION['loggedin'])) {
      $_SESSION['oneshot_msg'] = "<b>error:</b> you've gotta log in to do that, buddy!";
      $_SESSION['login_action'] = $_SERVER['REQUEST_URI'];
      header("Location:login.php");
      exit;
   }
?>
