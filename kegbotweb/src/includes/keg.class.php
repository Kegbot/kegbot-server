<?
class Keg {
   var $id;
   var $full_volume;
   var $startdate;
   var $enddate;
   var $status;
   var $beername;
   var $alccontent;
   var $calories;
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

   /**
   *
   * Return amount of volume left in keg.
   *
   * @return	int	 volunits remaining
   */
   function volumeLeft() {
      $q = "SELECT SUM(volume) as 'tot' FROM `drinks` WHERE `keg_id`='{$this->id}'";
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      $gone = $row['tot'];
      return $this->full_volume - $gone;
   }

   function toOunces($volunits) {
      return $volunits * 0.0338140226;
   }

   function toCalories($volunits) {
      return $this->toOunces($volunits) * $this->calories;
   }
}
?>
