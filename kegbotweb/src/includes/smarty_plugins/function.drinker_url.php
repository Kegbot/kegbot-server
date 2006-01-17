<?
function smarty_function_drinker_url($params, &$smarty)
{
   // XX TODO check input
   $out = "drinker-info.php?drinker=" . $params['name'];
   return $out;
}
?>
