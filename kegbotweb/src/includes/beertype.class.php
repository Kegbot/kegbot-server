<?
class BeerType {
   var $id;
   var $name;
   var $brewer_id;
   var $style_id;
   var $calories_oz;
   var $carbs_oz;
   var $abv;

   function BeerType($id) {
      $q = SQLQuery( $table = 'beertypes',
                     $select = NULL,
                     $where = array("`id`='$id'"),
                     $limit = 1 );
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      foreach ($row as $key => $val) {
         $this->$key = $val;
      }
   }

}
?>
