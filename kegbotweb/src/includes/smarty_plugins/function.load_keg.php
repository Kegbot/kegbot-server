<?
include_once('main-functions.php');
function smarty_function_load_keg($params, &$smarty)
{
   $smarty->assign($params['assign'], new Keg($params['id']));
}
?>
