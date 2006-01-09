<div style="text-align:center;">
   <center>
   {include file="boxes/mugshot-box.tpl" u=$leadinfo.drinker d="96" href=$leadinfo.drinker->getLink() border=$border}
   <b>{$leadinfo.drinker->username}</b><br>
   {if $place == 1}
   <font color="#ff0000">top dog!</font><br>
   {elseif $place == 2}
   respectable<br>
   {elseif $place == 3}
   so-so<br>
   {elseif $place == 4}
   improvement needed<br>
   {elseif $place == 5}
   barely notable<br>
   {else}
   position {$place}<br>
   {/if}
   {$leadinfo.amount}{$units}<br>
   &nbsp;<br>
   </center>
</div>

