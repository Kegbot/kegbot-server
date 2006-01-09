<LINK REL="alternate" TITLE="{$drinker->username} RSS Drink History" HREF="http://www.kegbot.org/drinker/{$drinker->username}/drinks.rss" TYPE="application/rss+xml">
<div class="contenthead">
   drinker info: {$drinker->username}
</div>
<div class="content">
   <table width="100%" cellspacing=3 cellpadding=1 border=0>
      <tr>
         <td rowspan="8" align="center" valign="top" width=140>
            <div>
            { include file="mugshot-box.tpl" u=$drinker d=128}
            </div>
            <font size=+1>{$rating}</font><br>({$avg_drinks_hour|string_format:"%.1f"} drinks/hour)
         </td>
      </tr>
      <tr>
         <td valign="top">
            {include file="drinker-quickshot.tpl"}
         </td>
      </tr>
   </table>
</div>

<div class="contenthead">
   binge statistics
</div>
<div class="content">
   {if $num_sess > 0}
      {include file="binge-stats.tpl"}
   {else}
   <p>
      this guy hasn't had nearly enough to drink! no statistics are available for babies...
   </p>
   {/if}
</div>   
<div class="contenthead">
   full drink history
</div>
<div class="content">
   {if $usehistory}
   <p>
      full drink history for { $drinker->username } is shown below. <a href="/drinker-info.php?drinker={$drinker->id}">hide history</a>.
   <p>
   <table cellspacing=0 border=0 width="430">
   <tr>
      <td><b>#</b></td><td align="right"><b>size</b></td><td>&nbsp;</td><td><b>user</b></td><td><b>when</b></td><td><b>bac</b></td>
   </tr>
   { foreach name=drinks item="drink" from=$drinks }
      { include file="drink-span.tpl" drink=$drink } 
   { /foreach }
   </table>
   </p>
   {else}
   <p>
      to show full drink history for this drinker, <a href="/drinker-info.php?drinker={ $drinker->id }&history=1">click here</a>
   </p>
   {/if}
</div>

