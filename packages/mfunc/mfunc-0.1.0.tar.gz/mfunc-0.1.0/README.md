# `mfunc`
This library was made so that you can get a list of points of a function by list slicing.
## How to Use
First, put `from mfunc import mfunc` at the top of your code.
Then, if you have already defined a function `f(x)`, you can initiate an instance of an `mfunc` by assigning `mfunc(f)` to a variable. Due to the behaviour of importing, you may need to do `mfunc.mfunc()` instead.
## Supported Features
Here is the list of supported features for an `mfunc`:<br><br>
* Item retrieval and slicing (e.g. `mfunc(lambda x:x)[:5]` returns the values of the function from 0 to 4).<br>

* The arithmetic operators `+ - * / // **`<br>

* A string representation (returns actual function).
## Bugs
If you hae discovered a bug or have an idea, post it [here](https://github.com/PlaceReporter99/mfunc-bug-tracker/issues).