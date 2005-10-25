<?
   // start the session. any page that wants sessioning shall include this
   // file.
   ini_set("session.use_only_cookies", 1);
   if (!session_id()) {
      session_name("SID");
      session_set_cookie_params (60*60*24*365*10, '/');
      session_start();
      #if ( $SID != "" ) {
         #   header("Location: /needcookies.php");
         #   exit();
         #}
      if (!isset($_SESSION['login_attempts'])) {
         $_SESSION['login_attempts'] = 0;
      }
   }
?>
