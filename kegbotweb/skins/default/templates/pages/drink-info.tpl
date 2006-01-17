{load_drink assign="drink" id=$getvars.drink}
<div class="contenthead">
   drink information
</div>
<div class="content">
   <p>
   <table cellspacing=3 border=0 width="430">
      <tr>
         <td colspan="2" align="center">
            <i>drink number {$drink->id}, consumed by {include file="misc/drinker-link.tpl" drinker=$drink->drinker_obj}</i>
         </td>
         <td rowspan="7" align="right" valign="top">
            <img src="{module_url module="images" image="beerpint.png"}" width="50" height="94">
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
      <!-- TODO FIXME
      <tr>
         <td align="right"><b>cost:</b></td>
         <td>{$drink->getCost()|money_fmt}</td>
      </tr>
      -->
      <tr>
         <td align="right"><b>pour end:</b></td>
         <td>{$drink->endtime|date_format:"%b %e %Y, %H:%M:%S"}</td>
      </tr>
      <tr>
         <td align="right"><b>keg:</b></td>
         <td>{include file="misc/keg-link.tpl" keg=$drink->keg_obj}</td>
      </tr>
   </table>
   </p>
</div>

