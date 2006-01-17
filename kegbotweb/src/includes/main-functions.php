<?
   require_once("load-config.php");
   require_once("allclasses.php");
   include_once('binge-functions.php');
   global $cfg;
   @mysql_connect($cfg['db']['host'], $cfg['db']['user'], $cfg['db']['password']) || die("the kegbot front end can't connect to the backend. check db config in cfg.inc.php");
   mysql_select_db($cfg['db']['db']) || die("the kegbot front end can't find this database ({$cfg['db']['db']}). uh oh.");
   $r = mysql_query("SELECT UNIX_TIMESTAMP(NOW())");
   $DBTIME = mysql_fetch_array($r);
   $GLOBALS['dbtime'] = $DBTIME[0];

   $KEGS = Array();
   $DRINKS = Array();
   $DRINKERS = Array();
   $TOKENS = Array();
   $TBLCOLS = Array();

   //Returns Today,Yesterday, Day of week ('l')
   //up to 6 days ago. Otherwise it uses $format
   function RelDate($epoch, $format = DATE_RFC822) {
      $day    = date('j',$epoch);
      $today  = date('j',time());
      $yday   = date('j',strtotime("-1 day"));

      //account for last month's day
      switch($day) {
          case $today:    return "Today";                break;
          case $yday:    return "Yesterday";            break;
          default:       
              //Look up to one week ago
              for($i=1;$i<=6;$i++) {
                  $pastday = date('j',strtotime("-$i days"));
                  if($day == $pastday) {
                      return(date('l',$epoch));
                  }
              }

              //If we made it to here, just print the format given
              return date($format,$epoch);
      }
   }

   function getAccountCharges($did) {
      $charges = array();
      $drinks = getUserDrinks($did);
      $kegs = getAllKegs();
      foreach ($kegs as $keg) {
         $drinks = getDrinksByQuery("SELECT * FROM `drinks` WHERE `user_id`='$did' AND `keg_id`='{$keg->id}'");
         $kegcost = 0.0;
         foreach ($drinks as $d) {
            $kegcost += $d->getCost();
         }
         if ($kegcost != 0.0) {
            $charges[] = new Charge("kegtotal","keg {$keg->id} total","",$kegcost);
         }
      }
      return $charges;
   }
   function updatePassword($d,$newpass) {
      $q = "UPDATE `users` SET `password`=MD5('$newpass') WHERE `id`='{$d->id}' LIMIT 1";
      mysql_query($q);
   }
   function postTag($drinkerid, $message) {
      $bac = getCurrentBAC($drinkerid);
      $posttime = time();
      $message = addslashes($message);
      $q = "INSERT INTO `wall` (`user_id`,`postdate`,`message`,`bac`) VALUES ('$drinkerid','$posttime','$message','$bac')";
      mysql_query($q);
   }
   function getLastTags($num = 5) {
      $q = "SELECT * FROM `wall` ORDER BY `postdate` DESC LIMIT $num";
      $res = mysql_query($q);
      $ret = Array();
      while (($row = mysql_fetch_assoc($res)))  {
         $row['message'] = stripslashes($row['message']);
         $t = new Tag($row);
         $t->drinker_obj = loadDrinker($t->user_id);
         $ret[] = $t;
      }
      return $ret;
   }
   // single-user stats
   function getDrinkerStats($uid) {

      $drinks = getUserDrinks($uid);
      $ret = Array();
      $ret['alltime_num'] = sizeof($drinks);
      $totalvol = 0;
      $totalcals = 0;
      $highest_bac = 0;
      $highest_bac_id = False;

      foreach ($drinks as $drink) {
         $totalvol += $drink->inOunces();
         $totalcals += $drink->getCalories();
         if ($drink->bac > $highest_bac) {
            $highest_bac = $drink->bac;
            $highest_bac_id = $drink->id;
         }
      }
      $ret['alltime_vol'] = $totalvol;
      $ret['alltime_bac'] = $highest_bac;
      $ret['alltime_bac_id'] = $highest_bac_id;
      $ret['alltime_cals'] = $totalcals;

      return $ret;
   }
   // leader-related functions
   function ssort($a, $b)
   {
      return strcmp($a->totalOunces(), $b->totalOunces());
   }
   function getLeadersByBinge($all_kegs = true, $num = 5)
   {
      echo "here!\n";
      $drinkers = getAllDrinkers();
      $binges = array();
      foreach ($drinkers as $drinker) {
         $sss = getSessions($drinker->id);
         uksort($sss, "ssort");
         $binges[] = $sss[0];
      }
      return $binges;
   }
   function getLeadersByBAC($all_kegs = true, $num = 5)
   {
      if ($all_kegs) {
         $q = "SELECT id,user_id,MAX(bac) as bac FROM bacs GROUP BY user_id ORDER BY bac DESC LIMIT $num";
      }
      else {
         $keg = loadCurrentKeg();
         // XXX FIXME
         //$q = "SELECT id,user_id,MAX(bac) FROM bacs WHERE keg_id='{$keg->id}' AND id > 80 GROUP BY bac ORDER BY bac DESC LIMIT $num";
      }
      $res = mysql_query($q);
      $ret = Array();
      while (($row = mysql_fetch_assoc($res)))  {
         $row['drinker'] = loadDrinker($row['user_id']);
         $row['amount'] = round($row['bac'],4);
         $ret[] = $row;
      }
      return $ret;
   }
   function getLeadersByCount($all_kegs = true, $num = 5)
   {
      if ($all_kegs) {
         $q = "SELECT user_id,COUNT(*) AS num FROM drinks GROUP BY user_id ORDER BY num DESC LIMIT $num";
      }
      else {
         $keg = loadCurrentKeg();
         $q = "SELECT user_id,COUNT(*) AS num FROM drinks WHERE keg_id='{$keg->id}' GROUP BY user_id ORDER BY num DESC LIMIT $num";
      }
      $res = mysql_query($q);
      $ret = Array();
      while (($row = mysql_fetch_assoc($res)))  {
         $row['drinker'] = loadDrinker($row['user_id']);
         $row['amount'] = $row['num'];
         $ret[] = $row;
      }
      return $ret;
   }
   function getLeadersByVolume($all_kegs = true, $num = 5, $kegid = NULL)
   {
      if ($all_kegs) {
         $q = "SELECT user_id,SUM(`volume`) AS `total_volume` FROM `drinks`,`kegs` WHERE drinks.keg_id = kegs.id AND drinks.status='valid' GROUP BY `user_id` ORDER BY `total_volume` DESC LIMIT $num";
      }
      else {
         if ($kegid == NULL) {
            $keg = loadCurrentKeg();
         }
         else {
            $keg = loadKeg($kegid);
         }
         $q = "SELECT user_id,SUM(`volume`) AS `total_volume` FROM `drinks`,`kegs` WHERE drinks.keg_id='{$keg->id}' AND drinks.keg_id = kegs.id AND drinks.status='valid' GROUP BY `user_id` ORDER BY `total_volume` DESC LIMIT $num";
      }
      $res = mysql_query($q);
      $ret = Array();
      while (($row = mysql_fetch_assoc($res)))  {
         //print_r($row);
         $row['drinker'] = loadDrinker($row['user_id']);
         $row['amount'] = round(volunits_to_ounces($row['total_volume']) ,2); // FIXME CONSTANT
         $row['units'] = " ounces";
         $ret[$row['user_id']] = $row;
      }
      return $ret;
   }

   function volunits_to_ounces($amt) {
      return $amt * 0.0338140226;
   }

   function newPolicy($type,$unitcost,$unitounces,$descr) {
      $descr = addslashes($descr);
      $q = "INSERT INTO `policies` (`type`,`unitcost`,`unitounces`,`description`) VALUES ('$type','$unitcost','$unitounces','$descr')";
      mysql_query($q);
   }

   function deleteGrant($id) {
      $q = "UPDATE `grants` SET `status`='deleted' WHERE `id`='$id' LIMIT 1";
      mysql_query($q);
   }

   function grantPolicy($pid,$did,$exp,$eoz,$edate) {
      if ($exp == 'ounces') {
         $etime= 0;
      }
      if ($exp == 'time') {
         $eoz = 0;
         $etime = strtotime($edate);
      }
      $q = "INSERT INTO `grants` (`foruid`,`expiration`,`forpolicy`,`exp_ounces`,`exp_time`) VALUES ('$did','$exp','$pid','$eoz','$etime')";
      mysql_query($q);

   }

   function updateUser($uid,$vars) {
      $fields = Array('username','weight','gender');

      foreach ($fields as $field) {
         $q = "UPDATE `users` SET `{$field}`='{$vars[$field]}' WHERE `id`='$uid' LIMIT 1";
         mysql_query($q);
      }
      $_SESSION['drinker'] = loadDrinker($uid);
   }
   function validateUser($username,$passwd) {
      $q = "SELECT `id` FROM `users` WHERE `username`='$username' AND `password` = MD5('$passwd')";
      $res = mysql_query($q);
      if (mysql_num_rows($res) == 0) {
         return False;
      }
      else {
         $row = mysql_fetch_assoc($res);
         $uid = $row['id'];
         return loadDrinker($uid);
      }
   }
   // return the amont of beer left, as a percentage of the starting ounces
   // known to be in the keg
   function getKegContents($kegobj)
   {
      // TODO/XXX - make SQL do this math!
      $q = "SELECT `totalticks` FROM `drinks` WHERE `status`='valid' AND keg_id='{$kegobj->id}' AND `frag`='0'";
      $res = mysql_query($q);
      $total = 0; 
      while ($row = mysql_fetch_array($res)) {
         $total += $row[0];
      }

      // we now have the total ticks poured for this keg in $total, so compute
      // it as a percentage of the keg's original capacity
      $origticks = $kegobj->ticksWhenFull();
      $pct_left = ($origticks - $total)/$origticks;
      return $pct_left;
   }
   function getDrink($id)
   {
      global $cfg; 
      $q = "SELECT * FROM `drinks` WHERE `id` = '$id'";
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      $newdrink = fillDrink($row);
      return $newdrink;
   }
   function getAllPolicies()
   {
      $q = "SELECT * FROM `policies` ORDER BY `type`,`unitcost`*`unitounces` DESC";
      $res = mysql_query($q);
      $ps = Array();
      while ($row = mysql_fetch_assoc($res)) {
         $p = new Policy($row);
         $ps[] = $p;
      }
      return $ps;
   }
   function getPolicy($id) {
      $q = "SELECT * FROM `policies` WHERE `id` = $id";
      $res = mysql_query($q);
      $row = @mysql_fetch_assoc($res); # XXX
      $p = new Policy($row);
      return $p;
   }
   function loadGrant($gid)
   {
      $q = "SELECT * FROM `grants` WHERE `id` = $gid LIMIT 1";
      echo $q;
      $res = mysql_query($q);
      $grants = Array();
      return new Grant(mysql_fetch_assoc($res));
   }
   function getUserGrants($userid)
   {
      $q = "SELECT * FROM `grants` WHERE `user_id` = $userid AND `status`!='deleted'";
      $res = mysql_query($q);
      $grants = Array();
      while ($row = mysql_fetch_assoc($res)) {
         $newgrant = new Grant($row);
         $grants[] = $newgrant;
      }
      return $grants;
   }
   function getUserDrinks($userid, $order = "DESC", $show_invalid = False)
   {
      global $cfg; 
      if (!$show_invalid) {
         $q = "SELECT * FROM `drinks` WHERE `status`='valid' AND `ticks` > " . $cfg['flow']['minticks'] . " AND `user_id` = '$userid' ORDER BY `id` $order";
      }
      else {
         $q = "SELECT * FROM `drinks` WHERE `ticks` > " . $cfg['flow']['minticks'] . " AND `user_id` = '$userid' ORDER BY `id` $order";
      }
      $res = mysql_query($q);
      $drinks = Array();
      while ($row = mysql_fetch_assoc($res)) {
         $newdrink = fillDrink($row);
         $drinks[] = $newdrink;
      }
      return $drinks;
   }
   function getAllTokens()
   {
      global $cfg;
      $q = "SELECT * FROM `tokens` ORDER BY `created` ASC";
      $res = mysql_query($q);
      $tokens= Array();
      while ($row = mysql_fetch_assoc($res)) {
         $newtok = fillToken($row);
         $tokens[] = $newtok;
      }
      return $tokens;
   }
   function getToken($id)
   {
      global $cfg;
      $q = "SELECT * FROM `tokens` WHERE `id`='$id' LIMIT 1";
      $res = mysql_query($q);
      return fillToken(mysql_fetch_assoc($res));
   }
   function getAllDrinkers()
   {
      global $cfg;
      $q = "SELECT * FROM `users` ORDER BY `id`";
      $res = mysql_query($q);
      $drinkers = Array();
      while ($row = mysql_fetch_assoc($res)) {
         $newdrinker = fillDrinker($row);
         $drinkers[$newdrinker->id] = $newdrinker;        
      }
      return $drinkers;
   }
   function ozsort($a,$b)
   {
      $va = $a->stats['alltime_vol'];
      $vb = $b->stats['alltime_vol'];
      if($va == $vb) {
         return 0;
      }
      return ($va > $vb) ? -1 : 1;
   }
   function getDrinksByQuery($q)
   {
      global $cfg; 
      $res = mysql_query($q);
      $drinks = Array();
      while ($row = mysql_fetch_assoc($res)) {
         if(empty($row)) 
            return NULL;
         $newdrink = fillDrink($row);
         $drinks[] = $newdrink;
      }
      return $drinks;
   }
   function getAllDrinks($kegid = 0,$did = 999999) // XXX clezan this  up
   {
      global $cfg; 
      $q = "SELECT * FROM `drinks` WHERE `id` <= '$did' AND `totalticks` > " . $cfg['flow']['minticks'] . " AND `frag` = '0' ORDER BY `id` ASC";
      if ($kegid != 0) {
         $q = "SELECT * FROM `drinks` WHERE `id` <= '$did' AND `totalticks` > " . $cfg['flow']['minticks'] . " AND `keg_id` = '$kegid' AND `frag` = '0' ORDER BY `endtime` DESC";
      }
      $res = mysql_query($q);
      $drinks = Array();
      while ($row = mysql_fetch_assoc($res)) {
         if(empty($row)) 
            return NULL;
         $newdrink = fillDrink($row);
         $drinks[] = $newdrink;
      }
      return $drinks;
   }
   function getDrinksSince($time,$userid)
   {
      global $cfg;
      $q = "SELECT * FROM `drinks` WHERE `endtime` > '$time' AND `user_id` = '$userid' AND `frag` = '0' AND `totalticks` > '" . $cfg['flow']['minticks'] . "' ORDER BY `endtime`";
      $res = mysql_query($q);
      $drinks = Array();
      while ($row = mysql_fetch_assoc($res)){
         $newdrink = fillDrink($row);
         $drinks[] = $newdrink;
      }
      return $drinks;
   }
   function getLastDrinks($num)
   {
      global $cfg; 
      $q = "SELECT * FROM `drinks` WHERE `totalticks` > " . $cfg['flow']['minticks'] . " AND `frag`='0' ORDER BY `id` DESC LIMIT $num";
      $res = mysql_query($q);
      $drinks = Array();
      while ($row = mysql_fetch_assoc($res)) {
         $newdrink = fillDrink($row);
         $drinks[] = $newdrink;
      }
      return $drinks;
   }
   function loadCurrentKeg(){
      $q = "SELECT `*` FROM `kegs` ORDER BY `id` DESC LIMIT 1";
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);

      if(empty($row))
         return NULL;
      return fillKeg($row);
   }
   function loadKeg($kegid) {
      global $KEGS;

      if (true or ! isset($KEGS[$kegid])) {
         $q = "SELECT * FROM `kegs` WHERE id='$kegid' LIMIT 1";
         $res = mysql_query($q);
         $row = mysql_fetch_assoc($res);
         return fillKeg($row);
      }
      return $KEGS[$kegid];
   }
   function loadDrinker($uid) {
      global $DRINKERS;

      if (is_numeric($uid)) {
         $q = "SELECT * FROM `users` WHERE id='$uid' LIMIT 1";
      }
      else {
         $uid = mysql_escape_string($uid);
         $q = "SELECT * FROM `users` WHERE username='$uid' LIMIT 1";
      }
      if (true or ! isset($DRINKERS[$uid])) {
         $res = mysql_query($q);
         $row = mysql_fetch_assoc($res);
         return fillDrinker($row);
      }
      return $DRINKERS[$uid];
   }
   function getUserName($uid) {
      $q = "SELECT `username` FROM `users` WHERE id='$uid' LIMIT 1";
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      if(empty($row))
         return NULL;
      return $row['username'];
   }
   function getLogData($last = 40) {
      global $cfg;
      $q = "SELECT `msg` from `logging` ORDER BY `logtime` DESC LIMIT $last";
      $res = mysql_query($q);
      $rows = Array();
      while (($row = mysql_fetch_assoc($res))) {
         $rows[] = $row['msg'];
      }
      return array_reverse($rows);
   }
   function genCumData($gname, $keg = 0,$upto = 0) {
      global $cfg;
      $alldrinks = getDrinkIds();
      $drinkers = getAllDrinkers();
      $q = "SELECT * FROM `drinks` WHERE `totalticks` > " . $cfg['flow']['minticks'] . " AND `frag` = '0' AND `status`='valid' ORDER BY `id` ASC";
      if ($keg) {
         $q = "SELECT * FROM `drinks` WHERE `keg_id`='$keg' AND `totalticks` > " . $cfg['flow']['minticks'] . " AND `frag` = '0' AND `status`='valid' ORDER BY `id` ASC";
      }
      $drinks = getDrinksByQuery($q);

      $total = array();
      $f = fopen("{$cfg['graph']['datadir']}/$gname.dat",'w');
      $fields = "did\t";
      foreach ($drinkers as $d) {
         $fields .= str_replace(" ","_",$d->username) . "\t";
      }
      #fwrite($f,"$q\n");
      fwrite($f,"#set fields = $fields\n");

      foreach ($drinkers as $d) {
         $total[$d->id] = 0.0;
      }
      foreach ($drinks as $d) {
         $total[$d->user_id] += round($d->inOunces(),2);
         fwrite($f,$d->id . "\t");
         foreach ($drinkers as $d) {
            fwrite($f,$total[$d->id] . "\t");
         }
         fwrite($f,"\n");
      }
   }
   function getSnapshot($did,$drinkers) {
      #$q = "select user_id,SUM(totalticks/kegs.tickmetric) as oz from drinks,kegs where frag=0 AND drinks.keg_id = kegs.id AND drinks.status='valid' AND drinks.id <=$did GROUP BY user_id ORDER BY oz DESC";
      $ret = array();
      $drinks = getAllDrinks(0,$did);
      return $ret;
   }
   function getDrinkIds() {
      $q = "SELECT id FROM drinks WHERE status='valid' and frag='0' order by id ASC";
      $res = mysql_query($q);
      $ret = array();
      while (($row = mysql_fetch_array($res)) != NULL ) {
         $ret[] = $row[0];
      }
      return $ret;
   }
   function genGraphData($graph, $last = 86400) {
      if (!strcmp($graph,"historical")) {
         return genCumData("historical",$keg = 0, $last);
       }
      elseif (!strcmp($graph,"keghist")) {
         $k = loadCurrentKeg();
         return genCumData("keghist",$keg = $k->id, $last);
       }
      global $cfg;
      $last = 60*60*3;
      $mintime = $GLOBALS['dbtime'] - $last;
      $mintime -= $mintime % (60*60); // back up to the hour boundary
      $q = "SELECT `temp`,`rectime`,`fridgestatus` FROM `thermolog` WHERE `rectime`>'$mintime' ORDER BY `rectime` ASC";
      $res = mysql_query($q);
      $rows = Array();
      while (($row = mysql_fetch_assoc($res))) {
         $rows[] = $row;
      }
      $f = fopen("{$cfg['graph']['datadir']}/current-temps.dat",'w');
      fwrite($f,"datetime\ttemp\tsteps\n");
      foreach ($rows as $row) {
         $time = strftime("%H:%M:%S",$row['rectime']);
         $time = strftime("%m/%d/%Y.%H:%M",$row['rectime']);
         $temp = (9.0/5.0)*$row['temp'] + 32.0;
         $line = "$time\t{$temp}\t{$row['fridgestatus']}\n";
         fwrite($f,$line);
      }
   }
   function getCurrentKegTemp() {
      $q = "SELECT `temp`,`rectime` FROM `thermolog` WHERE `sensor`='1' ORDER BY `rectime` DESC LIMIT 1";
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      return $row;
   }
   function mkDays($secs) {
      // return (years,days,hours,minutes,seconds) for a given number of seconds
      $ret = Array("years"=>0,"days"=>0,"hours"=>0,"minutes"=>0,"seconds"=>0);
      if ($secs <= 0) 
         return $ret;

      while ($secs >= 60*60*24*365) {
         $ret["years"] += 1;
         $secs -= 60*60*24*365;
      }
      while ($secs >= 60*60*24) {
         $ret["days"] += 1;
         $secs -= 60*60*24;
      }
      while ($secs >= 60*60) {
         $ret["hours"] += 1;
         $secs -= 60*60;
      }
      while ($secs >= 60) {
         $ret["minutes"] += 1;
         $secs -= 60;
      }

      return $ret;
   }
   function getCurrentDrunks() {
      $q = "SELECT `id` FROM `users`";
      $res = mysql_query($q);
      $drunks = Array();
      while ($row = mysql_fetch_assoc($res)) {
         $bac = getCurrentBAC($row['id']);
         if ($bac > 0.0) {
            $drinker = loadDrinker($row['id']);
            $drinker->setCurrentBAC($bac);
            $drunks[] = $drinker;
         }
      }
      if (sizeof($drunks) > 0) {
         return $drunks;
      }
      else {
         return NULL;
      }
   }

   function getCurrentBAC($user_id) {
      $q = "SELECT `bac`,`rectime`,UNIX_TIMESTAMP(NOW()) as `CURRTIME` FROM `bacs` WHERE `user_id`='$user_id' ORDER BY `rectime` DESC LIMIT 1";
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      if (empty($row)) {
         return 0.0;
      }
      else {
         return decomposeBAC($row['bac'],$row['CURRTIME'] - $row['rectime']);
      }
   }

   function decomposeBAC($bac,$time_diff) {
      $rate = 0.016;
      return max(0.0, $bac - ($rate * ($time_diff/3600.0)));
   }

   function getDrinkSize($orgticks, $kegid) {
      return $orgticks; // XXX TODO
   }
  function fillDrink($row){
      if($row == NULL)
         return NULL;
      $drink = new Drink($row);
      $drink->setUserName(getUserName($row['user_id']));
      $drink->setDrinkSize(getDrinkSize($row['totalticks'],$row['keg_id']));
      $drink->setKeg(loadKeg($row['keg_id']));
      $drink->setDrinker(loadDrinker($row['user_id']));
      $DRINKS[$row['id']] = $drink;
      return $drink;
   }
   function fillToken($row){
      if($row == NULL)
         return NULL;
      $token = new Token($row);
      $token->setOwner(loadDrinker($row['ownerid']));
      $TOKENS[$row['id']] = $token;
      return $token;
   }
   function fillDrinker($row){
      if($row == NULL)
         return NULL;
      $drinker = new Drinker($row);
      $DRINKERS[$row['id']] = $drinker;
      return $drinker;
   }
   function getAllKegs() {
      $q = "SELECT * FROM `kegs` ORDER BY `id` ASC";
      $res = mysql_query($q);
      $ret = array();
      while (($row = mysql_fetch_assoc($res)) != NULL) {
         $ret[] = new Keg($row);
      }
      return $ret;
   }
   function fillKeg($row){
      if($row == NULL)
         return NULL;
      $keg = new Keg($row);
      $KEGS[$row['kegid']] = $keg;
      return $keg;
   }
?>
