<?
require_once('load-config.php');
class Drinker {
   var $id;
   var $username;
   var $email;
   var $im_aim;
   var $admin;
   var $weight;
   var $gender;
   var $current_bac = 0.0;
   var $stats = NULL;

   function Drinker($assoc) {
      $this->id = $assoc['id'];
      $this->username = $assoc['username'];
      $this->email = $assoc['email'];
      $this->im_aim = $assoc['im_aim'];
      $this->weight = $assoc['weight'];
      $this->gender= $assoc['gender'];
      $this->admin = False;
      if ($assoc['admin'] == 'yes') {
         $this->admin = True;
      }
   }
   function getLink() {
      //return "drinker-info.php?drinker={$this->id}";
      return "/drinker/{$this->username}";
   }
   function getNameLinkified() {
      //return "<a href=\"/drinker-info.php?drinker={$this->id}\">{$this->username}</a>";
      return "<a href=\"/drinker/{$this->username}\">{$this->username}</a>";
   }
   function setCurrentBAC($bac) {
      $this->current_bac = $bac;
   }
   function isAdmin() {
      return $this->admin == True;
   }
   function getMugshotURL() {
      global $cfg;
      $uf = $cfg['dirs']['imagedir'] . "/{$this->username}.jpg";
      if (!file_exists($uf)) {
         return "/images/unknown-drinker.png";
      }
      return "/userpics/{$this->username}.jpg";
   }
   function getSlots() {
      $slots= Array();
      $slots[] = Array("pos" => "1", "name" => "", "file" => "");
      $slots[] = Array("pos" => "2", "name" => "", "file" => "");
      $slots[] = Array("pos" => "3", "name" => "", "file" => "");
      $slots[] = Array("pos" => "4", "name" => "", "file" => "");
      $slots[] = Array("pos" => "5", "name" => "", "file" => "");
      $slots[] = Array("pos" => "6", "name" => "", "file" => "");

      // load any real slots...
      $udir = "/home/mike/htdocs/userpics/{$this->id}";
      if ($handle = @opendir($udir)) {
         while (false !== ($file = readdir($handle))) { 
            $f = preg_replace('/(.+)\..*$/', '$1', basename($file));
            $found[$f] = $file;
         }
      }
      foreach ($found as $f_key => $f_file) {
         foreach ($slots as $slot) {
            if (!strcmp($slot['pos'], $f_key)) {
               print "MATC!!!\n";
               $slot['file'] = $f_file;
            }
            else {
               print $f_key . '\n';
            }
         }
      }
      print_r($slots);
      return $slots;
   }
}
?>
