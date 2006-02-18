<?
require_once("load-config.php");
function smarty_function_module_url($params, &$smarty)
{
   global $cfg;

   // build an argument stream from smarty params
   $args = array();
   foreach ($params as $key => $val) {
      if (strcmp($key, "module")) {
         $args[] = "$key=$val";
      }
   }

   // special cases
   if (!strcmp($params['module'],"main")) {
      $out = "index.php";
   } else {
      $out = $params['module'] . ".php";
   }

   // append arguments
   if (sizeof($args) > 0) {
      $out .= "?" . implode("&", $args);
   }
   return $out;
}
?>
