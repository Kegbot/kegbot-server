<tr bgcolor="{ cycle name="vol" values="#cc9966"}">
   <td>{$place}</td>
   <td align="left">
   { $volleader.drinker->getNameLinkified() }
   </td>
   <td align="right">{$volleader.ounces|string_format:"%.1f"}</td>
</tr>
