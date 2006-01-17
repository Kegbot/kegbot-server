<?
class Policy {
   var $id;
   var $gtype;
   var $unitcost;
   var $unitticks;
   var $descr;

   function Policy($id) {
      $q = SQLQuery( $table = 'policies',
                     $select = NULL,
                     $where = array("`id`='$id'"),
                     $limit = 1 );
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      foreach ($row as $key => $val) {
         $this->$key = $val;
      }
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
