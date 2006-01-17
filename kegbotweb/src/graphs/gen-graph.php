<?
   include('../includes/load-config.php');
   include('../includes/main-functions.php');
   include('../includes/SmartyBeer.class.php');


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


   $refresh = True;
   $last = 86400;

   if ($HTTP_GET_VARS['g']) {
      $g = $HTTP_GET_VARS['g'];
      if (!strcmp($HTTP_GET_VARS['r'],0)) {
         $refresh = False;
      }
      if ($HTTP_GET_VARS['d']) { // d= number of days
         $last = $HTTP_GET_VARS['d'] * 24*60*60;
      }
   }
   $f = $cfg['graph']['imgdir'] . "/$g.png";

   $smarty = new SmartyBeer();
   $smarty->caching = 1;
   $smarty->cache_lifetime = 600;

   // here, we use smarty's caching mechanism. graph-display.tpl is just an
   // empty template; we never call smarty to display it. we just want to use
   // smarty's cool key-based caching and internal caching timer to control
   // when we call buildGraph

   $tpl = '../templates/graph-display.tpl';
   if (!$smarty->is_cached($tpl,"$g.$d")) {
      $f = buildGraph($g,$refresh,$last);
   }

   // fetch the empty template, but don't display it. this caches the template
   // so later calls to is_cached() return true
   $smarty->fetch($tpl,"$g.$d");

   // display the image. not uing smarty for anything here.
   displayGraph($f);

   function buildGraph($g,$r,$l) {
      global $cfg;
      $g_script = $cfg['graph']['scriptdir'] . "/$g.ploticus";
      $g_data = $cfg['graph']['datadir'];
      $g_image = $cfg['graph']['imgdir'] . "/$g.png";
      $g_url = $cfg['graph']['imgurl'] . "/$g.png";
      $g_cmd = $cfg['graph']['cmd'];

      // generate the datafile
      genGraphData($g,$l);

      // build the command
      $orig = getcwd();
      chdir($g_data);
      $cmd = "$g_cmd -png -o $g_image $g_script";
      system($cmd);
      chdir($orig);
      return $g_image;
   }
   function displayGraph($f) {
      $i = imagecreatefrompng($f);
      Header("Content-type: image/png");
      imagepng($i);
   }

?>
