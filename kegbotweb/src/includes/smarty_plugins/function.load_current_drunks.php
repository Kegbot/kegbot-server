<?
include_once('main-functions.php');
function smarty_function_load_current_drunks($params, &$smarty)
{
   $smarty->assign($params['assign'], getCurrentDrunks());
}
?>
