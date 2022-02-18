import re
from functools import partial

import sublime
import sublime_plugin

SETTINGS_NAME = 'comment_marks.sublime-settings'

# > Config and Settings

def get_config():
    "Extract settings and construct all relevant parameters and declar necessary global constants"

    SETTINGS = sublime.load_settings(SETTINGS_NAME)
    # print('Comment Marks Settings -- ', SETTINGS.to_dict())

    SCOPE_COMMENT_CHARS = SETTINGS.get('scope_comment_chars', {})
    # take default from settings
    SCOPE_COMMENT_CHARS['default'] = SETTINGS.get('default_scope_comment_chars')

    COMMENT_START_PATTERNS = {
        scope: [
            # allow duplicates of last character only
            # relies on python trick where slicing beyond len of string/list
            # is ok ... just empty string/list returned
            rf'^[ \t]*{re.escape(c[0])}{re.escape(c[1:])}+'
            for c in chars
            ]
        for scope, chars
        in SCOPE_COMMENT_CHARS.items()
    }

    CUSTOM_COMMENT_START_PATTERNS = SETTINGS.get('custom_comment_start_patterns')
    # print('custom start patterns', CUSTOM_COMMENT_START_PATTERNS)

    # add custom to all
    # >> !! How deal with escape characters!
    # Rely on user using escaping backslashes (eg, "\\*" instead of "\*")
    COMMENT_START_PATTERNS.update(CUSTOM_COMMENT_START_PATTERNS)

    # > Compiling into complete patterns
    COMMENT_PATTERNS = {
        scope: r'|'.join([p for p in patterns ])
        for scope, patterns
        in COMMENT_START_PATTERNS.items()
    }

    # >> Trailing Characters

    SCOPE_COMMENT_TRAILING_CHARS = SETTINGS.get('scope_comment_trailing_chars', {})
    SCOPE_COMMENT_TRAILING_CHARS['default'] = SETTINGS.get('default_scope_comment_trailing_chars')
    COMMENT_TRAILING_PATTERNS = {
        scope: [
            # Add whitespace, end of line and "+" operator to trailing chars
            # big choice here!  Only duplicates of the first character are allowed
            # seems to be the common behaviour, but by no means for certain
            # >>> !! NEED TO ALLOW USER DEFINED CUSTOM TRAILING PATTERN
            # 1 leading spaces before trailing comment characters
            # 2 at least one, but also multiple of the first character
            # 3 the rest of the characters, if any, and just once
            # 4 trailing spaces up to the end of the line
            #  1  ------ 2 ------          3         4
            rf' *{re.escape(c[0])}+{re.escape(c[1:])} *$'
            for c in chars
        ]
        for scope, chars
        in SCOPE_COMMENT_TRAILING_CHARS.items()
    }

    global TRAILING_PATTERNS
    TRAILING_PATTERNS = {
        # 1 lazily capture whole comment mark as much as possible.
        #   using wildcard allows whole comment mark to be captured
        #   when no trailing comment characters are present at the end.
        #   laziness necesary to separate the two groups though!!!
        # 2 alternative tails for when multiple defined in settings
        # 3 NULL alternative, works with lazy wild card at start
        #   and is pivotal ... allows for no trailing comment chars
        #   by allowing the wild card to capture the whole string
        #   with the second group matching nothing by the end
        #   of the string.  POTENTIALLY DANGEROUS AND BAD??
        #           1     2                               3
        scope: rf"(.*?)({'|'.join([p for p in patterns])}|$)"
        for scope, patterns
        in COMMENT_TRAILING_PATTERNS.items()
    }

    # > Level Characters

    LEVEL_CHARS = SETTINGS.get('level_chars', {})
    DEFAULT_LEVEL_CHAR = SETTINGS.get('default_level_char')
    LEVEL_CHARS['default'] = DEFAULT_LEVEL_CHAR

    LEVEL_CHAR_FORMAT_SUB = SETTINGS.get('level_char_format_sub')

    # convert string "1", "2", ... to integers (sigh)
    LEVEL_CHAR_FORMAT_SUB = {
        int(n): sub
        for n, sub in LEVEL_CHAR_FORMAT_SUB.items()
    }

    global LEVEL_CHAR_FORMAT_SUB_PATTERNS
    LEVEL_CHAR_FORMAT_SUB_PATTERNS = {
        scope: {
            # default back to default lvl char, so long as comment_start_pattern is set
            (n*level_char): sub
            for n, sub in LEVEL_CHAR_FORMAT_SUB.items()
        }
        for scope, level_char in LEVEL_CHARS.items()
    }
    # LEVEL_CHAR_FORMAT_SUB_PATTERNS = {
    #     scope: {
    #         # default back to default lvl char, so long as comment_start_pattern is set
    #         (n*LEVEL_CHARS.get(scope, DEFAULT_LEVEL_CHAR)): sub
    #         for n, sub in LEVEL_CHAR_FORMAT_SUB.items()
    #     }
    #     for scope in COMMENT_START_PATTERNS
    # }

    # > Full Patterns

    # all specific scopes in level_chars and comment_chars
    # so that any specification gets represented here, even if not defined
    # in both level_chars and comment_chars.
    # When not defined forboth, fallback to default
    # this means scope specific level_chars and comment_chars are work
    # independently of each other
    all_scopes = set().union(COMMENT_PATTERNS, LEVEL_CHARS)
    # prepare defaults
    default_comment_pattern = COMMENT_PATTERNS['default']
    default_level_char = LEVEL_CHARS['default']

    global LEVEL_PATTERNS
    LEVEL_PATTERNS = {
        scope: (
            # parentheses around pattern important, breaks | off from rest of pattern
            # ie, OR is not greedy
            rf'({COMMENT_PATTERNS.get(scope, default_comment_pattern)})[ ]*({re.escape(LEVEL_CHARS.get(scope, default_level_char))}+)\s*(.+)'
            )
        for scope
        in all_scopes
    }
    # LEVEL_PATTERNS = {
    #     scope: (
    #         # parentheses around pattern important, breaks | off from rest of pattern
    #         # ie, OR is not greedy
    #         # > !!! Match for trailing here??
    #         rf'({pattern})[ ]*({re.escape(LEVEL_CHARS.get(scope, DEFAULT_LEVEL_CHAR))}+)\s*(.+)'
    #         )
    #     for scope, pattern
    #     in COMMENT_PATTERNS.items()
    # }

    # >> Print out to console
    print('Comment Marks -- Full Patterns Spec:')
    for scope, pattern in LEVEL_PATTERNS.items():
        print(f'\t{scope}: {pattern}')
    print('Trailing patterns:')
    for scope, pattern in TRAILING_PATTERNS.items():
        print(f'\t{scope}: {pattern}')
    print('Level characters and list formatting')
    for scope, subs in LEVEL_CHAR_FORMAT_SUB_PATTERNS.items():
        print(scope, subs)

    global EXTRACTION_SEP
    EXTRACTION_SEP = r'|:!:|'


# >> Load config when plugin loaded
def plugin_loaded():
    get_config()

class ReloadCommentMarkSettingsCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        get_config()

# > Goto Comment Command

class GotoCommentCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        # get_config()

        self._current_cursor_loc = self.view.sel()[0]
        # print('goto comment')

        sections = self.get_section_regions_matches()
        if sections:
            sections = self.update_with_formatted_matches(sections)
            # print(sections)
            self.panel(sections)

    def get_section_regions_matches(self):

        pattern = None
        syntax = self.view.syntax()
        scope = (
            syntax.scope
            if syntax and (syntax.scope in LEVEL_PATTERNS)
            else 'default'
            )
        pattern = LEVEL_PATTERNS[scope]
        # print(pattern)

        section_matches = []
        section_regions = self.view.find_all(
            pattern,
            fmt=rf'\2{EXTRACTION_SEP}\3',
            extractions=section_matches)

        sections = {
            'scope': scope,
            # why note just concretise here!?
            # use python3 they said ... everything's a generator they said!
            # >> !! Should probably be a list of dictionaries rather than tuples for semantic access
            'sections': list(zip(section_regions, section_matches))
        }

        return sections

    def get_lvl_match(self, section):
        match = section[1]  # index 1 as each section is [(REGION, MATCHED_TEXT)]
        lvl, section_text = match.split(EXTRACTION_SEP)

        return lvl, section_text

    def strip_trailing_comments(self, section_text, trailing_re):

        # >> strip trailing chars
        stripped_section_match = trailing_re.match(section_text)
        # if no match, fallback to just the original section text
        if stripped_section_match:
            stripped_section_text = stripped_section_match.group(1)
        else:
            stripped_section_text = section_text

        return stripped_section_text

    def format_match_for_list(self, format_sub_patterns, lvl, text):

        formatted_match = f'{format_sub_patterns.get(lvl, lvl)}{text}'

        return formatted_match

    def strip_trailing_chars(self):

        strip_trailing_chars = (
            sublime.load_settings(SETTINGS_NAME)
            .get('trim_trailing_comment_chars', True)
            )

        return strip_trailing_chars

    def update_with_formatted_matches(self, sections):

        if LEVEL_CHAR_FORMAT_SUB_PATTERNS:  # if none, don't do this
            scope = sections['scope']
            # should be available by this point,
            # as it means that scope is available in level_chars
            if scope in LEVEL_CHAR_FORMAT_SUB_PATTERNS:
                format_sub_patterns = LEVEL_CHAR_FORMAT_SUB_PATTERNS[scope]
            else:
                format_sub_patterns = LEVEL_CHAR_FORMAT_SUB_PATTERNS['default']

            # check if stripping trailing chars
            # code split like this so that only checking once not within the for-loop
            strip_trailing_chars = self.strip_trailing_chars()
            if strip_trailing_chars:
                # available scopes might differ between trailing and comment
                # check and take default as fall back
                if scope in TRAILING_PATTERNS:
                    trailing_pattern = TRAILING_PATTERNS[scope]
                else:
                    trailing_pattern = TRAILING_PATTERNS['default']

                trailing_re = re.compile(trailing_pattern)

                formatted_matches = []
                for section in sections['sections']:
                    lvl, section_text = self.get_lvl_match(section)
                    stripped_section_text = self.strip_trailing_comments(
                        section_text, trailing_re)
                    # print(match, lvl, section_text, stripped_section_text, stripped_section_match)
                    formatted_match = self.format_match_for_list(
                        format_sub_patterns, lvl, stripped_section_text)
                    formatted_matches.append(formatted_match)
            # if not stripping trailing characters
            # basically like above but no stripping trailing chars
            else:
                formatted_matches = []
                for section in sections['sections']:
                    lvl, section_text = self.get_lvl_match(section)
                    # print(match, lvl, section_text, stripped_section_text, stripped_section_match)
                    formatted_match = self.format_match_for_list(
                        format_sub_patterns, lvl, section_text)
                    formatted_matches.append(formatted_match)

        else:  # just concretise the generator and extract the matches
            formatted_matches = [
                section[1]
                for section in sections['sections']
            ]

        updated_sections = {
            'formatted_matches': formatted_matches
        }
        updated_sections.update(sections)

        return updated_sections

    # >> Goto function
    def goto_section(self, sections, index):

        # print(sections, index)
        if index == -1:
            region = self._current_cursor_loc
        else:
            region = sections['sections'][index][0]

        self.view.sel().clear()
        self.view.sel().add(region.begin())
        self.view.show(
            region.begin(), show_surrounds=True, keep_to_left=True, animate=False)
        # self.view.run_command('goto_line', {'line': self.view.line(region.begin())})

    def region_line_start(self, region):
        return self.view.line(region.begin()).a

    def nearest_section_idx(self, sections):
        view = self.view

        sections_above = []  # want a section above cursor
        for i, section in enumerate(sections):
            distance = self.region_line_start(section[0]) - self.region_line_start(self._current_cursor_loc)
            if distance <= 0:
                sections_above.append((i, distance))
            else:
                # positive distance means past current cursor
                break

        if not sections_above:
            return None
        else:
            return max(sections_above, key=lambda sa: sa[1])[0]

    def panel(self, sections):

        window = sublime.active_window()

        nearest_idx = self.nearest_section_idx(sections['sections'])
        initial_sel_idx = nearest_idx if nearest_idx else 0
        # print(initial_sel_idx)
        # print(self._current_cursor_loc, [r[0].begin() for r in sections['sections']])

        goto_callback = partial(self.goto_section, sections)
        window.show_quick_panel(
            sections['formatted_matches'],
            selected_index=initial_sel_idx,
            on_select=goto_callback, on_highlight=goto_callback
            )
