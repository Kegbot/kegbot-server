<?
class Policy {
   var $id;
   var $gtype;
   var $unitcost;
   var $unitticks;
   var $descr;

   function Policy($a) {
      $this->id = $a['id'];
      $this->ptype = $a['type'];
      $this->unitcost = $a['unitcost'];
      $this->unitounces = $a['unitounces'];
      $this->descr = $a['description'];
   }
   function getCost($oz) {
      if ($this->unitcost == 0 or $this->unitounces == 0) {
         return 0.0;
      }
      else {
         $x = $this->getCostPerOunce() * $oz;
         return $x;
      }
   }
   function printCost() {
      if ($this->unitcost == 0 or $this->unitounces == 0)
         return "--";
      $cost = $this->getCostPerOunce();
      return "$cost&cent;/oz";
   }
   function getCostPerOunce() {
      if ($this->unitcost == 0 or $this->unitounces == 0)
         return 0;
      return 100 * $this->unitcost / $this->unitounces;
   }
}
?>
