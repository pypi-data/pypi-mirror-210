# python-as3toplevel
A python implementation of some of the ActionScript3 toplevel functions and classes. They are as close as I could get them with my knowledge and the very limited documentation that adobe provides.
<br><br>The types (Array, Boolean, Number, and String) are actual types so you can use them as such. They include almost everything that they did in ActionScript3. The length method in each type can only be used to get the length, I didn't implement the length assignment for Arrays.
<br><br>Most of the inherited properties would be too hard to implement so I didn't bother with them.
<br><br>I implemented the type conversion functions inside the types themselves (ex: instead of String(expression) use String.String(expression)).
<br><br>For functions that needed a placeholder value for input(s) that aren't easily definable, could be multiple types, or relied on other factors to be set I use an empty dictionary as a placeholder. The values that these empty dictionaries represent aren't actually dictionaries, I just used something that would never be used in these functions so that I could detect it.
