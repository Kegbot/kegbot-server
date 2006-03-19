<?
   require_once("load-config.php");
   require_once("allclasses.php");
   include_once('binge-functions.php');
   include_once('units.php');
   global $cfg;

   @mysql_connect($cfg['db']['host'], $cfg['db']['user'], $cfg['db']['password']) || die("the kegbot front end can't connect to the backend. check db config in cfg.inc.php");
   mysql_select_db($cfg['db']['db']) || die("the kegbot front end can't find this database ({$cfg['db']['db']}). uh oh.");
   $r = mysql_query("SELECT UNIX_TIMESTAMP(NOW())");
   $DBTIME = mysql_fetch_array($r);
   $GLOBALS['dbtime'] = $DBTIME[0];

   $TOKENS = Array();

   /**
   *
   * A simple, SELECT-only MySQL query generator.
   *
   * At the moment, this function does not handle nearly all possible select
   * constructs, invalid data, or malicious inputs. It is mostly a convenience
   * function for very common internal use.
   *
   * @return	string	 query
   */
   function SQLQuery($table, $select = NULL, $where = NULL, $limit = NULL,
                     $order_by = NULL, $order_dir = "DESC")
   {
      $q = "SELECT ";
      if ($select == NULL) {
         $q .= "* ";
      } else {
         echo "select == $select";
         $q .= implode(",", $select) . " ";
      }

      $q .= "FROM $table ";
      if ($where != NULL) {
         $q .= "WHERE ";
         $q .= implode(" AND ", $where) . " ";
      }

      if ($order_by != NULL) {
         $q .= "ORDER BY `$order_by` $order_dir ";
      }

      if ($limit != NULL) {
         $q .= "LIMIT $limit ";
      }

      return $q;
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

   function getLeadersByBAC($all_kegs = true, $num = 5, $kegid = NULL)
   {
      if ($all_kegs) {
         $q = "SELECT id,user_id,MAX(bac) as bac FROM bacs GROUP BY user_id ORDER BY bac DESC LIMIT $num";
      }
      else {
         $keg = new Keg($kegid);
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

   function getLeadersByVolume($num, $keg)
   {
      if (!$keg) {
         $q = "SELECT user_id,SUM(`volume`) AS `total_volume` FROM `drinks`,`kegs` WHERE drinks.keg_id = kegs.id AND drinks.status='valid' GROUP BY `user_id` ORDER BY `total_volume` DESC LIMIT $num";
      }
      else {
         $q = "SELECT user_id,SUM(`volume`) AS `total_volume` FROM `drinks`,`kegs` WHERE drinks.keg_id='{$keg->id}' AND drinks.keg_id = kegs.id AND drinks.status='valid' GROUP BY `user_id` ORDER BY `total_volume` DESC LIMIT $num";
      }
      $res = mysql_query($q);
      $ret = Array();
      while (($row = mysql_fetch_assoc($res)))  {
         $row['drinker'] = loadDrinker($row['user_id']);
         $row['amount'] = round(volunits_to_ounces($row['total_volume']) ,2); // FIXME CONSTANT
         $row['units'] = " ounces";
         $ret[$row['user_id']] = $row;
      }
      return $ret;
   }

   function newPolicy($type,$unitcost,$unitounces,$descr) {
      $descr = addslashes($descr);
      $q = "INSERT INTO `policies` (`type`,`unitcost`,`unitounces`,`description`) VALUES ('$type','$unitcost','$unitounces','$descr')";
      mysql_query($q);
   }

   function grantPolicy($pid, $did, $exp, $eoz, $edate) {
      $etime = 0;
      $evol = 0;
      if (!strcmp($exp, "volume")) {
         $evol = ounces_to_volunits($eoz);
      }
      if (!strcmp($exp, "time")) {
         $etime = strtotime($edate);
      }
      $q = "INSERT INTO `grants` (`status`,`user_id`,`expiration`,`policy_id`,`exp_volume`,`exp_time`,`exp_drinks`,`total_volume`,`total_drinks`) VALUES ('active','$did','$exp','$pid','$evol','$etime',0,0,0)";
      mysql_query($q);
   }

   function createToken($did, $keyinfo) {
      $q = "INSERT INTO `tokens` (`user_id`,`keyinfo`,`created`) VALUES ('$did', '$keyinfo', NOW())";
      $res = mysql_query($q);
      if ($res) {
         return mysql_insert_id();
      }
      return NULL;
   }

   function createUser($username, $pass, $gender, $weight, $email) {
      $q = "INSERT INTO `users` (`username`,`email`,`gender`,`password`,`weight`,`im_aim`,`admin`,`image_url`) VALUES ('$username', '$email', '$gender', MD5('$pass'), '$weight','','no','')";
      $res = mysql_query($q);
      if ($res) {
         return mysql_insert_id();
      }
      return NULL;
   }

   function getAllPolicies()
   {
      $q = "SELECT `id` FROM `policies` ORDER BY `type`,`unitcost` DESC";
      $res = mysql_query($q);

      $ps = Array();
      while ($row = mysql_fetch_assoc($res)) {
         $p = new Policy($row['id']);
         $ps[] = $p;
      }
      return $ps;
   }

   function getPolicy($id) {
      return new Policy($id);
   }

   function loadGrant($id)
   {
      return new Grant($id);
   }

   function getUserGrants($userid)
   {
      $q = "SELECT `id` FROM `grants` WHERE `user_id` = $userid AND `status`!='deleted'";
      $res = mysql_query($q);
      $grants = Array();
      while ($row = mysql_fetch_assoc($res)) {
         $newgrant = new Grant($row['id']);
         $grants[] = $newgrant;
      }
      return $grants;
   }

   function getUserDrinks($userid, $order = "DESC")
   {
      global $cfg; 
      $q = "SELECT `id` FROM `drinks` WHERE `status`='valid' AND `user_id` = '$userid' ORDER BY `id` $order";
      $res = mysql_query($q);
      $drinks = Array();
      while ($row = mysql_fetch_assoc($res)) {
         $newdrink = new Drink($row['id']);
         $drinks[] = $newdrink;
      }
      return $drinks;
   }

   function getAllTokens()
   {
      global $cfg;
      $q = "SELECT `id` FROM `tokens` ORDER BY `created` ASC";
      $res = mysql_query($q);
      $tokens= Array();
      while ($row = mysql_fetch_assoc($res)) {
         $newtok = new Token($row['id']);
         $tokens[] = $newtok;
      }
      return $tokens;
   }

   function getToken($id)
   {
      return new Token($id);
   }

   function getAllDrinkers()
   {
      $q = "SELECT `id` FROM `users` ORDER BY `id`";
      $res = mysql_query($q);
      $drinkers = Array();
      while ($row = mysql_fetch_assoc($res)) {
         $newdrinker = new Drinker($row['id']);
         $drinkers[] = $newdrinker;
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

   function getBingeGroups($keg)
   {
      $start = "UNIX_TIMESTAMP('{$keg->startdate}')";
      $end = $keg->enddate;
      if (empty($end)) {
         $end = "NOW()";
      } else {
         $end = "UNIX_TIMESTAMP('$end')";
      }
      $q = "SELECT * FROM `binges` WHERE `starttime`>=$start AND `endtime`<=$end ORDER BY `starttime` ASC";
      $binges = getBingesByQuery($q);
      $groups = array();
      $last = NULL;
      foreach ($binges as $binge) {
         if ($last == NULL or $last->endtime < $binge->starttime) {
            $groups[] = array();
         }
         $groups[sizeof($groups)-1][] = $binge;
         $last = $binge;
      }
      return $groups;
   }
   function getBingesByQuery($q)
   {
      $res = mysql_query($q);
      if (empty($res)) {
         return array();
      }
      $binges = Array();
      while ($row = mysql_fetch_assoc($res)) {
         if(empty($row))
            return NULL;
         $binges[] = new Binge($row['id']);
      }
      return $binges;
   }

   function getDrinkersByQuery($q)
   {
      $res = mysql_query($q);
      $drinkers = Array();
      while ($row = mysql_fetch_assoc($res)) {
         if(empty($row))
            return NULL;
         $drinkers[] = new Drinker($row['id']);
      }
      return $drinkers;
   }


   function getDrinksByQuery($q)
   {
      $res = mysql_query($q);
      $drinks = Array();
      while ($row = mysql_fetch_assoc($res)) {
         if(empty($row))
            return NULL;
         $newdrink = new Drink($row['id']);
         $drinks[] = $newdrink;
      }
      return $drinks;
   }

   function loadDrinker($id) {
      if (is_numeric($id)) {
         return new Drinker($id);
      } else {
         $q = "SELECT `id` FROM `users` WHERE username='$id' LIMIT 1";
         $res = mysql_query($q);
         $row = mysql_fetch_assoc($res); // TODO CHECK INPUT
         return new Drinker($row['id']);
      }
   }

   function getCurrentKeg() {
      $q = "SELECT `id` FROM `kegs` ORDER BY `id` DESC LIMIT 1";
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      return new Keg($row['id']);
   }

   function getCurrentKegTemp() {
      $q = "SELECT `temp`,`rectime` FROM `thermolog` WHERE `sensor`='1' ORDER BY `rectime` DESC LIMIT 1";
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      return $row;
   }

   function getCurrentDrunks() {
      $q = "SELECT `id` FROM `users`";
      $res = mysql_query($q);
      $drunks = Array();
      while ($row = mysql_fetch_assoc($res)) {
         $bac = getCurrentBAC($row['id']);
         if ($bac > 0.0) {
            $drinker = loadDrinker($row['id']);
            $drinker->current_bac = $bac; // XXX FIXME
            $drunks[] = $drinker;
         }
      }
      return $drunks;
   }

   function getBAC($user_id, $drink_id) {
      $q = "SELECT `bac` FROM `bacs` WHERE `user_id`='$user_id' AND `drink_id`='$drink_id' LIMIT 1";
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      if (empty($row)) {
         return 0.0;
      }
      else {
         return $row['bac'];
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

   function getAllKegs() {
      $q = "SELECT `id` FROM `kegs` ORDER BY `id` ASC";
      $res = mysql_query($q);
      $ret = array();
      while (($row = mysql_fetch_assoc($res)) != NULL) {
         $ret[] = new Keg($row['id']);
      }
      return $ret;
   }

?>
