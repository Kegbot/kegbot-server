<?
   $nav_section = 'main';
   $nav_page = 'calculator';

   include('includes/main-functions.php');
   include('includes/SmartyBeer.class.php');

   // handle calculations
   $action = $HTTP_GET_VARS['action'];

   $smarty = new SmartyBeer();

   // display the top
   $templates = "/var/www/localhost/smarty/beerskin/templates";
   $smarty->display("$templates/top.tpl");
   $smarty->display("$templates/bac-calc.tpl");
   $smarty->display("$templates/bottom.tpl");
?>
