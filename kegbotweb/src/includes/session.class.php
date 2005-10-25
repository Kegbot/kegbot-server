<?
class Session {
   var $drinks;
   var $num = 0;

   function Session() {
      $this->drinks = Array();
      $this->num = 0;
   }

   function addDrink($drink) {
      $this->drinks[] = $drink;
   }

   function getStart() {
      return $this->drinks[0]->starttime;
   }
   function getEnd() {
      return $this->drinks[sizeof($this->drinks) - 1]->endtime;
   }
   function totalDrinks() {
      return sizeof($this->drinks);
   }
   function totalOunces() {
      $ounces = 0.0;
      foreach ($this->drinks as $d) {
         $ounces += $d->inOunces();
      }
      return round($ounces,2);
   }

}

?>
