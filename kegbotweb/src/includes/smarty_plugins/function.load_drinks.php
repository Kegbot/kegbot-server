<?
include_once('main-functions.php');
function smarty_function_load_drinks($params, &$smarty)
{
   // TODO: better way to support this?
   if (!empty($params['user_id'])) {
      $params['where'] = array("`user_id`='{$params['user_id']}'");
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
