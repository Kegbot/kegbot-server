<?
   require_once('includes/session.php');
   if (!isset($_SESSION['drinker']) || ! $_SESSION['drinker']->isAdmin() ) {
      $_SESSION['oneshot_msg'] = "you need to be an admin to access that page.";
      if (!isset($_SESSION['login_action'])) {
         $_SESSION['login_action'] = $_SERVER['REQUEST_URI'];
      }
      Header("Location:/account.php");
      exit;
   }
?>
