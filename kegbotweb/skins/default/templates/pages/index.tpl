<LINK REL="alternate" TITLE="Kegbot RSS" HREF="http://www.kegbot.org/main.rss" TYPE="application/rss+xml">
<div class="contenthead">
   welcome{if $s_drinker->username}, {$s_drinker->username}{/if}
</div>
<div class="content">
   <p>
   this is the kegbot kegerator! for more information, see the <a
   href="http://kegbot.org/project/">project page</a>.
   </p>
</div>
<div class="contenthead">
   last five drinks
</div>

{load_drinks assign="last_drinks" limit="5" order_by="id" order_dir="desc"}

<div class="content">
   {if !$last_drinks}
   <p>
   virgin kegbot; no drinks yet recorded! this is indeed a very special time...
   </p>
   {else}
   <p>
   <div align="center">
   <table border="0" cellspacing="1" cellpadding="1">
   <tr>
   <td>&nbsp;</td>
   { foreach name=drinks item="drink" from=$last_drinks }
      <td>
         <center>
         <a href="{module_url module="drink-info" drink=$drink->id}">
         {include file="boxes/mugshot-box.tpl" u=$drink->drinker_obj d="72" border=1}
         </a>
         </center>
      </td>
      <td>&nbsp;</td>
   {/foreach}
   </tr>
   <tr>
      <td>&nbsp;</td>
   { foreach name=drinks item="drink" from=$last_drinks }
      <td align="center">
         {$drink->getSize()|string_format:"%.2f"} oz
      </td>
      <td>&nbsp;</td>
   {/foreach}
   </tr>
   </table>
   </div>
   </p>
   <p>
   <div class="box">
   <table cellspacing=0 border=0 width="430">
   <tr>
      <td>&nbsp;</td>
      <td align="right"><b>size</b></td>
      <td>&nbsp;</td>
      <td align="right" colspan="2"><b>calories</b>&nbsp;&nbsp;</td>
      <td><b>user</b></td>
      <td><b>when</b></td>
      <td><b>bac</b></td>
   </tr>
   { foreach name=drinks item="drink" from=$last_drinks }
      { include file="spans/drink.tpl" drink=$drink } 
   { /foreach }
   </table>
   </div>
   {/if}
      {if 0}
      <img src="http://kegbot.org/graphs/gen-graph.php?g=keghist">
      {/if}
   </p>
</div>

<div class="contenthead">
   current drunks!
</div>

{load_current_drunks assign="drunks"}

<div class="content">
   <p>
   {if $drunks}
      <table cellspacing=0 width="430">
         <tr>
            <td><b>drinker</b></td>
            <td><b>current bac</b></td>
         </tr>
      {foreach name=drunks item="drinker" from=$drunks}
         {include file="boxes/bac-leaders.tpl" drinker=$drinker }
      {/foreach}
      </table>
   {else}
   all drinkers appear to be sober right now. i am lonely.
   {/if}
   </p>
</div>

<!--
<div class="contenthead">
   current keg status
</div>
<div class="content">
   <p>
      <center>
         <b><a href="/keg/{$curr_keg->id}">{$curr_keg->beername}</a></b>; {$curr_keg->alccontent|string_format:"%.1f"}% abv; <i>{$curr_keg->status}</i>; {$keg_temp_c|string_format:"%.2f"} &deg;C / {$keg_temp_f|string_format:"%.2f"} &deg;F<br>
      </center>
   </p>
   <p>
      <div class="box">
      <img src="/graphs/gen-graph.php?g=current-temps&d={$graphdays}"><br>
      <img src="/graphs/gen-graph.php?g=current-fridge&d={$graphdays}"><br>
      </div>
   </p>
   <p>
      sensor data is collected every 30 seconds, and this graph is refreshed at
      least once per minute. note that the stated accuracy of the temperature
      sensors is a rather large &#177;0.5 &deg;C.
   </p>
   <p>
      the moving average is computed only for the primary sensor, and is based
      on the last 30 points, or roughly, the last 15 minutes of measurements.
   </p>
</div>
-->

<div class="contenthead">
   tags
</div>
<div class="content">
   <p>
   {if $s_drinker}
   {foreach from=$tags item="tag"}
   {include file="spans/tag.tpl"}
   {/foreach}
   {else}
   must be logged in to view tags
   {/if}
   </p>
</div>
