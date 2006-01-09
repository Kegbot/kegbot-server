<?
   $nav_section = 'stats';
   $nav_page = 'drinkinfo';

   require_once('includes/main-functions.php');
   require_once('includes/SmartyBeer.class.php');
   require_once('includes/session.php');

   $action = $HTTP_POST_VARS['action'];
   if ($HTTP_GET_VARS['clear']){
      $_SESSION['login_attempts'] = 0;
   }

   if (!$action) {
      $action = $HTTP_GET_VARS['action'];
   }
   if (!strcmp($action,"logout")) {
      unset($_SESSION['loggedin']);
      unset($_SESSION['drinker']);
   }
   elseif (!strcmp($action,"login")) {
      $user = $HTTP_POST_VARS['login'];
      $pass = $HTTP_POST_VARS['password'];

      if ($drinker = validateUser($user,$pass)) {
         $_SESSION['loggedin'] = 1;
         $_SESSION['drinker'] = $drinker;
         $_SESSION['login_attempts'] = 0;
      }
      else {
         $_SESSION['login_attempts'] += 1;
         $_SESSION['oneshot_msg'] = '<b>invalid username or password.</b> drink again!';
      }
   }

   if ($_SESSION['loggedin']) {
      if ($_SESSION['login_action']) {
         $loc = $_SESSION['login_action'];
         unset($_SESSION['login_action']);
         Header("Location:$loc");
      }
      else {
         Header("Location:/account.php");
      }
      exit;
   }

   $smarty = new SmartyBeer();
   $smarty->caching = 0;
   $smarty->assign('attempted',$_SESSION['login_attempts']);

   // oneshot message (session)
   if ($_SESSION['oneshot_msg']) {
      $smarty->assign('oneshot_msg',$_SESSION['oneshot_msg']);
      unset($_SESSION['oneshot_msg']);
   }

   $smarty->show_page("login.tpl");
?>
