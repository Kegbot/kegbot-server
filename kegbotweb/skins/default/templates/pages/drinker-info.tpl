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
            {include file="boxes/drinker-quickshot.tpl"}
         </td>
      </tr>
   </table>
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
      <table cellspacing=0 border=0 width="430">
      <tr>
         <td><b>#</b></td>
         <td align="right"><b>size</b></td>
         <td>&nbsp;</td>
         <td><b>user</b></td>
         <td><b>when</b></td>
         <td><b>bac</b></td>
      </tr>
      { foreach name=drinks item="drink" from=$drinks }
         { include file="spans/drink.tpl" drink=$drink } 
      { /foreach }
      </table>
   </p>
</div>

