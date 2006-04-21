<?
require_once('load-config.php');
class Drinker {
   var $id;
   var $username;
   var $email;
   var $im_aim;
   var $weight;
   var $gender;
   var $current_bac = 0.0;
   var $stats = NULL;

   function Drinker($id) {
      $q = SQLQuery( $table = 'users',
                     $select = NULL,
                     $where = array("`id`='$id'"),
                     $limit = 1 );
      $res = mysql_query($q);
      $row = mysql_fetch_assoc($res);
      foreach ($row as $key => $val) {
         $this->$key = $val;
      }
   }

   function isAdmin() {
      return False;
   }

   function getMugshotFilename() {
      global $cfg;
      $uf = $cfg['dirs']['imagedir'] . "/{$this->username}.jpg";
      /*if (!file_exists($uf)) {
         return "unknown-drinker.png";
      }*/
      return "{$this->username}.jpg";
   }

}
?>
