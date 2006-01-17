<?
   include_once('includes/SmartyBeer.class.php');

   $tplpage = "drinker-info.tpl";
   $cid = $_GET['drinker'];
   $smarty = new SmartyBeer();
   $smarty->assign('id', $_GET['drinker']);
   $smarty->show_page($tplpage, $cid);
?>
