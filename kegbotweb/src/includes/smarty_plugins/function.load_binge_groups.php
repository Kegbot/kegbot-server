<?
include_once('main-functions.php');

function smarty_function_load_binge_groups($params, &$smarty)
{
   $smarty->assign($params['assign'], getBingeGroups($params['keg']));
}
?>
