<?
   // page-specific stuff
   $nav_section = 'stats';
   $nav_page = 'keginfo';
   $tplpage = "keg-info.tpl";

   // generate the template processor
   include_once('includes/load-config.php');
   include_once('includes/SmartyBeer.class.php');
   $smarty = new SmartyBeer();

   // cache based on query string - alternative; snippet saved
   $reqid = $_SERVER[REQUEST_URI];
   $cid = ereg_replace("PHPSESSID=[^&]+&", "", $reqid); 

   $history = $HTTP_GET_VARS['history'];

   // skip computation and SQL if cached
   if (!$smarty->is_cached($tplpage, $cid)) {
      include_once('includes/main-functions.php');

      $keg = loadKeg($HTTP_GET_VARS['keg']);
      if (intval($history) == 1) {
         $smarty->assign("usehistory",$history);
         $drinks = getAllDrinks($keg->id);
         $smarty->assign("drinks",$drinks); // TODO - use member function instead
      }
      $drinks = getAllDrinks($keg->id);
      $last_drink = $drinks[0];
      $smarty->assign('keg',$keg);
      $smarty->assign('full_pct',getKegContents($keg)*100);
      $smarty->assign('drinks_served',count($drinks));
      $smarty->assign('last_drink',$last_drink);
      $leaders = getLeadersByVolume(false,100,$keg->id);
      $drinkers = array();
      foreach ($leaders as $l) {
         $drinker = $l['drinker'];
         $drinkers[$drinker->id] = $drinker;
         $stats = array();
         $stats['alltime_vol'] = $leaders[$drinker->id]['amount'];
         $drinkers[$drinker->id]->stats = $stats;
      }
      //uasort($drinkers,"ozsort");
      $smarty->assign('keg_volleaders', $drinkers);
   }

   // display the stuff
   $smarty->display("top.tpl");
   $smarty->display("$tplpage",$cid);
   $smarty->display("bottom.tpl");
?>
