<table border="0" cellspacing="7">
<tr>
{foreach name=slots item=pic from=$drinker->getSlots()}
<td>
   <div style="border:1px solid black;width:64;height:64;">
   &nbsp;
   {if $pic.file}
   <img width="64" height="64" src="/userpics/{$pic.url}">
   {/if}
   </div>
   <font size="-2">
   {if $pic.name == ""}
      <i>empty</i>
   { else }
      $pic.name
   {/if }
   </font>
</td>
{/foreach}
</tr>
</table>

