   <td>{$grant->policy_obj->descr}</td>
   {if $grant->policy_obj->getCostPerOunce() == 0}
      <td>--</td>
   {else}
      <td>{$grant->policy_obj->getCostPerOunce()|money_fmt}/oz</td>
   {/if}
   <td>{$grant->getExpirationStr()}</td>
   <td>{$grant->getToGo()}</td>
