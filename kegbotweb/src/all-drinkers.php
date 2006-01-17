<?
   include_once('includes/SmartyBeer.class.php');

   $tplpage = "all-drinkers.tpl";
   $smarty = new SmartyBeer();
   $smarty->show_page($tplpage, $cid);
?>
