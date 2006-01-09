<div class="leftbox" style="background:#003; font:12px Courier, sans-serif; text-align: center;color: #fff; border:1px solid #fff; border-top:0px;">
current keg
</div>
{foreach name=curr_vol from=$g_current_vol item=resinfo}
   <div class="leftbox" style="font:10px Courier, sans-serif;">
   <center>
   {include file="boxes/mugshot-box.tpl" u=$resinfo.drinker d=100 border=0 href=$resinfo.drinker->getLink()}
   {$resinfo.amount}{$resinfo.units}
   </center>
   </div>

{/foreach}
