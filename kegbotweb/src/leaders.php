<?
   include_once('includes/load-config.php');
   include_once('includes/SmartyBeer.class.php');

   $nav_section = 'stats';
   $nav_page = 'findLeaders';
   $tplpage = "leaders.tpl";

   $smarty = new SmartyBeer();

   $disp = 5; //number of rankings to show
   if ($_GET['num']) {
      $disp = $_GET['num'];
   }
   $cid = $disp;
   if(!$smarty->is_cached($tplpage,$cid)) {
      include_once('includes/main-functions.php');

      $smarty->register_function("disp_rank", "dispRank"); 
      $drinklead = Array();
      $keglead = Array();

      $refresh = ($_GET['r'] == 1) ? true : false;
      $smarty->assign('refresh',$refresh);

      $smarty->assign('alltime_vol', getLeadersByVolume(true, $disp));
      $smarty->assign('current_vol', getLeadersByVolume(false,$disp));

      $smarty->assign('alltime_num', getLeadersByCount(true, $disp));
      $smarty->assign('current_num', getLeadersByCount(false,$disp));

      $smarty->assign('alltime_bac', getLeadersByBAC(true, $disp));
      $smarty->assign('current_bac', getLeadersByBAC(false,$disp));

      //$smarty->assign('alltime_binge', getLeadersByBinge(true, $disp));
      //$smarty->assign('current_binge', getLeadersByBinge(false,$disp));
   }

   $smarty->show_page($tplpage,$cid);
?>
