<div class="contenthead">
current leaders
</div>
<div class="content">
   <p>
   <center>
   {if $refresh}
      autorefresh enabled [<a href="/leaders2.php">disable</a>]
   {else}
      autorefresh disabled [<a href="/leaders2.php?r=1">enable</a>]
   {/if}
   </p>
   <p>
      <form action="leaders2.php" method="get">
         <input type="submit" name="show" value="show">
         <select name="num">
         <option>5
         <option>6
         <option>7
         <option>8
         <option>9
         <option>10
         <option>15
         <option>25
         <option value="500">all
         </select>
         drinkers per award
      </form>
   </center>
   </p>
   <p>
   <table border="0">
   <tr>
      <td align="center">
         <b>all-time top drinkers</b>
      </td>
      <td align="center">
         <b>current keg top drinkers</b>
      </td>
      <td align="center">
         <b>blood alcohol freaks</b>
      </td>
      <td align="center">
         <b>largest binge</b>
      </td>
   </tr>
   <tr>
      <td align="center" valign="top">
         { foreach name=alltime_vol item="volleader" from=$alltime_vol} 
             { include file="leader-box.tpl" units=$volleader.units border=1 leadinfo=$volleader place=$smarty.foreach.alltime_vol.iteration }
         { /foreach }
      </td>
      <td align="center" valign="top">
      { foreach name=current_vol item="kegleader" from=$current_vol} 
          { include file="leader-box.tpl" border=1 units=$kegleader.units leadinfo=$kegleader place=$smarty.foreach.current_vol.iteration }
      { /foreach }
      </td>
      <td align="center" valign="top">
      { foreach name=alltime_bac item="BACleader" from=$alltime_bac } 
         { include file="leader-box.tpl" border=1 units="%" leadinfo=$BACleader place=$smarty.foreach.alltime_bac.iteration }
      { /foreach }
      </td>
      <td align="center" valign="top">
      { foreach name=alltime_binge item="binger" from=$alltime_binge } 
         { include file="leader-box.tpl" border=1 units="%" leadinfo=$binger place=$smarty.foreach.alltime_binge.iteration }
      { /foreach }
      </td>
   </tr>
   </table>
   </p>
</div>

{if $edition == 'default'}
<div class="contenthead">
   leader movement
</div>
<div class="content">
      <img src="http://kegbot.org/graphs/gen-graph.php?g=historical">
      <p>
         this graph plots all-time total ounces versus actual drinks. each time
         someone takes a drink, the plots step one place to the right. flat
         sections show periods of drinker inactivity.
      </p>
</div>
{/if}
