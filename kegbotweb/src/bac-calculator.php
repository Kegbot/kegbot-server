<?
   $nav_section = 'main';
   $nav_page = 'calculator';

   include('includes/main-functions.php');
   include('includes/SmartyBeer.class.php');

   // handle calculations
   $action = $HTTP_GET_VARS['action'];

   $smarty = new SmartyBeer();

   $smarty->show_page("bac-calculator.tpl");
?>
