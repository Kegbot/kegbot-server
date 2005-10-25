         <select name="drinker[]" size=5 multiple>
         { foreach from=$drinkers item=drinker}
            <option value="{$drinker->id}">{$drinker->username}</option>
         {/foreach}
         </select>
