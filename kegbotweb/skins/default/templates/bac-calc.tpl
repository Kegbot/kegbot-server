<div class="contenthead">
   blood alcohol content calculator
</div>
<div class="content">
   <p>
      find out how drunk you are! or, test the BAC-calculating abilities of the kegbot.
   </p>
   <p>
      the method used here is based on <a
      href="http://www.nhtsa.dot.gov/people/injury/alcohol/bacreport.html">this</a>
      technique. more BAC information is located <a
      href="http://alcohol.hws.edu/researchlinks/bac.htm">here</a>.
   </p>
   <p>
      <table>
         <form method="post" action="/bac-calculator.php">
         <input type="hidden" name="action" value="add">
         <tr>
            <td><b>gender:</b>
            <td>
               <select name="gender">
               <option value="male">male
               <option value="female">female
            </select>
            </td>
         </tr>
         <tr>
            <td><b>weight:</b></td>
            <td><input type="text" name="weight" size="4"> pounds</td>
         </tr>
         <tr>
            <td><b>size of drink:</b></td>
            <td><input type="text" name="drinksize" size="4"> ounces</td>
         </tr>
         <tr>
            <td><b>percent alcohol:</b></td>
            <td><input type="text" name="alcperence" size="4"> percent</td>
         </tr>
         <tr>
            <td><b>time since consumed:</b></td>
            <td><input type="text" name="drinktime" size="4" value="0"> seconds</td>
         </tr>
         <tr>
            <td>&nbsp;</td>
            <td><input type="submit" name="submit"></td>
         </tr>
         </form>
      </table>
   </p>
</div>

