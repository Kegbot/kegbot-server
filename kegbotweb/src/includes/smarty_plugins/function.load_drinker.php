<?
include_once('main-functions.php');
function smarty_function_load_drinker($params, &$smarty)
{
   $smarty->assign($params['assign'], loadDrinker($params['id']));
}
?>
