<?
   // functions to calculate BAC
   //
   // to calculate the BAC, we need to know:
   //    - person's gender

   function getBAC($lb_weight, $gender, $drink_ounces, $drink_alc_pct, $drink_time) {
      // method is based on following document:
      // http://www.nhtsa.dot.gov/people/injury/alcohol/bacreport.html
      //
      // inputs:
      //    $lb_weight     weight of subject, in pounds
      //    $drink_ounces  amount of drink, in ounces
      //    $drink_alc_pct alcoholic content of drink, in percent
      //    $drink_time    seconds elapsed since this drink

      // calculate weight in metric KGs
      $kg_weight = $lb_weight/2.2046;

      // set expected body water percentage (based on gender)
      if (! strcmp($gender,"male")) {
         $water_pct = 0.58;
      }
      else {
         $water_pct = 0.49;
      }

      // find total body water (in milliliters)
      $body_water = $kg_weight * $water_pct * 1000.0;

      // weight in grams of 1 oz of alcohol
      $alc_weight = 29.57 * 0.79; // (ml/oz) * (g/ml) = 23.26 grams

      // calculate teh rate of alcohol per subject's total body water
      $alc_per_body_ml = $alc_weight / $body_water;

      // find alcohol concentration in blood (80.6% of water)
      $alc_per_blood_ml = $alc_per_body_ml * 0.806;

      // switch alc_per_blood_ml to "grams percent", or grams of alcohol per 100 ml
      $grams_pct = $alc_per_blood_ml * 100.0;

      // NOW: grams_pct is the BAC 1 ounce of alcohol would produce in this
      // subject, with instant consumption, absorption, and distribution.

      // determine how much we've really consumed
      $alc_consumed = $drink_ounces * $drink_alc_pct;
      $instant_bac = $alc_consumed * $grams_pct;


      // NEXT: accomodate for consumption/absorption time
      // let $drink_time be the time that we believe the drink has been
      // consumed, in "seconds ago"
      // let $metab_rate be the rate of metabolism in one hour. (conservative: 0.012, average 0.017)
      $metab_rate = 0.017;
      $hours_ago = $drink_time/60/60;
      $metabolized_bac = ceil($instant_bac - ($hours_ago * $metab_rate), 0.0);

      // for instant bac, set drink_time to 0
      return $metabolized_bac;
   }

   function oldestAlcohol($lb_weight, $drink_ounces, $drink_alc_pct, $drink_time) {
      // determine how long ago, in seconds, we need look back to calculate the
      // BAC of a person. this is important because some drinks in the past
      // have completely metabolized, and we can ignore them
   }
?>
