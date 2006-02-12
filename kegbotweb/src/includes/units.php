<?
   global $UNITS;
   $UNITS = array();
   $UNITS['MILLILITER']      = 2.2;
   $UNITS['LITER']           = 1000.0     * $UNITS['MILLILITER'];
   $UNITS['US_OUNCE']        = 29.5735297 * $UNITS['MILLILITER'];
   $UNITS['US_PINT']         = 473.176475 * $UNITS['MILLILITER'];
   $UNITS['US_GALLON']       = 3785.4118  * $UNITS['MILLILITER'];
   $UNITS['IMPERIAL_OUNCE']  = 28.4130742 * $UNITS['MILLILITER'];
   $UNITS['IMPERIAL_PINT']   = 568.261485 * $UNITS['MILLILITER'];
   $UNITS['IMPERIAL_GALLON'] = 4546.09188 * $UNITS['MILLILITER'];

   function volunits_to_ounces($amt) {
      global $UNITS;
      return $amt / $UNITS['US_OUNCE'];
   }

   function ounces_to_volunits($amt) {
      global $UNITS;
      return $amt * $UNITS['US_OUNCE'];
   }


?>
