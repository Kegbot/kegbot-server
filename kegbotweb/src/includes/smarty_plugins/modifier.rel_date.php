<?
function smarty_modifier_rel_date($stamp)
{
   $diff = $GLOBALS['dbtime'] - $stamp;
   if ($diff < 60) { 
      $diff = round($diff);
      $s = ($diff == 1) ? "" : "s";
      return "$diff second$s ago";
   }
   elseif ($diff < 60*60) {
      $mins = round($diff/60);
      $s = ($mins == 1) ? "" : "s";
      return "$mins minute$s ago";
   }
   elseif ($diff < 60*60*24) {
      $hours = round($diff/(60*60));
      $s = ($hours == 1) ? "" : "s";
      return "$hours hour$s ago";
   }
   elseif ($diff < 60*60*24*7) {
      return strftime("%A %H:%M",$stamp);
   }
   else {
      return strftime("%B %e, %Y %H:%M", $stamp);
   }
}
?>
