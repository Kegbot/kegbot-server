<?
include_once("main-functions.php");

class GrantCharge {
   var $id;
   var $grant_id;
   var $user_id;
   var $drink_id;
   var $volume;

   function GrantCharge($id) {
      $q = SQLQuery( $table = 'grantcharges',
                     $select = NULL,
                     $where = array("`id`='$id'"),
                     $limit = 1 );
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      foreach ($row as $key => $val) {
         $this->$key = $val;
      }
      $this->grant_obj = GetGrant($this->grant_id);
   }
}
?>
