<?
class Charge{
   var $kind;
   var $desc;
   var $link;
   var $amt;

   function Charge($k,$d,$l,$a) {
      $this->kind = $k;
      $this->desc = $d;
      $this->href = $l;
      $this->amt = $a;
   }
}

?>
