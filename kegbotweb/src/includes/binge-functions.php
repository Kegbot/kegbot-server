<?
   include_once('session.class.php');
   function getSessions($uid) {
      $drinks = getUserDrinks($uid, "ASC");

      $sessions = Array();
      $idx = 0;
      $sessnum = 0;
      $numdrinks = sizeof($drinks);
      $sess_gap = 90* 60;
      foreach ($drinks as $drink) {
         // first, if this drink happens more than $sess_gap after the last drink, then we have a new session
         if (!isset($last_drink) || ($drink->starttime - $last_drink->endtime) > $sess_gap) {
            $sessions[] = new Session();
            $sessnum = sizeof($sessions) - 1;
         }
         // either we're using our old session, or we just started a new one.
         // either way, add the drink!
         $sessions[$sessnum]->addDrink($drink);
         $sessions[$sessnum]->num = $sessnum + 1;

         $last_drink = $drink;
         $idx++;
      }

      // we should now have an array of sessions, each session being an array of drinks.
      return $sessions;
   }
?>
