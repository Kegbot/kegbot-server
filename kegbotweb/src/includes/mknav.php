<?
   require_once("XMLParser.obj");
   function genNavbar($section,$page)
   {
      $parser = new XMLParser("includes/nav.xml","file",1);
      $sections = $parser->getTree();

      //print_r($sections['NAVPLACES']);

      $sects = $sections['NAVPLACES']['SECTION'];
      echo '<div class="leftnav">';
      foreach ($sects as $key => $value) {
         echo '<div class="sepbar">';
         echo "<b>" . $value['ATTRIBUTES']['NAME'] . "</b>";
         echo "</div>\n";

         echo "<div class=\"navbox\">\n";
         foreach ($value['SUBSECTION'] as $sectidx => $subsect) {
            $link = $subsect['ADDR']['VALUE'];
            $title = $subsect['TITLE']['VALUE'];
            echo "   <div class=\"navlink\" style=\"padding-right:3px;\">\n";
            echo "      <a style=\"color:#111\" href=\"$link\">$title</a>\n";

            echo "   </div>\n";
         }
         echo "</div><br>\n";
      }
      echo "</div>\n";
   }

?>
