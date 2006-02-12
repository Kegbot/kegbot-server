<div class="contenthead">
current leaders
</div>
<div class="content">
   <p>
      <center>
      <form action="{module_url module="leaders"}" method="get">
         <input type="submit" name="show" value="show">
         {html_options name="num" options=$select_range selected=$max_leaders}
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
   </tr>
{load_leaders_by_volume assign="alltime_vol" limit=$max_leaders}
   <tr>
      <td align="center" valign="top">
         { foreach name=alltime_vol item="volleader" from=$alltime_vol} 
             { include file="boxes/leader-box.tpl" units=$volleader.units border=1 leadinfo=$volleader place=$smarty.foreach.alltime_vol.iteration }
         { /foreach }
      </td>
{load_leaders_by_volume assign="current_vol" limit=$max_leaders keg="current"}
      <td align="center" valign="top">
      { foreach name=current_vol item="kegleader" from=$current_vol} 
          { include file="boxes/leader-box.tpl" border=1 units=$kegleader.units leadinfo=$kegleader place=$smarty.foreach.current_vol.iteration }
      { /foreach }
      </td>
{load_leaders_by_bac assign="alltime_bac" limit=$max_leaders keg="current"}
      <td align="center" valign="top">
      { foreach name=alltime_bac item="BACleader" from=$alltime_bac } 
         { include file="boxes/leader-box.tpl" border=1 units="%" leadinfo=$BACleader place=$smarty.foreach.alltime_bac.iteration }
      { /foreach }
      </td>
   </tr>
   </table>
   </p>
</div>

<div class="contenthead">
   leader movement
</div>
<div class="content">
      <img src=graphs/gen-graph.php?g=historical">
      <p>
         this graph plots all-time total ounces versus actual drinks. each time
         someone takes a drink, the plots step one place to the right. flat
         sections show periods of drinker inactivity.
      </p>
</div>
