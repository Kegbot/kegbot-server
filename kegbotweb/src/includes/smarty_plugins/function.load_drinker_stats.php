<?
include_once('main-functions.php');
function smarty_function_load_drinker_stats($params, &$smarty)
{
   $stats = getDrinkerStats($params['id']);
   $smarty->assign($params['assign'], $stats);
}
?>

