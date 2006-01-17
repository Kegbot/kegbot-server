<?
   include_once('includes/load-config.php');
   include_once('includes/SmartyBeer.class.php');

   $tplpage = "index.tpl";

   // generate the template processor
   $smarty = new SmartyBeer();
   $smarty->caching=1;

   if ($_GET['clear']) {
      $smarty->clear_all_cache();
   }

   // show the page
   $cid = $_SESSION['drinker']->id;
   $smarty->show_page($tplpage, $cid);

?>
