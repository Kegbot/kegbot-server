<?
include_once('main-functions.php');
function smarty_function_load_leaders_by_bac($params, &$smarty)
{
   $leaders = getLeadersByBAC($num = $params['limit']);
   $smarty->assign($params['assign'], $leaders);
}
?>
