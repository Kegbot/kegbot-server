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
   $tail = '';
   foreach ($params as $key => $val) {
      if (strcmp($key, "module")) {
         $args[] = "$key=$val";
         $path .= "/$val";
      }
   }
   if (sizeof($args) > 0) {
      $tail = "?" . implode("&", $args);
   }

   // special cases
   if (!strcmp($params['module'],"main")) {
      return $cfg['urls']['baseurl'] . "/";
   }

   // build the url
   if ($cfg['misc']['fancy_urls'] and $TR[$params['module']]) {
      $out = $TR[$params['module']];
      $out .= $path;
   }
   else {
      $out = $params['module'] . ".php";
      $out .= $tail;
   }
   return $cfg['urls']['baseurl'] . '/' . $out;
}
?>
