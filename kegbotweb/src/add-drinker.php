<?
   require_once('includes/allclasses.php');
   require_once('includes/loggedin-required.php');
   require_once('includes/admin-required.php');
   require_once('includes/main-functions.php');
   require_once('includes/units.php');

   // create the drinker
   $did = createUser($_POST['username'],
      $_POST['password'],
      $_POST['gender'],
      $_POST['weight'],
      $_POST['email']);

   if ($did == NULL) {
      echo "Error creating drinker!";
      exit;
   }

   // create the first policy
   if (intval($_POST['policy']) != -1) {
      grantPolicy(intval($_POST['policy']), $did, 'none', 0, 0);
   }

   // create initial token
   if (!empty($_POST['token'])) {
      createToken($did, $_POST['token']);
   }

   Header('Location: admin-info.php');
?>
