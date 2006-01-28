<?
include_once('main-functions.php');
function smarty_function_load_leaders_by_volume($params, &$smarty)
{

   $keg = $params['keg'];
   if (!strcmp($params['keg'], "current")) {
      $keg = getCurrentKeg();
   }
   $leaders = getLeadersByVolume($params['limit'], $keg);
   $smarty->assign($params['assign'], $leaders);
}
?>
