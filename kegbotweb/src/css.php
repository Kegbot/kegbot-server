<?
   include_once('includes/load-config.php');
   include_once('includes/SmartyBeer.class.php');

   $smarty = new SmartyBeer();
   $file = $_GET['css'];
   $cid = $file;

   //$smarty->fetch("css.tpl",$cid);
   $f = $smarty->basedir . '/css/' . realpath($file);
   echo implode('', file($f));

?>
