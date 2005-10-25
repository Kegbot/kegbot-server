         {if $drinker->bio}
            <p>
            </p>
            {/if}
            <div class="plainboxhead" style="width:280px;">
               <b>drinks: quick shot</b>
            </div>
            <div class="plainbox" style="width:280px;">
               <table border=0>
                  <tr>
                     <td align="right" valign="top"><b>career:&nbsp;</b></td>
                     <td colspan="1" align="left">
                        {$stats.alltime_vol|string_format:"%.2f"} oz{if $stats.alltime_cals > 0},
                        {$stats.alltime_cals|string_format:"%d"} calories{/if}<br>
                        = {$stats.alltime_vol/12.0|string_format:"%.1f"} bottles<br>
                        = {$stats.alltime_vol/16.0|string_format:"%.1f"} pints
                        {if $stats.alltime_vol/128 >= 1}
                        <br>= {$stats.alltime_vol/128.0|string_format:"%.1f"} gallons!
                        {/if}
                        {if $stats.alltime_vol/1984.0 >= 0.5}
                        <br>= {$stats.alltime_vol/1984.0|string_format:"%.1f"} keg!!
                        {/if}
                     </td>
                  </tr>
                  {if $stats.last24 > 0}
                  <tr>
                     <td align="right" valign="top"><b>in past 24hrs:</b></td>
                     <td>{$last24|string_format:"%.1f"}</td>
                  </tr>
                  {/if}
                  {if $currentbac > 0}
                  <tr>
                     <td align="right" valign="top"><b>current bac:</b></td>
                     <td>{$currentbac|string_format:"%.3f"}</td>
                  </tr>
                  {/if}
                  {if $stats.alltime_bac > 0.001}
                  <tr>
                     <td align="right" valign="top"><b>highest BAC:</b></td>
                     <td colspan="1" align="left">{$stats.alltime_bac|string_format:"%.3f"}%</td>
                  </tr>
                  {/if}
               </table>
            </div>

