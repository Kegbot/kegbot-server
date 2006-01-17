<?
include_once('main-functions.php');
function smarty_function_load_drinker_stats($params, &$smarty)
{
   $drinkers = getAllDrinkers();
   $stats = array();
   foreach ($drinkers as $d) {
      $stats{$d->id} = getDrinkerStats($d->id);
   }
   $smarty->assign($params['assign'], $stats);
}
?>

