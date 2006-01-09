<div class="contenthead">
   the liquor cabinet
</div>
<div class="content">
   { if $attempted <= 5}
   <p>
      registered drinkers may access all sorts of helpful information by
      logging in below.
   </p>
   { if $oneshot_msg }
   <p>
      {$oneshot_msg}
   </p>
   {/if}
   <p>
      <table>
         <form method="post" action="/login.php">
         <input type="hidden" name="action" value="login">
         <tr>
            <td><b>drinker name:</b></td>
            <td><input type="text" name="login" size="20"></td>
         </tr>
         <tr>
            <td><b>password:</b></td>
            <td><input type="password" name="password" size="20"></td>
         </tr>
         <tr>
            <td>&nbsp;</td>
            <td><input type="submit" name="submit"></td>
         </tr>
         </form>
      </table>
   </p>
   {else}
   <p>
      you have failed your login attempt too many times.
   </p>
   {/if}
</div>

