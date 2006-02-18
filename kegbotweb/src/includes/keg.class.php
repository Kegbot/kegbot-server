<?
class Keg {
   var $id;
   var $full_volume;
   var $startdate;
   var $enddate;
   var $status;
   var $beername;
   var $alccontent;
   var $calories_oz;
   var $descr;
   var $origcost;
   var $beerpalid;
   var $ratebeerid;

   var $beerpalbase = "http://www.beerpal.com/beerinfo.asp?ID=";
   var $ratebeerbase = "http://ratebeer.com/Ratings/Beer/Beer-Ratings.asp?BeerID=";

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
