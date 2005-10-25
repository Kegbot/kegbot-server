<?
   include_once('includes/load-config.php');
   include_once('includes/SmartyBeer.class.php');

   $nav_section = 'stats';
   $nav_page = 'findLeaders';
   $tplpage = "leader-board.tpl";

   $smarty = new SmartyBeer();
   $smarty->caching = 0; 

   if(!$smarty->is_cached($tplpage)) {
      include_once('includes/main-functions.php');

      $smarty->register_function("disp_rank", "dispRank"); 
      $drinklead = Array();
      $keglead = Array();
      $disp = 5; //number of rankings to show

      $smarty->assign('alltime_vol', getLeadersByVolume(true, $disp));
      $smarty->assign('current_vol', getLeadersByVolume(false,$disp));

      $smarty->assign('alltime_num', getLeadersByCount(true, $disp));
      $smarty->assign('current_num', getLeadersByCount(false,$disp));

      $smarty->assign('alltime_bac', getLeadersByBAC(true, $disp));
      $smarty->assign('current_bac', getLeadersByBAC(false,$disp));
   }

   // display the top
   $smarty->display("top.tpl");
   $smarty->display($tplpage);
   $smarty->display("bottom.tpl");
?>
