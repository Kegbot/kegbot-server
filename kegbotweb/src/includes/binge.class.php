<?
include_once("main-functions.php");

class Binge {
   var $id;
   var $user_id;
   var $startdrink_id;
   var $enddrink_id;
   var $volume;

   function Binge($id) {
      $q = SQLQuery( $table = 'binges',
                     $select = NULL,
                     $where = array("`id`='$id'"),
                     $limit = 1 );
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      foreach ($row as $key => $val) {
         $this->$key = $val;
      }
      $this->drinker_obj = GetDrinker($this->user_id);
   }
   function getSize() {
      return volunits_to_ounces($this->volume);
   }

}
?>
