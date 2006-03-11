<?
include_once('main-functions.php');
function smarty_function_load_drinks($params, &$smarty)
{
   $params['where'] = array();
   $params['where'][] = "`status`='valid'";

   // TODO: better way to support this?
   if (!empty($params['user_id'])) {
      $params['where'][] = "`user_id`='{$params['user_id']}'";
   }
   if (!empty($params['keg_id'])) {
      $params['where'][] = "`keg_id`='{$params['keg_id']}'";
   }

   $q = SQLQuery( $table='drinks',
                  $select = NULL,
                  $where = empty($params['where']) ? NULL : $params['where'],
                  $limit = empty($params['limit']) ? NULL : $params['limit'],
                  $order_by = empty($params['order_by']) ? NULL : $params['order_by'],
                  $order_dir = empty($params['order_dir']) ? NULL : $params['order_dir']);
   $smarty->assign($params['assign'], getDrinksByQuery($q));
}
?>
