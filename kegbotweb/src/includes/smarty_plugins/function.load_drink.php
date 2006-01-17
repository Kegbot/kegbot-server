<?
include_once('main-functions.php');
function smarty_function_load_drink($params, &$smarty)
{
   $smarty->assign($params['assign'], new Drink($params['id']));
}
?>
