   <td>{$grant->policy_obj->description}</td>
   {if $grant->policy_obj->getCostPerOunce() == 0}
      <td>--</td>
   {else}
      <td>{$grant->policy_obj->getCostPerOunce()|money_fmt}/oz</td>
   {/if}
   <td>{$grant->getExpirationStr()}</td>
   <td>{$grant->getToGo()}</td>
