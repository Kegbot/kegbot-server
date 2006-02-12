<?
include_once('main-functions.php');

function smarty_function_load_binges($params, &$smarty)
{
   $q = SQLQuery( $table='binges',
                  $select = NULL,
                  $where = array("`user_id`='{$params['user_id']}' AND `enddrink_id` > `startdrink_id`+1 AND `volume` >= " . ounces_to_volunits(64)),
                  $limit = empty($params['limit']) ? NULL : $params['limit'],
                  $order_by = "volume",
                  $order_dir = "DESC");
   $smarty->assign($params['assign'], getBingesByQuery($q));
}
?>
