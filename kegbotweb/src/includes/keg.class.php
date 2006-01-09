<?
class Keg {
   var $id;
   var $tickmetric;
   var $startounces;
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

   function Keg($assoc) {
      $this->id = $assoc['id'];
      $this->tickmetric = $assoc['tickmetric'];
      $this->startounces = $assoc['startounces'];
      $this->startdate = $assoc['startdate'];
      $this->enddate = $assoc['enddate'];
      $this->status = $assoc['status'];
      $this->beername = $assoc['beername'];
      $this->alccontent = $assoc['alccontent'];
      $this->calories = $assoc['calories_oz'];
      $this->descr = $assoc['description'];
      $this->origcost = $assoc['origcost'];
      $this->beerpalid = $assoc['beerpalid'];
      $this->ratebeerid = $assoc['ratebeerid'];
   }
   function getDescrLinkified() {
      return "<a href=\"/keg-info.php?keg={$this->id}\">{$this->beername}</a>";
   }

   // return how many ticks makes a full keg; accomodate for whatever units the
   // capacity is stored in. (currently: ounces)
   function ticksWhenFull() {
      return $this->startounces * $this->tickmetric;
   }

   function toOunces($ticks) {
      return $ticks/$this->tickmetric;
   }
   function toCalories($ticks) {
      return $this->toOunces($ticks) * $this->calories;
   }
}
?>
