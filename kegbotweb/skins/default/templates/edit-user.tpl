<div class="contenthead">
   master user control
</div>
<div class="content">
   <p>
      <table border="0" cellspacing="5" cellpadding="5">
         <form method="get" action="user-control.php">
         <input type="hidden" name="targetuser" value="{$drinker->id}">
         <tr>
            <td align="right" valign="top">
               <input type="submit" name="action" value="delete">
            </td>
            <td>
               permanently remove <b>{$drinker->username}</b> from the system. (drink logs for this drinker will be saved.)</td>
         </tr>
          <tr>
            <td align="right" valign="top">
               <input type="submit" name="action" value="squelch">
            </td>
            <td>
               keep <b>{$drinker->username}</b> from being able to drink beer, make any account changes, or do anything useful. aka "collections department".
            </td>
         </tr>
         </form>
      </table>
   </p>
</div>

<div class="contenthead">
   edit grants
</div>
<div class="content">
   <p>
      summary of grants for <b>{$drinker->username}</b>:
   </p>
   <p>
      <table cellspacing=0 border=0 width="440">
      <tr>
         <td><b>action</b></td>
         <td><b>description</b></td>
         <td><b>cost/oz</b></td>
         <td><b>expires</b></td>
         <td><b>to go</b></td>
      </tr>
      {foreach name=grants item="grant" from=$grants}
         <tr>
         <td><a href="edit-grant.php?targetgrant={$grant->id}&action=edit">edit</a>/<a href="delete-grant.php?g={$grant->id}&u={$drinker->id}">kill</a>&nbsp;</td>
         { include file="grant-span.tpl" grant=$grant}
         </tr>
      {/foreach}
      </table>
   </p>
</div>


