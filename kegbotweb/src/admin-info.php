<?
   require_once('includes/allclasses.php');
   require_once('includes/loggedin-required.php');
   require_once('includes/admin-required.php');
   require_once('includes/main-functions.php');
   require_once('includes/SmartyBeer.class.php');

   $smarty = new SmartyBeer();
   $smarty->caching = 0;

   // set up select name of drinkers 
   $smarty->assign("drinkers",getAllDrinkers());
   $smarty->assign("tokens",getAllTokens());
   $smarty->assign("policies",getAllPolicies());

   $smarty->show_page("admin-info.tpl",$cid);

?>
