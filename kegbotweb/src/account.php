<?
   include_once('includes/load-config.php');

   $nav_section = 'stats';
   $nav_page = 'drinkinfo';

   require_once('includes/main-functions.php');
   require_once('includes/SmartyBeer.class.php');
   require_once('includes/loggedin-required.php');

   $smarty = new SmartyBeer();
   $drinker = $_SESSION['drinker'];
   $cid = $drinker->id;
   $smarty->caching = 0;

   $smarty->assign('drinker',$drinker);
   $smarty->assign('genders',Array('male','female'));
   $smarty->assign('grants',getUserGrants($drinker->id));
   $c = getAccountCharges($drinker->id);
   $smarty->assign('charges',$c);
   $total = 0;
   foreach ($c as $charge) {
      $total += $charge->amt;
   }
   $smarty->assign('balance',$total);

   // oneshot message (session)
   if ($_SESSION['oneshot_msg']) {
      $smarty->assign('oneshot_msg',$_SESSION['oneshot_msg']);
      unset($_SESSION['oneshot_msg']);
   }

   $smarty->show_page("account.tpl");
?>
