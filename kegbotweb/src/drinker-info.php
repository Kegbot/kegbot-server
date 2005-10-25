<?
   $nav_section = 'stats';
   $nav_page = 'keginfo';
   $tplpage = "drinker-info.tpl";
   $errpage = "error.tpl";
   include_once('includes/SmartyBeer.class.php');
   include_once('includes/binge-functions.php');

   $smarty = new SmartyBeer();
   $smarty->caching = 1;
   $smarty->cache_lifetime = 6000;
   $history = intval($HTTP_GET_VARS['history']);

   // cache based on query string - alternative; snippet saved
   $reqid = $_SERVER[REQUEST_URI]; 
   $cid = ereg_replace("PHPSESSID=[^&]+&", "", $reqid); 

   if (!$smarty->is_cached($tplpage,$cid)) {
      include_once('includes/main-functions.php');
      $drinker = loadDrinker($HTTP_GET_VARS['drinker']);
      $uid = $drinker->id;

      if($drinker == NULL) {
         $tplpage = $errpage;
         $msg = "Drinker id $history does not exist.";
         $smarty->assign('msg',$msg);
         $smarty->display("top.tpl");
         $smarty->display("$tplpage",$cid);
         $smarty->display("bottom.tpl");
         exit;
      }

      $smarty->assign('drinker',$drinker);
      $smarty->assign('stats',getDrinkerStats($uid));
      $smarty->assign('currentbac',getCurrentBAC($drinker->id));
      $pdrinks = getDrinksSince(time() - 60*60*24,$drinker->id);
      $ounces = 0.0;
      foreach ($pdrinks as $d) {
         $ounces += $d->inOunces();
      }
      $smarty->assign("last24",$ounces);

      if ($history == intval(1)) {
         $drinks = getUserDrinks($uid,"DESC",True);
         $smarty->assign("usehistory",$history);
         $smarty->assign("drinks",$drinks); // TODO - use member function instead
      }

      // assignments: binge-related
      $sessions = getSessions($uid);
      $smarty->assign('sessions',$sessions);

      // now, some session post-processing. this could be done elsewhere but.. ho well.
      $num_sess = 0;
      $sess_min_ounces = 24.0;
      $sess_min_drinks = 2;
      $all_session_ounces_avg = 0.0;
      $max = 0.0;
      foreach ($sessions as $session) {
         $sess_ounces = 0.0;
         foreach ($session->drinks as $drink) {
            $sess_ounces += $drink->inOunces();
         }
         if (sizeof($session->drinks) < $sess_min_drinks || $sess_ounces < $sess_min_ounces) {
            continue;
         }
         $num_sess++;
         $start = $session->getStart();
         $end = $session->getEnd();
         $all_session_ounces_avg += $sess_ounces;
         $all_session_duration_avg += $end - $start;

         $duration = $end - $start;
         if ($duration > $max)
            $max = $duration;
         if ($duration < $min || !isset($min))
            $min = $duration;

      }

      // if there is insufficient session data, do not proceed
      if ($num_sess == 0 || $all_session_duration_avg == 0) {
         $smarty->assign('num_sess',0);
         $smarty->assign('rating',"non-drinker");
      }
      else {
         $all_session_ounces_avg = $all_session_ounces_avg/$num_sess;
         $all_session_duration_avg = $all_session_duration_avg/$num_sess;

         $std_drink_size = 12.0;
         $avg_ounces_second = $all_session_ounces_avg / $all_session_duration_avg;
         if ($all_session_duration_avg < 60*60) {
            // because, if we only have one 10-minute session to go on... no good
            $avg_ounces_hour = $all_session_ounces_avg;
            $avg_drinks_hour = $avg_ounces_hour / $std_drink_size;
         }
         else {
            $avg_ounces_hour = $avg_ounces_second * 60 * 60;
            $avg_drinks_hour = $avg_ounces_hour / $std_drink_size;
         }

         $smarty->assign('num_sess',$num_sess);
         $smarty->assign('sess_avg_ounces',$all_session_ounces_avg);
         $smarty->assign('sess_avg_duration',$all_session_duration_avg/60/60);
         $smarty->assign('avg_ounces_hour',$avg_ounces_hour);
         $smarty->assign('avg_drinks_hour',$avg_drinks_hour);

         $smarty->assign('longest_session',$max/60/60);
         $smarty->assign('shortest_session',$min/60/60);

         // pick the binge rating
         $dph = $avg_drinks_hour;
         if ($dph < 0.5) {
            $rating = "<i>harmless</i>";
         }
         elseif ($dph < 1) {
            $rating = "lightweight";
         }
         elseif ($dph < 1.5) {
            $rating = "average";
         }
         elseif ($dph < 2) {
            $rating = "beer guzzler";
         }
         else {
            $rating = "<font color=\"#ff0000\">alcoholic</font>";
         }

         $smarty->assign('rating',$rating);
      }
   }

   $smarty->display("top.tpl");
   $smarty->display("$tplpage",$cid);
   $smarty->display("bottom.tpl");
?>
