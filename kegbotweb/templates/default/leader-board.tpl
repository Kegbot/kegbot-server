<div class="contenthead">
   top drinkers (all time)
</div>
<div class="content">
   <p>
   <table cellspacing=0 border=0 width="430">
   <tr>
      <td valign="top">
      <table cellspacing=0 border=0 width="210">
      <tr>
    <td colspan=3 align=center><b>by volume</b></td>
      </tr>
      <tr>
    <td><b>place</b></td><td><b>user</b></td><td align="right"><b>ounces</b></td>
      </tr>
      { foreach name=alltime_vol item="volleader" from=$alltime_vol} 
          { include file="vol-span.tpl" volleader=$volleader place=$smarty.foreach.alltime_vol.iteration }
      { /foreach }
      </table>
      </td>
      <td width="20"> &nbsp;&nbsp;&nbsp; </td>
      <td valign="top">
      <table cellspacing=0 border=0 width="210">
      <tr>
    <td colspan=3 align=center><b>by number</b></td>
      </tr>
      <tr>
         <td><b>place</b></td><td><b>user</b></td><td align="right"><b>drinks</b></td>
      </tr>
      { foreach name=alltime_num item="numleader" from=$alltime_num} 
         { include file="num-span.tpl" numleader=$numleader place=$smarty.foreach.alltime_num.iteration }
      { /foreach }
      </table>
      </td>
   </tr>
   </table>
   </p>
</div>


<div class="contenthead">
   top drinkers (current keg)
</div>
<div class="content">
   <p>
   <table cellspacing=0 border=0 width="430">
   <tr>
      <td valign="top">
      <table cellspacing=0 border=0 width="210">
      <tr>
    <td colspan=3 align=center><b>by volume</b></td>
      </tr>
      <tr>
    <td><b>place</b></td><td><b>user</b></td><td align="right"><b>ounces</b></td>
      </tr>
      { foreach name=current_vol item="kegleader" from=$current_vol} 
          { include file="vol-span.tpl" volleader=$kegleader place=$smarty.foreach.current_vol.iteration }
      { /foreach }
      </table>
      </td>
      <td width="20"> &nbsp;&nbsp;&nbsp; </td>
      <td valign="top">
      <table cellspacing=0 border=0 width="210">
      <tr>
    <td colspan=3 align=center><b>by number</b></td>
      </tr>
      <tr>
         <td><b>place</b></td><td><b>user</b></td><td align="right"><b>drinks</b></td>
      </tr>
      { foreach name=current_num item="kegleader" from=$current_num} 
         { include file="num-span.tpl" numleader=$kegleader place=$smarty.foreach.current_num.iteration }
      { /foreach }
      </table>
      </td>
   </tr>
   </table>
   </p>
</div>


<div class="contenthead">
   highest observed BACs
</div>
<div class="content">
   <p>
   <table cellspacing=0 border=0 width="430">
      <tr>
         <td><b>place</b></td><td><b>user</b></td><td align="right"><b>blood alc. %</b></td>
      </tr>
      { foreach name=alltime_bac item="BACleader" from=$alltime_bac } 
         { include file="BAC-span.tpl" BACleader=$BACleader place=$smarty.foreach.alltime_bac.iteration }
      { /foreach }
   </table>
   </p>
</div>

<div class="contenthead">
   leader movement
</div>
<div class="content">
   <p>
      <img src="http://kegbot.org/graphs/test-graph.php">
   </p>
</div>
