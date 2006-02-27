<?
   include_once('includes/SmartyBeer.class.php');

   $tplpage = "drink-info.tpl";
   $cid = $_GET['drink'];
   $smarty = new SmartyBeer();
   $smarty->show_page($tplpage, $drink);
?>
