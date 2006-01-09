<?
   include_once('load-config.php');
   include_once('drinker.class.php');
   include_once('charge.class.php');
   include_once('Smarty.class.php');
   global $skin, $css;
   include_once('session.php');
   include_once('main-functions.php');
   if ($_SESSION['skin']) {
      $skin = $_SESSION['skin'];
      $css  = $_SESSION['css'];
   }
   else {
      $skin = 'default';
      $css  = '/css.php?css=main.css';
   }

   function netcash_filter($val)
      {
         if ($val == 0) {
            return "--";
         }
         elseif ($val > 0) {
            return "<font color=\"green\">+$val</font>";
         }
         else {
            return "<font color=\"red\">$val</font>";
         }
      }
      function cash_filter($val)
      {
         if ($val == 0) {
            return "$val";
         }
         elseif ($val > 0) {
            return "<font color=\"green\">$val</font>";
         }
         else {
            return "<font color=\"red\">$val</font>";
         }
      }

   function money_fmt($m) {
      if ($m < 1) {
         return "no cost";
      }
      else {
         $m = round($m/100.0,2);
         return htmlentities(money_format('%.2n',$m),ENT_QUOTES,'ISO-8859-15');
      }
   }

   function bac_format($bac)
   {
      $bacval = max(0.0,floatval($bac) - 0.005);
      $amt = min( ($bacval/0.08) * 255.0,255);
      $color = sprintf("%0x0000 $amt",$amt);
      if ($bacval >= 0.08) {
         $bac = "<b>$bac</b>";
      }
      return "<font color=\"#$color\">$bac</font>";

   }

   function rel_date($stamp) {
      $diff = $GLOBALS['dbtime'] - $stamp;
      if ($diff < 60) { 
         $diff = round($diff);
         $s = ($diff == 1) ? "" : "s";
         return "$diff second$s ago";
      }
      elseif ($diff < 60*60) {
         $mins = round($diff/60);
         $s = ($mins == 1) ? "" : "s";
         return "$mins minute$s ago";
      }
      elseif ($diff < 60*60*24) {
         $hours = round($diff/(60*60));
         $s = ($hours == 1) ? "" : "s";
         return "$hours hour$s ago";
      }
      elseif ($diff < 60*60*24*7) {
         return strftime("%A %H:%M",$stamp);
      }
      else {
         return strftime("%B %e, %Y %H:%M", $stamp);
      }
  }

  class SmartyBeer extends Smarty {
      var $basedir;

      function SmartyBeer() {
         global $cfg, $skin, $css;
         // constructor
         $this->Smarty();

         $this->basedir = $cfg['dirs']['skindir'] . "/$skin";
         file_exists($this->basedir) || die("Skin dir {$this->basedir} not found!");
         $smartydir = $cfg['dirs']['smartytmp'] . "/$skin";
         file_exists($smartydir) || die("Smarty dir not found!");

         $this->template_dir = $this->basedir . '/templates/';
         $this->config_dir = $this->basedir . '/configs/';
         $this->compile_dir = $smartydir . '/templates_c/';
         $this->cache_dir = $smartydir . '/cache/';


         $this->register_modifier("rel_date","rel_date");
         $this->register_modifier("money_fmt","money_fmt");
         $this->register_modifier("bac_format","bac_format");
         $this->register_modifier("cash_filter",Array(&$this,"cash_filter"));
         $this->register_modifier("netcash_filter",Array(&$this,"netcash_filter"));

         $this->assign('app_name','Beer Bot');
         $this->assign('css',$css);
         $this->assign('skin',$skin);
         $this->assign('g_current_vol', getLeadersByVolume(false,5));
         $this->assign('g_alltime_vol', getLeadersByVolume(true,5));

         if (isset($_SESSION['drinker'])) {
            $this->assign('s_drinker',$_SESSION['drinker']);
         }

         // enable caching...
         $this->caching = 2;
         // for up to 1 minute
         $this->cache_lifetime = $cfg['smarty']['cachetime'];
         // and check for changes
         $this->compile_check = true;
      }

      function show_page($tpl, $cid="") {
         $this->display("misc/top.tpl", $cid);
         $this->display("pages/$tpl", $cid);
         $this->display("misc/bottom.tpl", $cid);
      }

   }

?>
