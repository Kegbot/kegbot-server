<?
include_once('main-functions.php');
function smarty_function_load_drinkers($params, &$smarty)
{
   $smarty->assign($params['assign'], getAllDrinkers());
}
?>
