<?
function smarty_modifier_money_fmt($m)
{
   if ($m <= 0) {
      return "no cost";
   }
   else {
      $m = round($m/100.0,2);
      return htmlentities(money_format('%.2n',$m),ENT_QUOTES,'ISO-8859-15');
   }
}
?>
