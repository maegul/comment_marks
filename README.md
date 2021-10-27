# Comment Marks

Set bookmarks or section headings simply with comments and a special character.


## Example

In the python code below, two _marks_ or _sections_ are set (`Main` and `Main trigger`) by using `>` characters in comments.

The number of `>` characters defines what level the section has much like hashes for headings in a markdown file.

```python

def my_function():
	retun 'hello world'

# > Main

def main():
	my_function()

# >> Main trigger

if __name__ == '__main__':
	main()
```


## Usage

* Command Palette: `Goto Comment Mark`
* No Key binding set, but go to `Preferences` > `Package Settings` > `Comment Marks` > `Key Bindings`
	* You will see examples on the right and your user key bindings configuration file on the right.  Feel free to copy-paste across.
