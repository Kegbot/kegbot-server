<?
   $tplpage = "keg-info.tpl";

   include_once('includes/SmartyBeer.class.php');
   $smarty = new SmartyBeer();
   $cid = $_GET['keg'];
   $smarty->assign('id',$_GET['keg']);
   $smarty->show_page("$tplpage",$cid);
?>
