<?
include_once('main-functions.php');
function smarty_function_load_leaders_by_volume($params, &$smarty)
{
   $leaders = getLeadersByVolume($num = $params['limit']);
   $smarty->assign($params['assign'], $leaders);
}
?>
