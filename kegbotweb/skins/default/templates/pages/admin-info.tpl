<div class="contenthead">
   edit user
</div>
<div class="content">
   <form action="edit-user.php">
   <p>
         <select name="u">
         { foreach from=$drinkers item=drinker}
            <option value="{$drinker->id}">{$drinker->username}</option>
         {/foreach}
         </select>
         <input type="submit" name="edit" value="edit">
   </p>
   </form>
</div>

<div class="contenthead">
   grant a policy
</div>
<div class="content">
   <form action="grant-policy.php" method="post">
   <p>
      <table border="0">
      <tr>
      <td rowspan="2" valign="top"><input type="submit" name="action" value="grant"></td>
      <td valign="top">
         {include file="misc/policy-select.tpl"}
      </td>
      <td valign="top">to user(s)</td>
      <td valign="top">
         {include file="boxes/multi-drinker-select.tpl"}
      </td>
      </tr>
      <tr>
      <td valign="top" colspan="3">
         <input type="radio" name="exptype" value="none" checked> expires never<br>
         <input type="radio" name="exptype" value="volume" > expires after <input type="text" name="expounces" size="3" value="64"> ounces<br>
         <input type="radio" name="exptype" value="time" > expires on date <input type="text" name="expdate" size="16">
      </td>
      </tr>
      </table>
   </p>
   </form>
</div>

<div class="contenthead">
   site tokens
</div>
<div class="content">
   <p>
      all tokens are listed below. click on a token id to edit it or see the
      token history.
   </p>
   <p>
      <div class="box">
      <table border="0" cellspacing="0">
      <tr>
         <td><b>keyinfo</b></td>
         <td><b>owner</b></td>
         <td><b>created</b></td>
      </tr>
      {foreach from=$tokens item=token}
         {include file="spans/token.tpl" token=$token}
      {/foreach}
      </table>
      </div>
   </p>
</div>

<div class="contenthead">
   site policies
</div>
<div class="content">
   <p>
      all known policies are shown below.
   </p>
   <p>
      {include file="misc/policy-select.tpl" policies=$policies}
      <input type="submit" name="action" value="edit">
      <input type="submit" name="action" value="delete">
      <input type="submit" name="action" value="show grants">
   </p>
   <p>
      or, you may add a new policy to the system below.
   </p>

   <form action="new-policy.php" method="post">
   <p>
   <table>
   <tr>
      <td align="right"><b>description:</b></td>
      <td><input type="text" name="descr" size="35"></td>
   </tr>
   <tr>
      <td align="right" valign="top"><b>unit ounces:</b></td>
      <td>
         <input type="text" name="unitounces" size="8" value="1.0">
      </td>
   </tr>

   <tr>
      <td align="right" valign="top"><b>price/unit:</b></td>
      <td>
         <input type="text" name="unitcost" size="8" value="0.05">
      </td>
   </tr>

   <tr>
      <td>&nbsp;</td>
      <td><input type="submit" name="action" value="create"></td>
   </tr>

   </table>
   </p>
   </form>
</div>

<div class="contenthead">
   new drinker
</div>
<div class="content">
   <p>
      add a new drinker!
   </p>
   <form action="add-drinker.php" method="post">
   <p>
   <table>
      <tr>
         <td align="right" valign="top"><b>drinker name:</b></td>
         <td><input type="text" name="username" size="35"></td>
      </tr>
      <tr>
         <td align="right" valign="top"><b>password:</b></td>
         <td><input type="password" name="password" size="35"></td>
      </tr>
      <tr>
         <td align="right" valign="top"><b>password (again):</b></td>
         <td><input type="password" name="confirm" size="35"></td>
      </tr>
      <tr>
         <td align="right" valign="top"><b>gender:</b></td>
         <td><input type="radio" name="gender" value="male" checked>male<br><input type="radio" name="gender" value="female">female</td>
      </tr>
      <tr>
         <td align="right" valign="top"><b>weight:</b></td>
         <td><input type="text" name="weight" size="35" value="175"></td>
      </tr>
   </table>
   </form>
</div>


