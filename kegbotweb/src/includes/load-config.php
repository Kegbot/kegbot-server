<?
   $domaininfo = explode(".", $_SERVER['HTTP_HOST']);
   if (!strcmp("www",$domaininfo[0])) {
      $domaininfo = array_slice($domaininfo, 1);
   }
   $cfgf = '/data/kegbot/htdocs/includes/' . $domaininfo[0] . '.cfg.inc.php';
   if (!file_exists($cfgf)) {
      $cfgf = '/data/kegbot/htdocs/includes/cfg.inc.php';
   }
   include($cfgf);
   global $cfg;
?>
