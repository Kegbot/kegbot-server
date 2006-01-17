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

   function getLeadersByVolume($all_kegs = true, $num = 5, $kegid = NULL)
   {
      if ($all_kegs) {
         $q = "SELECT user_id,SUM(`volume`) AS `total_volume` FROM `drinks`,`kegs` WHERE drinks.keg_id = kegs.id AND drinks.status='valid' GROUP BY `user_id` ORDER BY `total_volume` DESC LIMIT $num";
      }
      else {
         $keg = new Keg($kegid);
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

   function volunits_to_ounces($amt) {
      return $amt * 0.0338140226;
   }

   function ounces_to_volunits($amt) {
      return $amt * 29.5735297;
   }

   function newPolicy($type,$unitcost,$unitounces,$descr) {
      $descr = addslashes($descr);
      $q = "INSERT INTO `policies` (`type`,`unitcost`,`unitounces`,`description`) VALUES ('$type','$unitcost','$unitounces','$descr')";
      mysql_query($q);
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
            $drinker->bac = $bac; // XXX FIXME
            $drunks[] = $drinker;
         }
      }
      return $drunks;
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
