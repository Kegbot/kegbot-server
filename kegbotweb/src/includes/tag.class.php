<?
class Tag {
   var $id;
   var $user_id;
   var $postdate;
   var $message;

   function Tag($assoc) {
      $this->id = $assoc['id'];
      $this->user_id= $assoc['user_id'];
      $this->postdate= $assoc['postdate'];
      $this->message= $assoc['message'];
      $this->bac = $assoc['bac'];

      $this->drinker_obj = NULL;
   }
}
?>
