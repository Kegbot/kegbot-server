<?
require_once("load-config.php");
function smarty_function_module_url($params, &$smarty)
{
   global $cfg;

   $TR = Array('drink-info' => 'drink',
               'drinker-info' => 'drinker',
               'keg-info' => 'keg');

   // build an argument stream from smarty params
   $args = array();
   $path = '';
   foreach ($params as $key => $val) {
      if (strcmp($key, "module")) {
         $args[] = "$key=$val";
         $path .= "/$val";
      }
   }

   // special cases
   if (!strcmp($params['module'],"main")) {
      return "/index.php";
   } else {
      $out = '/' . $params['module'] . ".php";
   }

   if ($cfg['misc']['fancy_urls'] and $TR[$params['module']]) {
      $out = '/' . $TR[$params['module']] . $path;
      return $out;
   }
   else {
      // append arguments
      if (sizeof($args) > 0) {
         $out .= "?" . implode("&", $args);
      }
   }
   return $out;
}
?>
