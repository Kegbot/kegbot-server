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
   $d = loadDrinker($_GET['u']);
   $smarty->assign("target",$d);
   $smarty->assign("grants",getUserGrants($drinker->id));

   
   $smarty->show_page("edit-user.tpl",$cid);

?>
