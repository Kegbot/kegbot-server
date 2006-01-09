<div class="contenthead">
   info for keg #{$keg->id}
</div>
<div class="content">
   <p>
   <table cellspacing=3 border=0 width="430">
      <tr>
         <td align="right" valign="top"><b>name:</b></td>
         <td>
            {$keg->beername} ({$keg->alccontent|string_format:"%.2f"}% alcohol)
            </td>
         <td rowspan="6" align="right">
            <img src="/images/keg.png" width="77" height="100">
         </td>
      </tr>
      {if $keg->ratebeerid or $keg->beerpalid}
      <tr>
         <td align="right"><b>beer info:</b></td>
         <td>
            { if $keg->ratebeerid != 0} 
               <a href="{$keg->ratebeerbase}{$keg->ratebeerid}">ratebeer</a>
            {/if}
            &nbsp;
            { if $keg->beerpalid != 0} 
               <a href="{$keg->beerpalbase}{$keg->beerpalid}">beerpal</a>
            {/if}
            &nbsp;
         </td>
      </tr>
      {/if}
      <tr>
         <td align="right"><b>status:</b></td>
         <td>{$keg->status}</td>
      </tr>
      <tr>
         <td align="right"><b>ticks/ounce:</b></td>
         <td>{$keg->tickmetric|string_format:"%.1f"}</td>
      </tr>
      <tr>
         <td align="right"><b>activated:</b></td>
         <td>{$keg->startdate|date_format}</td>
      </tr>
      <tr>
         <td align="right"><b>last pour:</b></td>
         <td><a href="/drink-info.php?drink={$last_drink->id}">{$last_drink->starttime|date_format:"%b %e %Y, %H:%M:%S"}</a></td>
      </tr>
      <tr>
         <td align="right"><b>drinks served:</b></td>
         <td>{$drinks_served} ({$full_pct|string_format:"%.1f"}% full)</td>
      </tr>
      {if $keg->descr}
      <tr>
         <td valign="top" align="right"><b>description:</b></td>
         <td align="left" valign="top">
         {$keg->descr}
         </td>
      </tr>
      {/if}
   </table>
   </p>
</div>
<div class="contenthead">
   full drink history
</div>
<div class="content">
   {if $keg->status == "online"}
   <img src="http://kegbot.org/graphs/gen-graph.php?g=keghist">
   {/if}
   {if $usehistory}
   <p>
      full drink history for keg shown below. <a href="/keg/{$keg->id}">hide history</a>.
   <p>
   <table cellspacing=0 border=0 width="430">
   <tr>
      <td><b>#</b></td><td align="right"><b>size</b></td><td>&nbsp;</td><td><b>user</b></td><td><b>when</b></td>
   </tr>
   { foreach name=drinks item="drink" from=$drinks }
      { include file="spans/drink.tpl" drink=$drink } 
   { /foreach }
   </table>
   </p>
   {else}
   <p>
      to show full drink history for this keg, <a href="/keg-info.php?keg={ $keg->id }&history=1">click here</a>
   </p>
   {/if}

</div>

<div class="contenthead">
   leaders of keg {$keg->id}
</div>
<div class="content">
   <p>
   <br>
   { foreach name=all_drinkers item="d" from=$keg_volleaders}
   { if $d->stats.alltime_vol >= 16.0 }
   <div class="box">
   <table width="100%" border="0" cellpadding="3" cellspacing="3">

   <tr>
      <td align="center" valign="top">
            { include file="boxes/mugshot-box.tpl" u=$d d=100}
            <font size="+1">{$d->getNameLinkified()}</font>
      </td>

      <td valign="top">
         {if $d->stats.alltime_vol < 16.0}
         <font size="+1" color="#ff0000">
            <b>hall of shame finalist</b>
         </font>
         {else}
            {include file="boxes/drinker-quickshot.tpl" drinker=$d stats=$d->stats}
         {/if}
      </td>
   </tr>
   </table>
   </div>
   <br>
   {/if}
   { /foreach }
   </p>
</div>
