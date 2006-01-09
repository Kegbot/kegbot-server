<?
   include_once('includes/load-config.php');
   include_once('includes/SmartyBeer.class.php');

   $smarty = new SmartyBeer();
   $file = pathinfo($_GET['image']);
   $file = $file['basename'];
   $cid = $file;

   $f = $smarty->basedir . '/images/' . $file;
   if (file_exists($f)) {
      echo implode('', file($f));
   }

?>
