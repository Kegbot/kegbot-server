<?
   include_once('includes/load-config.php');
   include_once('includes/SmartyBeer.class.php');

   $nav_section = 'stats';
   $nav_page = 'findLeaders';
   $tplpage = "all-drinkers.tpl";

   $smarty = new SmartyBeer();

   if(!$smarty->is_cached($tplpage)) {
      $stats = array();
      include_once('includes/main-functions.php');
      $drinkers = getAllDrinkers();
      $sorted = array();
      foreach ($drinkers as $drinker) {
         $drinkers[$drinker->id]->stats = getDrinkerStats($drinker->id);
      }
      uasort($drinkers,"ozsort");
      $smarty->assign('drinkers', $drinkers);
   }

   // display the top
   $smarty->display("top.tpl");
   $smarty->display($tplpage);
   $smarty->display("bottom.tpl");
?>
