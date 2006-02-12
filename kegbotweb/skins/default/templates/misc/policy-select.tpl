      <select name="policy">
      {foreach from=$policies item=i}
         <option value="{$i->id}">{$i->description} ({$i->getCostPerOunce()|money_fmt}/oz)
      {/foreach}
      </select>
