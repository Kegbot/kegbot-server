<?
class Keg {
   var $id;
   var $full_volume;
   var $startdate;
   var $enddate;
   var $status;
   var $type_id;
   var $descr;
   var $origcost;

   function Keg($id) {
      $q = SQLQuery( $table = 'kegs',
                     $select = NULL,
                     $where = array("`id`='$id'"),
                     $limit = 1 );
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      foreach ($row as $key => $val) {
         $this->$key = $val;
      }
      $this->beertype = GetBeerType($this->type_id);
   }

   function description() {
      return $this->beertype->name;
   }
   function abv() {
      return $this->beertype->abv;
   }
   function volumeServed() {
      $q = "SELECT SUM(volume) as 'tot' FROM `drinks` WHERE `keg_id`='{$this->id}'";
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      return $row['tot'];
   }
   function volumeLeft() {
      return $this->full_volume - $this->volumeServed();
   }

   function toCalories($volunits) {
      return volunits_to_ounces($volunits) * $this->calories_oz;
   }
}
?>
