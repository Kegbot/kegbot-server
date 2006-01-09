      <select name="policy">
      {foreach from=$policies item=i}
         <option value="{$i->id}">{$i->descr} ({$i->printCost()})
      {/foreach}
      </select>
