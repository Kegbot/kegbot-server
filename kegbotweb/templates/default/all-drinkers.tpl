<div class="contenthead">
   all known drinkers
</div>
<div class="content">
   <p>
   <br>
   { foreach name=all_drinkers item="d" from=$drinkers}
   <div class="box">
   <table width="100%" border="0" cellpadding="3" cellspacing="3">
   <tr>
      <td align="center" valign="top">
            { include file="mugshot-box.tpl" u=$d d=100}
            <font size="+1">{$d->getNameLinkified()}</font>
      </td>

      <td valign="top">
         {if $d->stats.alltime_vol < 16.0}
         <font size="+1" color="#ff0000">
            <b>hall of shame finalist</b>
         </font>
         {else}
            {include file="drinker-quickshot.tpl" drinker=$d stats=$d->stats}
         {/if}
      </td>
   </tr>
   </table>
   </div>
   <br>
   { /foreach }
   </p>
</div>
