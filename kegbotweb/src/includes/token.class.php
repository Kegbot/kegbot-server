<?
class Token {
   var $id;
   var $user_id;
   var $keyinfo;
   var $created;

   function Token($id) {
      $q = SQLQuery( $table = 'tokens',
                     $select = NULL,
                     $where = array("`id`='$id'"),
                     $limit = 1 );
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      foreach ($row as $key => $val) {
         $this->$key = $val;
      }
      $this->owner_obj = GetDrinker($this->user_id);
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
