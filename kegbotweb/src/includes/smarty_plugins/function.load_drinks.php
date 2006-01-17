<?
include_once('main-functions.php');
function smarty_function_load_drinks($params, &$smarty)
{
   $q = "SELECT * FROM `drinks` ";
   if (!empty($params['keg'])) {
      $q .= " WHERE keg_id=" . $params['keg']; // TODO ERROR CHECK
   }
   $q .= " ORDER BY `id` DESC";
   if (!empty($params['limit'])) {
      $q .= " LIMIT " . $params['limit'];
   }
   $drinks = getDrinksByQuery($q);
   $smarty->assign($params['assign'], $drinks);
}
?>
