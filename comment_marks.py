import re
from functools import partial

import sublime
import sublime_plugin


# > Comment start

def get_config():
    "Extract settings and construct all relevant parameters and declar necessary global constants"

    SETTINGS = sublime.load_settings('comment_marks.sublime-settings')
    # print('Comment Marks Settings -- ', SETTINGS.to_dict())

    SCOPE_COMMENT_CHARS = SETTINGS.get('scope_comment_chars')

    COMMENT_START_PATTERNS = {
        scope: [
            rf'^[ \t]*{re.escape(c)}+'
            for c in chars
            ]
        for scope, chars
        in SCOPE_COMMENT_CHARS.items()
    }

    CUSTOM_COMMENT_START_PATTERNS = SETTINGS.get('custom_comment_start_patterns')

    # add custom to all
    COMMENT_START_PATTERNS.update(CUSTOM_COMMENT_START_PATTERNS)

    # > Compiling into complete patterns
    COMMENT_PATTERNS = {
        scope: r'|'.join([p for p in patterns ])
        for scope, patterns
        in COMMENT_START_PATTERNS.items()
    }

    # > Level Characters

    DEFAULT_LEVEL_CHAR = SETTINGS.get('default_level_char')
    LEVEL_CHARS = SETTINGS.get('level_chars')

    LEVEL_CHAR_FORMAT_SUB = SETTINGS.get('level_char_format_sub')

    LEVEL_CHAR_FORMAT_SUB = {
        int(n): sub
        for n, sub in LEVEL_CHAR_FORMAT_SUB.items()
    }

    global LEVEL_CHAR_FORMAT_SUB_PATTERNS
    LEVEL_CHAR_FORMAT_SUB_PATTERNS = {
        scope: {
            # default back to default lvl char, so long as comment_start_pattern is set
            (n*LEVEL_CHARS.get(scope, DEFAULT_LEVEL_CHAR)): sub
            for n, sub in LEVEL_CHAR_FORMAT_SUB.items()
        }
        for scope in COMMENT_START_PATTERNS
    }

    # > Full Patterns
    global LEVEL_PATTERNS
    LEVEL_PATTERNS = {
        scope: (
            # parentheses around pattern important, breaks | off from rest of pattern
            # ie, OR is not greedy
            rf'({pattern})[ ]*({re.escape(LEVEL_CHARS.get(scope, DEFAULT_LEVEL_CHAR))}+)\s*(.+)'
            )
        for scope, pattern
        in COMMENT_PATTERNS.items()
    }

    print('Comment Marks -- Full Patterns Spec:')
    for scope, pattern in LEVEL_PATTERNS.items():
        print(f'\t{scope}: {pattern}')

    global EXTRACTION_SEP
    EXTRACTION_SEP = r'|:!:|'


def plugin_loaded():
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
            'sections': list(zip(section_regions, section_matches))
        }

        return sections

    def update_with_formatted_matches(self, sections):

        if LEVEL_CHAR_FORMAT_SUB_PATTERNS:  # if none, don't do this
            scope = sections['scope']
            # should be available by this point,
            # as it means that scope is available in level_chars
            format_sub_patterns = LEVEL_CHAR_FORMAT_SUB_PATTERNS[scope]

            formatted_matches = []
            for section in sections['sections']:
                match = section[1]
                lvl, section_text = match.split(EXTRACTION_SEP)
                # print(match, lvl, section_text)
                formatted_match = f'{format_sub_patterns.get(lvl, lvl)}{section_text}'
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

    def panel(self, sections):

        goto_callback = partial(self.goto_section, sections)
        window = sublime.active_window()
        window.show_quick_panel(
            sections['formatted_matches'],
            on_select=goto_callback, on_highlight=goto_callback
            )
