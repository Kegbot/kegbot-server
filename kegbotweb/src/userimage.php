<?
   include_once('includes/load-config.php');
   include_once('includes/main-functions.php');

   $drinker = loadDrinker($_GET['id']);
   $q =  "SELECT `filetype`,`data` FROM `userpics` WHERE `user_id`='{$drinker->id}'";
   $res = mysql_query($q);
   if ($res == NULL) {
      Header("Location: images.php?image=unknown-drinker.png");
      return;
   }
   $row = mysql_fetch_assoc($res);
   if (empty($row)) {
      Header("Location: images.php?image=unknown-drinker.png");
      return;
   }
   /* TODO: use a mtime stored in the DB */
   Header("Expires: " . date("D, j M Y H:i:s", time() + (86400 * 30)) . " UTC");
   Header("Cache-Control: Public");
   Header("Pragma: Public");

   Header("Content-type: image/{$row['filetype']}");
   echo $row['data'];

?>
