<div class="contenthead">
   all known drinkers
</div>
{load_drinkers assign="drinkers"}
{load_drinker_stats assign="stats"}
<div class="content">
   <p>
   <br>
   {foreach name=all_drinkers item="d" from=$drinkers}
   {assign var="drinkerid" value=$d->id}
   {load_drinker_stats assign="stats" id=$d->id}
   {if $stats.alltime_vol >= 64.0}
   <div class="box">
   <table width="100%" border="0" cellpadding="3" cellspacing="3">
   <tr>
      <td align="center" valign="top">
            { include file="boxes/mugshot-box.tpl" u=$d d=100}
            <font size="+1">{include file="misc/drinker-link.tpl drinker=$d}</font>
      </td>

      <td valign="top">
         {include file="boxes/drinker-quickshot.tpl" drinker=$d stats=$stats}
      </td>
   </tr>
   </table>
   </div>
   <br>
   {/if}
   { /foreach }
   </p>

   <p>
   <h2 align="center">hall of shame</h2>
   <div class="box">
   <center>find us in the street and ridicule us!<br></center>
   {foreach name=all_drinkers item="d" from=$drinkers}
   {assign var="drinkerid" value=$d->id}
   {load_drinker_stats assign="stats" id=$d->id}
   {if $stats.alltime_vol < 64.0}
   <div style="text-align:center; float:left; padding-right: 5px; padding-top:5px;">
      { include file="boxes/mugshot-box.tpl" u=$d d=100}
      {include file="misc/drinker-link.tpl drinker=$d}
   </div>
   {/if}
   {/foreach}
   <div class="spacer">&nbsp;</div>
   </div>
   </p>
</div>
