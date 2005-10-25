<?
// need to include main-functions for the getPolicy call
include_once("main-functions.php");
class Grant {
   var $id;
   var $foruid;
   var $expiration;
   var $status;
   var $policy;
   var $exp_ounces;
   var $exp_time;
   var $exp_drinks;
   var $total_ounces;
   var $total_drinks;

   function Grant($a) {
      $this->id = $a['id'];
      $this->foruid = $a['foruid'];
      $this->expiration = $a['expiration'];
      $this->status = $a['status'];
      $this->policy = getPolicy($a['forpolicy']);
      $this->exp_ounces = $a['exp_ounces'];
      $this->exp_time = $a['exp_time'];
      $this->exp_drinks = $a['exp_drinks'];
      $this->total_ounces = $a['total_ounces'];
      $this->total_drinks = $a['total_drinks'];
   }
   function getExpirationStr() {
      if (!strcmp($this->expiration,"time")) {
         $date = strftime("%D",$this->exp_time);
         return "on $date";
      }
      elseif (!strcmp($this->expiration,"ounces")) {
         return "after {$this->exp_ounces} ounces";
      }
      return "never";
   }
   function getToGo() {
      if (!strcmp($this->expiration,"time")) {
         $dest = $this->exp_time;
         $src  = time();
         $info = mkDays($dest-$src);
         $ret = "";
         if ($info['years'] != 0)
            $ret .= $info['years'] . ' years ';
         if ($info['days'] != 0) {
            $ret .= $info['days'] . ' days ';
            if ($info['days'] > 1) {
               return $ret . "+";
            }
         }
         if ($info['hours'] != 0)
            $ret .= $info['hours'] . ' hours ';
         if ($info['minutes'] != 0)
            $ret .= $info['minutes'] . ' minutes ';
         if ($info['seconds'] != 0)
            $ret .= $info['seconds'] . ' seconds ';
         if (!strcmp($ret,""))
            $ret = "expired!";

         return $ret;
      }
      elseif (!strcmp($this->expiration,"ounces")) {
         $diff = $this->exp_ounces - $this->total_ounces;
         $diff = round($diff,2);
         if ($diff <= 0) 
            return "expired!";
         return "$diff ounces";
      }
      return "--";
   }
}
?>
