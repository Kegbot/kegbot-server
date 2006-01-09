<?
   include('../includes/load-config.php');
   include('../includes/main-functions.php');
   include('../includes/SmartyBeer.class.php');

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
