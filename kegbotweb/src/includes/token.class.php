<?
class Token {
   var $id;
   var $ownerid;
   var $keyinfo;
   var $created;

   function Token($assoc) {
      $this->id = $assoc['id'];
      $this->ownerid = $assoc['ownerid'];
      $this->keyinfo = $assoc['keyinfo'];
      $this->created = $assoc['created'];

      $this->owner_obj = false;
   }
   function getOwnerName() {
      if ($this->owner_obj != false) {
         return $this->owner_obj->username;
      }
      else {
         return "unknown (" . $this->ownerid . ")";
      }
   }
   function setOwner($owner) {
      if ($owner != NULL) {
         $this->owner_obj = $owner;
      }
   }
}
?>
