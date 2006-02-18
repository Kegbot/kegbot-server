<LINK REL="alternate" TITLE="{$drinker->username} RSS Drink History" HREF="http://www.kegbot.org/drinker/{$drinker->username}/drinks.rss" TYPE="application/rss+xml">
{load_drinker assign="drinker" id=$id}
<div class="contenthead">
   drinker info: {$drinker->username}
</div>
<div class="content">
   <table width="100%" cellspacing=3 cellpadding=1 border=0>
      <tr>
         <td rowspan="8" align="center" valign="top" width=140>
            <div>
            { include file="boxes/mugshot-box.tpl" u=$drinker d=128}
            </div>
            <font size=+1>{$rating}</font><br>({$avg_drinks_hour|string_format:"%.1f"} drinks/hour)
         </td>
      </tr>
      <tr>
         <td valign="top">
            {load_drinker_stats assign="stats" id=$drinker->id}
            {include file="boxes/drinker-quickshot.tpl" drinker=$drinker stats=$stats}
         </td>
      </tr>
   </table>
</div>

{load_binges assign="binges" user_id=$drinker->id}
<div class="contenthead">
   binges
</div>
<div class="content">
   <p>
      a binge constitutes 3 or more drinks, separated by no more than 90
      minutes each, and totalling at least 4 pints
   </p>

   {if !$binges}
   <p>
      <b>none recorded yet.</b> {$drinker->username} is clearly a very balanced
      drinker.
   </p>
   {else}
   <p>
   <div class="box">
   <table class="sortable" id="binges" cellspacing=0 border=0 width="430">
      <tr>
      <td><b>#</b></td>
      <td><b>size</b></td>
      <td><b>start</b></td>
      <td><b>end</b></td>
   </tr>
   {foreach from=$binges item="binge"}
      {if $binge->enddrink_id > $binge->startdrink_id and $binge->volume > 400}
      { include file="spans/binge.tpl" binge=$binge}
      {/if}
   {/foreach}
   </table>
   </div>
   </p>
   {/if}
</div>

{load_drinks assign="drinks" user_id=$drinker->id order_by="id" order_dir="DESC"}
<div class="contenthead">
   full drink history
</div>
<div class="content">
   <p>
      full drink history for { $drinker->username } is shown below.
   </p>
   <p>
   <div class="box">
   <table class="sortable" id="all_drinks" cellspacing=0 border=0 width="430">
      <tr>
         <td>&nbsp;</td>
         <td align="right"><b>size</b></td>
         <td align="right"><b>calories</b></td>
         <td>user</td>
         <td><b>when</b></td>
         <td><b>bac</b></td>
      </tr>
      { foreach name=drinks item="drink" from=$drinks }
         { include file="spans/drink.tpl" drink=$drink } 
      { /foreach }
      </table>
   </div>
   </p>
</div>

