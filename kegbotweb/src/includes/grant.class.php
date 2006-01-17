<?
// need to include main-functions for the getPolicy call
include_once("main-functions.php");
class Grant {
   var $id;
   var $user_id;
   var $expiration;
   var $status;
   var $policy_id;
   var $exp_volume;
   var $exp_time;
   var $exp_drinks;
   var $total_volume;
   var $total_drinks;

   var $policy_obj;

   function Grant($id) {
      $q = SQLQuery( $table = 'grants',
                     $select = NULL,
                     $where = array("`id`='$id'"),
                     $limit = 1 );
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      foreach ($row as $key => $val) {
         $this->$key = $val;
      }

      $this->policy_obj = new Policy($this->policy_id);
   }

   function getExpirationStr() {
      if (!strcmp($this->expiration,"time")) {
         $date = strftime("%D",$this->exp_time);
         return "on $date";
      }
      elseif (!strcmp($this->expiration,"volume")) {
         $oz = round(volunits_to_ounces($this->exp_volume), 2);
         return "after $oz ounces";
      }
      return "never";
   }
   function getToGo() {
      if (!strcmp($this->status, "expired")) {
         return "expired!";
      }
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
      elseif (!strcmp($this->expiration,"volume")) {
         $diff = $this->exp_volume - $this->total_volume;
         $diff = volunits_to_ounces($diff);
         $diff = round($diff,2);
         if ($diff <= 0) 
            return "expired!";
         return "$diff ounces";
      }
      return "--";
   }
}
?>
