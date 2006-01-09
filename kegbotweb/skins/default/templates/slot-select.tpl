{foreach name=slots item=slot from=$drinker->getSlots()}
   <option value="{$slot.pos}">{$slot.pos}: {if $slot.name == ""}empty{else}{$slot.name}{/if}
{/foreach}
