# Comment Marks

**Set bookmarks or section headings simply with comments and a special character.**

_Will probably require sublime restart after installation_

_Comment Marks_ are highlighted below (using Sublime Text Find) in a piece of example code

![example code](./misc/code_example_shot.png "Optional title")

---

Running the `Goto Comment Mark` Command (see [Usage](#usage) below) will provide the searchable quickpanel seen below which will take you to the selected comment.

![Quick Panel Search](./misc/quick_panel_shot.png "Optional title")

## Example

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


In the python code above, two _marks_ or _sections_ are set (`Main` and `Main trigger`) by using `>` characters in comments.

The number of `>` characters defines what level the section has much like hashes for headings in a markdown file.

## Usage

* **Command Palette**: `Goto Comment Mark`
* No **Key binding** is set by default. 
    * To set user key bindings, go to the `Sublime Text` menu, then `Preferences` > `Package Settings` > `Comment Marks` > `Key Bindings`
	* You will see examples on the left and your user key bindings configuration file on the right.  Feel free to copy-paste across.

### Trailing Comment Characters

* Some syntaxes (eg `C` or `HTML`) use delimiting characters for comments rather than using a single character or symbol and line endings.
    - eg `/* A comment in C */`.  Here, the `*/` in the end is what is meant by "trailing comment characters".
* By default, `Comment Marks` includes the trailing comment characters as being part of the Comment Mark presents them in the command palette.
* _Alternatively_, the trailing comment marks can be trimmed out.
* _To enable this_, alter the setting `trim_trailing_comment_chars` value to `true` (it's default is false).  See [configuration](#configuration) below.
    - The trailing characters that are trimmed by default, and for specific scopes, are configurable also.

## Design

Aims:

* Provide a simple but effective and flexible approach to creating, searching and navigating to arbitrary "bookmarks" in a file.
* Make the process easy, lightweight and essentially editor independent.
* Use a plugin that is simple but configurable and _hopefully_ performant.

This plugin is similar to `Table of comments` ([see Page on Package Control](https://packagecontrol.io/packages/Table%20of%20comments)).

**Differences**:

* Simpler functionality and code base (_hopefully so that it is more easily hacked by users_)
	- Uses `python 3.8`, and is therefore compatible only with `Sublime Text v4`
* More configurable (_I think_)
* Faster (_in my experience_)
	- Specifically, I'm referring to the time from running the `Goto Comment Mark` command and seeing the quick panel of "bookmarks" (and the equivalent in `Table of comments`).
	- If this plugin is faster, it's probably due to these reasons:
		+ regex paterns are prepared on plugin load, not when the commands are run
		+ plugin is relatively minimal
		+ uses `python 3.8` and `f-strings`, which may provide noticeable performance gains.


## Configuration

* Go to `Preferences` > `Package Settings` > `Comment Marks` > `Settings`, which will open the default settings on the left your custom settings on the right.
    - Extensive comments in the settings `json` file should provide sufficient guidance.

_Current default settings:_

```javascript
{
    // Restarting Sublime will probably be necessary for settings to take effect
    // The command "Comment Marks: Reload Settings" (run from the command palette)
    // should apply any changes to the settings without needing to restart.
    // If that does not work, restarting will be a more reliable means of doing so.

    // > look ... there are Comment Marks in here :)

    // > Basic Visual Settings

    // Character to use in comments for creating Comment Marks
    // Use repeats of this character to create Comment Marks of increasingly "lower levels"
    // like in markdown
    "default_level_char": ">",

    // Control the formatting of Comment Marks in the Command Palette
    // Numeric keys signify what level of Comment Mark the formatting applies to, or
    // more specifically, the number of "default_level_char" characters
    // that have been repeated.
    // The string value is what will replace the level_chars in the quick panel ...
    // ... note the spaces which create indentation in the Command Palette.
    "level_char_format_sub": {
        "1": "",
        "2": "  - ",
        "3": "   -- ",
        "4": "    -- ",
        "5": "     -- ",
        "6": "      -- ",
    },

    // >> Scope specific comment mark character (like level_char above)

    // Custom level char for specific scopes, if you want to use a different
    // character in particular scopes (so it looks better or clearer, for instance).
    // To find the scope of a file, hit CTRL+SHIFT+P, and see the top line, or
    // in control panel, run `view.syntax().scope`
    "level_chars": {
        // "source.python": ">",
        // "source.c": ">"
    },

    // >> Trimming trailing comments (for languages like CSS, HTML, C)

    // Whether to trim the trailing characters of a comment (such as */ in CSS)
    // Default is false, as somewhat experimental.
    // Feel tree to turn on, but if there are problems with this, you can turn it off
    "trim_trailing_comment_chars": true,

    // What trailing characters to trim for specific scopes/syntaxes (such as */ in CSS).
    // These are searched for at the end of every comment mark and stripped if found.
    // Default characters are defined in another setting below.
    // SO YOU DO NOT NEED TO TOUCH THIS SETTING.
    // But if a specific syntax isn't covered by the default settings,
    // you can provide the specific trailing characters below for the specific syntax/scope.
    // To find the scope of a file, hit CTRL+SHIFT+P, and see the top line, or
    // in the control panel, run `view.syntax().scope`.
    // You must provide a list of strings, even if providing only a single string.
    "scope_comment_trailing_chars": {
        // "source.css": ["*/"]
    },

    // Default characters used as a fallback when no scope-specific characters
    // are defined above.
    // Each one is searched, one after the other, using a regex OR operator ("|")
    // Relying on these is the intended behaviour, YOU DO NOT NEED TO PROVIDE
    // SCOPE-SPECIFIC CHARACTERS ABOVE.
    // Feel free to adjust or augment this list as you see fit, though you
    // might alter the behaviour of the plugin by doing so.
    // Must provide a list of strings, even if only one string.
    "default_scope_comment_trailing_chars": ["*/", "-->"],


    // > Customising the detection of comments

    // >> Introduction (rant)

    // The plubin finds Comment Marks as follows:
        // 1. Uses regex patterns that ...
        // 2. Search for lines that start with some combination of whitespace and comment
        //      characters
        // 3. And also generally search for multiple alternative comment characters
        // 4. Then, the pattern searches for the level character defined here (eg, ">")
        // 5. And finally everything that follows (ie, the "heading" you've written)

    // As programming languages have different syntaxes for comments, this plugin's
    // default settings define multiple comment characters which are searched as alternatives.
    // This works well most of the time, but maybe something is off for a particular syntax
    // or you use it in a particular way.
    // The settings below allow you to manipulate what characters are searched for
    // within files of a particular syntax/scope.
    // These characters will then be placed into a larger regex pattern
    // (to take care of whitespace) etc.
    // If you want, with "custom_comment_start_patterns", you can set the full regex for
    // what defines a comment line in a particular syntax/scope,
    // where the plugin will add the rest of the needed regex
    // for searching for the headings of the comment marks and the level characters (">") etc.

    // >> Defining comment characters

    // If the default list of comment characters doesn't cover a syntax that
    // you're working with (or there's a bug), you can specify the comment character
    // for a particular syntax or scope directly here.
    // These comment characters are put together into a larger pattern that
    // presumes these characters can occur 1 or more times (using regex `+`) ...
    // ... see the `source.python` example in custom_comment_start_patterns
    // below for what this pattern looks like for python.
    // When a file's scope is not here, default characters (defined below) are used instead
    // where the first character/sequence found is used.
    // Must provide a list of strings, even if only one string.
    "scope_comment_chars": {
        "source.python": ["#"],
        "source.json.sublime.keymap": ["/"]
    },

    // Default characters used as the fallback when no scope-specific characters
    // are defined above.
    // There is no need to specify scope-specific characters, relying on these
    // default characters is the intended functionality of the plugin.
    // You really shouldn't need to alter these, but just in case, you can.
    // Doing so may break the plugin though!
    // Must provide a list of strings, even if only one string.
    "default_scope_comment_chars": ["#", "/", "/*", "%", "<!--", "-"],


    // >> Comment regex pattern override

    // Provide specific regex patterns for detecting comments for specific scopes.
    // REQUIRES KNOWING REGEX.
    // These patterns will COMPLETELY OVERRIDE those automatically generated from
    // the characters in scope_comment_chars.
    // This setting is available if it's necessary to rectify the default behaviour
    // either because of a bug, a special need, or a syntax that has not been accounted for.
    // Also, it will result in a simpler regex pattern for any scope provided for, which
    // could be somewhat more performant (though probably not noticeably).
    // A valid example for python is provided for demonstration.
    // Must provide a list of strings, even if only one string.

    // WARNING ... these patterns are not interpretted as python raw strings, so to use the
    // the backslash character ("\") in regex, you'll have to escape it with the python
    // escape character, which is the same ("\").
    // EG, to match an asterisk with regex requires escaping it ("\*") as the asterisk
    // is an operator in regex.  BUT, because python interprets the backslash as an escape
    // character, it also needs to be escaped ("\\") resulting in "\\*" to match an asterisk.
    // Absurdly, to match a backslash in regex requires "\\", ie an escaped escape chararacter,
    // and to do it here with a python string requires escaping both of those backslashes,
    // ie "\\\\".

    "custom_comment_start_patterns": {
        "source.python": ["^[ \t]*#+"]
    },

}
```

## Changelog


### 0.1.11

* Filter out trailing comment characters (such as in `CSS`) from Command Palette items
    - Done only for displaying in the command palette.
    - Made optional with current default of being off (false).
* Reorganise settings into a more logical order
* Make workings of settings more "modular"
    - separate defaults from scope-specific settings
    - allow scope specific level character and comment character settings to be orthogonal to each other.  Any scope-specific setting for either parameter (level char or comment char) when there is no setting for the other for the same scope, will simply take the default.
