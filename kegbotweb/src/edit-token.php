<?
   include_once('includes/allclasses.php');
   include_once('includes/admin-required.php');
   include_once('includes/main-functions.php');
   include_once('includes/SmartyBeer.class.php');

   $smarty = new SmartyBeer();
   $cid = $_GET['id'];

   // set up available policies
   $smarty->caching = 0;
   $smarty->assign("token",getToken($_GET['id']));

   $smarty->show_page("edit-token.tpl",$cid);

?>
