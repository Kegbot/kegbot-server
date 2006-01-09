   <td>{$grant->policy->descr}</td>
   {if $grant->policy->getCostPerOunce() == 0}
      <td>--</td>
   {else}
      <td>{$grant->policy->getCostPerOunce()}&cent;</td>
   {/if}
   <td>{$grant->getExpirationStr()}</td>
   <td>{$grant->getToGo()}</td>
