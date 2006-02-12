<tr>
   <td>{$policy->id}&nbsp;&nbsp;&nbsp;</td>
   <td>{$policy->description}&nbsp;&nbsp;&nbsp;</td>
   {if $policy->getCostPerOunce() == 0}
      <td>--&nbsp;&nbsp;&nbsp;</td>
   {else}
      <td>{$policy->getCostPerOunce()}&cent;&nbsp;&nbsp;&nbsp;</td>
   {/if}
</tr>
