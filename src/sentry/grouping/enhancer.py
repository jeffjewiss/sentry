from __future__ import absolute_import

import six
import base64
import msgpack

from parsimonious.grammar import Grammar, NodeVisitor


# Grammar is defined in EBNF syntax.
enhancements_grammar = Grammar(r"""

enhancements = line+

line = _ (comment / rule / empty) newline?

rule = _ matchers actions

matchers       = matcher+
matcher        = _ matcher_type sep argument
matcher_type   = "path" / "function" / "module"

actions        = action+
action         = _ range? flag action_name
action_name    = "keep" / "group" / "in-app"
flag           = "+" / "-"
range          = "^" / "v"

comment        = ~r"#[^\r\n]*"

argument       = quoted / unquoted
quoted         = ~r'"([^"\\]*(?:\\.[^"\\]*)*)"'
unquoted       = ~r"\S+"

sep     = ":"
space   = " "
empty   = ""
newline = ~r"[\r\n]"
_       = space*

""")


VERSION = 1
MATCH_KEYS = {
    'path': 'p',
    'function': 'f',
    'module': 'm',
}
SHORT_MATCH_KEYS = dict((v, k) for k, v in six.iteritems(MATCH_KEYS))

ACTIONS = ['keep', 'group', 'in-app']
ACTION_FLAGS = {
    (True, None): 0,
    (True, 'up'): 1,
    (True, 'down'): 2,
    (False, None): 3,
    (False, 'up'): 4,
    (False, 'down'): 5,
}
REVERSE_ACTION_FLAGS = dict((v, k) for k, v in six.iteritems(ACTION_FLAGS))


class Match(object):

    def __init__(self, key, pattern):
        self.key = key
        self.pattern = pattern

    def _to_config_structure(self):
        return MATCH_KEYS[self.key] + self.pattern

    @classmethod
    def _from_config_structure(cls, obj):
        return cls(SHORT_MATCH_KEYS[obj[0]], obj[1:])


class Action(object):

    def __init__(self, key, flag, range):
        self.key = key
        self.flag = flag
        self.range = range

    def _to_config_structure(self):
        return ACTIONS.index(self.key) | (ACTION_FLAGS[self.flag, self.range] << 5)

    @classmethod
    def _from_config_structure(cls, num):
        flag, range = REVERSE_ACTION_FLAGS[num >> 5]
        return cls(ACTIONS[num & 0xf], flag, range)


class Enhancements(object):

    def __init__(self, rules, version):
        self.rules = rules
        self.version = version

    def _to_config_structure(self):
        return [self.version, [x._to_config_structure() for x in self.rules]]

    def dumps(self):
        return base64.urlsafe_b64encode(msgpack.dumps(
            self._to_config_structure()).encode('zlib')).strip('=')

    @classmethod
    def _from_config_structure(cls, data):
        version, rules = data
        return cls([Rule._from_config_structure(x) for x in rules], version)

    @classmethod
    def loads(cls, data):
        padded = data + b'=' * (4 - (len(data) % 4))
        try:
            return cls._from_config_structure(msgpack.loads(
                base64.urlsafe_b64decode(padded).decode('zlib')))
        except (LookupError, AttributeError, TypeError, ValueError) as e:
            raise ValueError('invalid grouping enhancement config: %s' % e)

    @classmethod
    def from_config_string(self, s):
        tree = enhancements_grammar.parse(s)
        return EnhancmentsVisitor().visit(tree)


class Rule(object):

    def __init__(self, matchers, actions):
        self.matchers = matchers
        self.actions = actions

    def _to_config_structure(self):
        return [
            [x._to_config_structure() for x in self.matchers],
            [x._to_config_structure() for x in self.actions],
        ]

    @classmethod
    def _from_config_structure(cls, tuple):
        return Rule([Match._from_config_structure(x) for x in tuple[0]],
                    [Action._from_config_structure(x) for x in tuple[1]])


class EnhancmentsVisitor(NodeVisitor):
    visit_comment = visit_empty = lambda *a: None

    def visit_enhancements(self, node, children):
        return Enhancements(filter(None, children), version=VERSION)

    def visit_line(self, node, children):
        _, line, _ = children
        comment_or_rule_or_empty = line[0]
        if comment_or_rule_or_empty:
            return comment_or_rule_or_empty

    def visit_rule(self, node, children):
        _, matcher, actions = children
        return Rule(matcher, actions)

    def visit_matcher(self, node, children):
        _, ty, _, argument = children
        return Match(ty, argument)

    def visit_matcher_type(self, node, children):
        return node.text

    def visit_argument(self, node, children):
        return children[0]

    def visit_action(self, node, children):
        _, rng, flag, action_name = children
        return Action(action_name, flag, rng[0] if rng else None)

    def visit_action_name(self, node, children):
        return node.text

    def visit_flag(self, node, children):
        return node.text == '+'

    def visit_range(self, node, children):
        if node.text == '^':
            return 'up'
        return 'down'

    def visit_quoted(self, node, children):
        return node.text[1:-1] \
            .encode('ascii', 'backslashreplace') \
            .decode('unicode-escape')

    def visit_unquoted(self, node, children):
        return node.text

    def visit_identifier(self, node, children):
        return node.text

    def generic_visit(self, node, children):
        return children
