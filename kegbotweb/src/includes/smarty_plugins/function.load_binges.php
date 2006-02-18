<?
include_once('main-functions.php');

function smarty_function_load_binges($params, &$smarty)
{
   $q = SQLQuery( $table='binges',
                  $select = NULL,
                  $where = array("`user_id`='{$params['user_id']}'"),
                  $limit = empty($params['limit']) ? NULL : $params['limit'],
                  $order_by = "volume",
                  $order_dir = "DESC");
   $smarty->assign($params['assign'], getBingesByQuery($q));
}
?>
