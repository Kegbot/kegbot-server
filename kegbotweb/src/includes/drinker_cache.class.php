<?
class Drinker_cache{
   var $id = 0;
   var $username = "";
   var $totaloz = 0;
   var $totaldrinks = 0;
   var $totaldrinkers = 0;
   var $lastdrink = 0;
   var $starttime = "9223372036854775800";
   var $kegdrinks = 0;
   var $kegoz = 0;
   var $maxBAC = 0;
   var $totaltime = 0;
   var $drinker_obj = NULL;
   
   function Drinker_cache($assoc) {
      if($assoc){
      $this->id = $assoc['id'];
      $this->username = $assoc['username'];
      $this->totaloz = $assoc['totaloz'];
      $this->totaldrinks = $assoc['totaldrinks'];
      $this->totaldrinkers = $assoc['totaldrinkers'];
      $this->lastdrink = $assoc['lastdrink'];
      $this->starttime = $assoc['starttime'];
      $this->totaltime = $assoc['totaltime'];
      $this->kegdrinks = $assoc['kegdrinks'];
      $this->kegoz = $assoc['kegoz'];
      $this->maxBAC = $assoc['maxBAC'];
      $this->drinker_obj = false;
      }
   }

   function setid ($userid){
      $this->id = $userid;
   }
   function setusername ($name){
      $this->username = $name;
   }
   function settotaloz ($oz){
      $this->totaloz = $oz;
   }
   function settotaldrinks ($drinks){
      $this->totaldrinks = $drinks;
   }
   function settotaldrinkers ($drinkers){
      $this->totaldrinkers = $drinkers;
   }
   function setlastdrink ($lastdrink){
      $this->lastdrink = $lastdrink;
   }
   function setdrinker(&$drinker) {
      $this->drinker_obj = $drinker;
   }
   function setkegdrinks($drinks) {
      $this->kegdrinks = $drinks;
   }
   function setkegoz($oz) {
      $this->kegoz = $oz;
   }
   function setmaxBAC($max) {
      $this->maxBAC = $max;
   }
   function getmaxBAC() {
      return $this->maxBAC;
   }
}

?>
