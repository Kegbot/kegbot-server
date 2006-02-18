{load_drink assign="drink" id=$getvars.drink}
<div class="contenthead">
   drink information
</div>
<div class="content">
   <p>
   <table cellspacing=3 border=0 width="430">
      <tr>
         <td colspan="2" align="center">
            <i>drink number {$drink->id}, consumed by {include file="misc/drinker-link.tpl" drinker=$drink->drinker_obj}</i>
         </td>
         <td rowspan="7" align="right" valign="top">
            <img src="{module_url module="images" image="beerpint.png"}" width="50" height="94">
         </td>
      </tr>
      <tr>
         <td align="right"><b>drink size:</b></td>
         <td>{$drink->getSize()|string_format:"%.2f"} ounces</td>
      </tr>
      <tr>
         <td align="right"><b>pour start:</b></td>
         <td>{$drink->starttime|date_format:"%b %e %Y, %H:%M:%S"}</td>
      </tr>
      <!-- TODO FIXME
      <tr>
         <td align="right"><b>cost:</b></td>
         <td>{$drink->getCost()|money_fmt}</td>
      </tr>
      -->
      <tr>
         <td align="right"><b>pour end:</b></td>
         <td>{$drink->endtime|date_format:"%b %e %Y, %H:%M:%S"}</td>
      </tr>
      <tr>
         <td align="right"><b>keg:</b></td>
         <td>{include file="misc/keg-link.tpl" keg=$drink->keg_obj}</td>
      </tr>
      <tr>
         {assign var="binge" value=$drink->getBinge()}
         <td align="right"><b>binge:</b></td>
         <td>{$binge->id}</td>
      </tr>
   </table>
   </p>
</div>

{load_nearby_drinkers assign="friends" drink=$drink}
<div class="contenthead">
   drinking with {$drink->drinker_obj->username}
</div>
<div class="content">
   <p>
   {if !$friends}
   <b>{$drink->drinker_obj->username}</b> appeared to be drinking alone.
   {else}
   <div class="box">
      {foreach from=$friends item=friend}
         <div style="text-align:center; float:left; padding:5px;">
         {include file="boxes/mugshot-box.tpl" u=$friend d=50}
         {include file="misc/drinker-link.tpl drinker=$friend}<br>
         </div>
      {/foreach}
      <br clear="all">
   </div>
   <div class="spacer">&nbsp;</div>
   </p>
   {/if}
</div>
