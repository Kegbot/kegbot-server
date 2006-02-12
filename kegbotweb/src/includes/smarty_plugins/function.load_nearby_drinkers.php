<?
include_once('main-functions.php');

function smarty_function_load_nearby_drinkers($params, &$smarty)
{
   $drink = $params['drink'];
   $lowtime = $drink->starttime - (60*60);
   $hightime = $drink->starttime + (60*60);
   $q = "SELECT `user_id` as 'id',SUM(`volume`) FROM drinks WHERE `user_id`!={$drink->user_id} AND (`starttime` >= $lowtime AND `starttime` <= $hightime) GROUP BY `id`";
   $smarty->assign($params['assign'], getDrinkersByQuery($q));
}
?>
