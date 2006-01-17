<?
   $tplpage = "drink-info.tpl";

   include_once('includes/SmartyBeer.class.php');
   $smarty = new SmartyBeer();
   $smarty->show_page("$tplpage");
?>
