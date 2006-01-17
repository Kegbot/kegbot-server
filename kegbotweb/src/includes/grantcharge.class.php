<?
// need to include main-functions for the getPolicy call
include_once("main-functions.php");
class GrantCharge {
   var $id;
   var $grant_id;
   var $drink_id;
   var $user_id;
   var $volume;

   function GrantCharge($a) {
      $this->id = $a['id'];
      $this->grant_id= $a['grant_id'];
      $this->drink_id = $a['drink_id'];
      $this->user_id = $a['user_id'];
      $this->volume = $a['volume'];
   }
}
?>
