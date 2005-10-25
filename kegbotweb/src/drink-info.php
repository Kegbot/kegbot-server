<?
   $nav_section = 'stats';
   $nav_page = 'drinkinfo';
   $tplpage = "drink-info.tpl";
   $errpage = "error.tpl";

   include_once('includes/SmartyBeer.class.php');

   $smarty = new SmartyBeer();
   $smarty->caching=0;
   
   if(!$smarty->is_cached($tplpage)) {
      include_once('includes/main-functions.php');
      global $cfg;

      $drinkid = $HTTP_GET_VARS['drink'];
      $drink = getDrink($drinkid);
      if($drink == NULL) {
	 $tplpage = $errpage;
	 $msg = "Drink id $drinkid does not exist.";
	 $smarty->assign('msg',$msg);
      } else if($drink->totalticks < $cfg['flow']['minticks']){
	 $msg = "Drink id #$drinkid is a balk.  That is, it was an attempted pour that was either aborted, or the result of a glitch in the system.  Though they are recorded for posterity there is no reason for you to care about them. Please stop entering random drink id's into the URL.";
	 $tplpage = $errpage;
	 $smarty->assign('msg',$msg);
      } else {
	 $uid = $drink->user_id;
	 $keg = $drink->keg_id;
	 $id = $drink->id;
	 
	 $smarty->assign('drink',$drink);
	 $cond = Array("`user_id` = '$uid'");
	 //$drinknum = findRankLC('starttime',$id,'drinks',$cond);
	 $smarty->assign('drinknum',$drinknum);
	 $cond = Array("`keg_id` = '$keg'");
	 //$kegdrinks = findRankLC('starttime',$id,'drinks',$cond);
	 $smarty->assign('kegdrinknum',$kegdrinks);
	 //$totalnum = findRankLow('starttime',$id,'drinks');
	 $smarty->assign('totalnum',$totalnum);
	 //$c_entry = getCacheUser($uid);
	 //$avg = $c_entry->totaloz / $c_entry->totaldrinks;
	 $size = $drink->getSize();
	 $smarty->assign('size',$size);
	 $smarty->assign('hist_avg',$avg);
	 //$c_entry = getCacheUser(0);
	 //$avg = $c_entry->totaltime / $c_entry->totaldrinks;
	 $smarty->assign('time_avg',$avg);
	 $diff = $avg - ($drink->endtime - $drink->starttime);
	 $smarty->assign('diff_pos',$diff);
	 $smarty->assign('diff_neg',$diff * -1);
      }
   }
   
   // display the top
   $smarty->display("top.tpl");
   $smarty->display("$tplpage");
   $smarty->display("bottom.tpl");
?>
