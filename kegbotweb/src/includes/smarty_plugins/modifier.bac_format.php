<?
function smarty_modifier_bac_format($bac)
{
   $bacval = max(0.0,floatval($bac) - 0.005);
   $amt = min( ($bacval/0.08) * 255.0,255);
   $color = sprintf("%0x0000 $amt",$amt);
   if ($bacval >= 0.08) {
      $bac = "<b>$bac</b>";
   }
   return "<font color=\"#$color\">$bac</font>";
}
?>
