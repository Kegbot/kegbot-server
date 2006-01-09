<?
   include_once('includes/load-config.php');
   include_once('includes/SmartyBeer.class.php');

   // per-page stuff
   $nav_section = 'main';
   $nav_page = 'main';
   $tplpage = "index.tpl";

   // generate the template processor
   $smarty = new SmartyBeer();
   $smarty->caching=1;

   if ($_GET['clear']) {
      $smarty->clear_all_cache();
   }

   $cid = $_SESSION['drinker']->id;
   // skip computation and SQL if cached
   if (!$smarty->is_cached($tplpage,$cid)) {
      include_once('includes/main-functions.php');
      $smarty->assign('last_drinks',getLastDrinks(5));
      $smarty->assign('drunks',getCurrentDrunks());

      $d = 1;
      if ($HTTP_GET_VARS['d']) {
         $d = $HTTP_GET_VARS['d'];
      }
      $smarty->assign('graphdays',$d);

      // assign current keg temperature
      $curr = getCurrentKegTemp();
      $smarty->assign('curr_keg',loadCurrentKeg());
      $smarty->assign('tags',getLastTags());
      $smarty->assign('keg_temp_c',$curr['temp']);
      $smarty->assign('keg_temp_f',(9.0/5.0)*$curr['temp']+32);
      $smarty->assign('keg_time',$curr['time']);
   }

   $smarty->show_page($tplpage, $cid);

?>
