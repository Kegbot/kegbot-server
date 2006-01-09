<tr bgcolor="{ cycle name="BAC" values="#cc9966,#996600"}">
   <td align="left">
   { $place }
   </td>
   <td>{$BACleader.drinker->getNameLinkified()}</td>
   <td align="right">{$BACleader.bac|string_format:"%.3f"}</td>
</tr>

