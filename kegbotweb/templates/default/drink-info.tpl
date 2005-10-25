<div class="contenthead">
   drink information
</div>
<div class="content">
   <p>
   <table cellspacing=3 border=0 width="430">
      <tr>
         <td colspan="2" align="center">
            <i>drink number {$drink->id}, consumed by {$drink->drinker_obj->getNameLinkified()}</i>
         </td>
         <td rowspan="7" align="right" valign="top">
            <img src="/images/beerpint.png" width="50" height="94">
         </td>
      </tr>
      <tr>
         <td align="right"><b>drink size:</b></td>
         <td>{$drink->getSize()|string_format:"%.2f"} ounces</td>
      </tr>
      <tr>
         <td align="right"><b>pour start:</b></td>
         <td>{$drink->starttime|date_format:"%b %e %Y, %H:%M:%S"}</td>
      </tr>
      <tr>
         <td align="right"><b>cost:</b></td>
         <td>{$drink->getCost()|money_fmt}</td>
      </tr>
      <tr>
         <td align="right"><b>pour end:</b></td>
         <td>{$drink->endtime|date_format:"%b %e %Y, %H:%M:%S"}</td>
      </tr>
      <tr>
         <td align="right"><b>keg:</b></td>
         <td>{$drink->keg_obj->getDescrLinkified()}</td>
      </tr>
   </table>
   </p>
</div>

<!--
<div class="contenthead">
   statistics
</div>
<div class="content">
   <p>
      <ul>
         <li>This was drink number
             <b>{$kegdrinknum}</b> for this keg,
             <b>{$drinknum}</b> for {$drink->drinker_obj->getNameLinkified()}, and
             <b>{$totalnum}</b> overall.

         <li>On average, drinks of this size take <b>{$time_avg|string_format:"%.1f"} seconds</b> to pour, so
         this drink was poured 
         {if $diff_pos == 0}
            remarkably well
         {elseif $diff_pos > 0}
            <b>{$diff_pos|string_format:"%.1f"}</b> seconds faster than expected
         {else}
            <b>{$diff_neg|string_format:"%.1f"}</b> seconds slower than expected
         {/if}

         <li>{$drink->drinker_obj->getNameLinkified()} usually pours a drink
         <b>{$hist_avg|string_format:"%.2f"} ounces</b> in size, so this drink was
         {if abs($hist_avg - $size) <= 1}
            <b>spot on</b>
         {elseif ($hist_avg > $size)}
            <b>a disappointment</b>
         {else}
            <b>a step up</b>
         {/if}
      </ul>
   </p>
</div>

-->
