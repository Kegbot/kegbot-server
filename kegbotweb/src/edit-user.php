<?
   include_once('includes/allclasses.php');
   include_once('includes/admin-required.php');
   include_once('includes/main-functions.php');
   include_once('includes/SmartyBeer.class.php');

   $smarty = new SmartyBeer();
   $smarty->caching = 0;
   $cid = 0;

   // set up available policies
   $smarty->assign("policies",getAllPolicies());
   $drinker = loadDrinker($_GET['u']);
   $smarty->assign("drinker",$drinker);
   $smarty->assign("grants",getUserGrants($drinker->id));

   
   $smarty->display("top.tpl");
   $smarty->display("edit-user.tpl",$cid);
   $smarty->display("bottom.tpl");

?>
