<?
include_once('units.php');
class Drink {
   var $id;
   var $ticks;
   var $volume;
   var $starttime;
   var $endtime;
   var $user_id;
   var $keg_id;
   var $status;

   function Drink($id) {
      $q = SQLQuery( $table = 'drinks',
                     $select = NULL,
                     $where = array("`id`='$id'"),
                     $limit = 1 );
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      foreach ($row as $key => $val) {
         $this->$key = $val;
      }
      $this->keg_obj = new Keg($this->keg_id);
      $this->drinker_obj = new Drinker($this->user_id);
   }

   function inOunces() {
      return volunits_to_ounces($this->volume);
   }

   function getCalories() {
      return $this->keg_obj->toCalories($this->volume);
   }

   function getCost() {
      return 0; // TODO FIXME
   }

   function getSize() { // XXX needed
      return $this->inOunces();
   }

}

?>
