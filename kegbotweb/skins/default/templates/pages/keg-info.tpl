{load_keg assign="keg" id=$id}
<div class="contenthead">
   info for keg #{$keg->id}
</div>
<div class="content">
   <p>
   <table cellspacing=3 border=0 width="430">
      <tr>
         <td align="right" valign="top"><b>name:</b></td>
         <td>
            {$keg->description()} ({$keg->abv()|string_format:"%.2f"}% alcohol)
            </td>
         <td rowspan="6" align="right">
            <img src="{module_url module="images" image="keg.png"}" width="77" height="100">
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
         <td align="right"><b>keg size:</b></td>
         <td>{$keg->full_volume|volunits_to_ounces|string_format:"%d"} oz</td>
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
         <td align="right"><b>served:</b></td>
         <td>{$keg->volumeServed()|volunits_to_ounces|string_format:"%.1f"} oz ({$keg->volumeLeft()/$keg->full_volume*100|string_format:"%.1f"}% full)</td>
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
   <div style="float:left">
   <a href="{module_url module="keg-info" keg=$keg->id-1}">&laquo; prev keg</a>
   </div>
   <div style="float:right">
   <a href="{module_url module="keg-info" keg=$keg->id+1}">next keg &raquo;</a>
   </div>
   <br clear="all">
</div>

{load_binge_groups assign=groups keg=$keg}
<div class="contenthead">
   drinking groups
</div>
<div class="content">
   <p>
   {foreach from=$groups item=group}
   {if sizeof($group) <= 1}
   {else}
   <!--
   <div style="float:left; text-align:center; vertical-align:middle;margin:0px;  font:32px serif; padding:5px; background:#aaa; width:50px; height:50px">
      <b>12</b>
   </div>
   -->
   <div class="box">
      <div>
      {$group.0->starttime|rel_date}
      </div>
      {assign var="totvol" value=0}
      {foreach from=$group item=binge}
         {assign var="totvol" value=$totvol+$binge->volume}
         <div style="text-align:center; float:left; padding:5px;">
         {include file="boxes/mugshot-box.tpl" u=$binge->drinker_obj d=50}
         {include file="misc/drinker-link.tpl drinker=$binge->drinker_obj}
         </div>
      {/foreach}
      <div style="text-align:center; vertical-align:middle; float:right;">
         <font size="+5"><b>{$totvol/12|volunits_to_ounces|string_format:"%d"}</b></font><br>
         bottles
      </div>
      <br clear="all">
   </div>
   <br>
   {/if}
   {/foreach}
   </p>
   <div class="spacer">&nbsp;</div>
</div>

<div class="contenthead">
   full drink history
</div>
<div class="content">
   <p>
      full drink history for keg shown below.
   </p>
   {load_drinks assign="drinks" keg_id=$keg->id order_by="id" order_dir="desc"}
   {include file="boxes/drinks.tpl" drinks=$drinks}

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
