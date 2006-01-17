<?
   include_once('includes/load-config.php');
   include_once('includes/SmartyBeer.class.php');

   $tplpage = "leaders.tpl";
   $smarty = new SmartyBeer();

   $disp = 5; //number of rankings to show
   if ($_GET['num']) {
      $disp = $_GET['num'];
   }
   $cid = $disp;
   $select_range = array(  5 => '5',
                           6 => '6',
                           7 => '7',
                           8 => '8',
                           9 => '9',
                           10 => '10',
                           15 => '15',
                           25 => '25',
                           500 => 'all' );

   $smarty->assign('select_range', $select_range);
   $smarty->assign('max_leaders', $disp);
   $smarty->show_page($tplpage,$cid);
?>
