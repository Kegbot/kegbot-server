<p>
   <div class="box">
   <table class="sortable" id="drinks" cellspacing=0 border=0 width="430">
   <tr>
      <td><b>#</b></td><td align="right"><b>size</b></td><td>&nbsp;</td><td><b>user</b></td><td><b>when</b></td>
   </tr>
   {assign var="last_date" value=0}
   { foreach name=drinks item="drink" from=$drinks }
      {if $last_date != 0 && $last_date > ($drink->endtime + 60*60*3)}
      <tr><td colspan=4>&nbsp;</td></tr>
      {/if}
      {include file="spans/drink.tpl" drink=$drink}
      {assign var="last_date" value=$drink->endtime}
   { /foreach }
   </table>
   </div>
</p>
