<?
   include_once('includes/load-config.php');
   include_once('includes/SmartyBeer.class.php');

   $smarty = new SmartyBeer();
   $file = pathinfo($_GET['css']);
   $file = $file['basename'];
   $cid = $file;

   //$smarty->fetch("css.tpl",$cid);
   $f = $smarty->basedir . '/css/' . $file;
   if (file_exists($f)) {
      echo implode('', file($f));
   }

?>
