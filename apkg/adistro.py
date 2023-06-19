"""
apkg helpers for distro parsing and matching

standard distro module is used for getting current distro
"""
from abc import ABC, abstractmethod
import re

try:
    from functools import cached_property
except ImportError:
    from cached_property import cached_property
from packaging.specifiers import SpecifierSet
from packaging import version

import distro

from apkg.log import getLogger
from apkg.util import common


log = getLogger(__name__)


RE_VERSION_RULE = r'(\w+)\s*((?:==|!=|~=|<=?|>=?)\s*\d+.*)'


class Distro:
    """
    represent distro by id and (optional) version
    """
    def __init__(self, distro_str, aliases=None):
        self.orig = distro_str
        # idver format, i.e.: debian-10, ubuntu-21.04
        self.idver = distro2idver(self.orig)
        self.id, self.version = parse_idver(self.idver)
        self.aliases = aliases or {}

    def match(self, *rules):
        """
        return True if self matches supplied distro rule(s)
        """
        drules = distro_rules(rules, aliases=self.aliases)
        return drules.match(self)

    def print(self, sep='-', short=False):
        s = self.id
        if short:
            s = s[:3]
        if not self.version:
            return s
        if sep:
            s += sep
        s += str(self.version)
        return s

    @cached_property
    def human(self):
        """
        return distro in human-friendly format, i.e.: 'fedora 10'
        """
        return self.print(sep=' ')

    @cached_property
    def tiny(self):
        """
        return distro in tiny format, i.e.: deb10, ubu21.04
        """
        return self.print(sep='', short=True)

    @cached_property
    def parsed_version(self):
        return version.parse(self.version)

    def __str__(self):
        return self.human

    def __repr__(self):
        return "<Distro('%s')>" % self.idver


class DistroRuleBase(ABC):
    """
    base class for distro rules
    """
    @abstractmethod
    def match(self, distro_):
        pass


class DistroRule(DistroRuleBase):
    """
    rule matching specific distro id and version range
    """
    def __init__(self, rule_str):
        self.rule_str = rule_str
        m = re.match(RE_VERSION_RULE, rule_str)
        if m:
            self.id = m.group(1)
            spec_str = m.group(2)
            self.version_spec = SpecifierSet(spec_str)
        else:
            self.id = rule_str
            self.version_spec = None

    def match(self, distro_):
        if distro_.id != self.id:
            return False
        if not self.version_spec:
            return True
        if not distro_.version:
            return False
        return distro_.parsed_version in self.version_spec

    def __str__(self):
        return self.rule_str

    def __repr__(self):
        return "<DistroRule('%s')>" % self.rule_str


class DistroRuleAll(DistroRuleBase):
    """
    rule matching any distro
    """
    def match(self, _):
        return True

    def __str__(self):
        return 'all distros'

    def __repr__(self):
        return "<DistroRuleAll>"


class DistroRules(DistroRuleBase):
    """
    list of multiple distro rules
    """
    def __init__(self, rules):
        self.rules = rules

    def match(self, distro_):
        """
        return True when any single rule matches (OR)
        """
        for rule in self.rules:
            if rule.match(distro_):
                return True
        return False

    def __str__(self):
        return ' | '. join([r.rule_str for r in self.rules])

    def __repr__(self):
        return "<ApkgDistroRules(%s)>" % self.__str__()


def distro_rules(rules, aliases=None):
    """
    parse (a list of) distro rule string(s) into ApkgDistroRule(s)
    using distro aliases if supplied

    Params:
        rules: a distro rule string or a list of thereof
        aliases: distro aliases dict (optional)

    Return:
        * ApkgDistroRule for a string
        * ApkgDistroRules for a list of strings
    """
    if isinstance(rules, str):
        # single rule string
        rules = [rules]

    aliases = aliases or {}
    drules = []
    for rule in rules:
        if rule in aliases:
            r = aliases[rule]
        else:
            r = DistroRule(rule)
        drules.append(r)

    if len(drules) == 1:
        # single DistroRule
        return drules[0]
    else:
        # multiple DistroRules
        return DistroRules(drules)


def name2rule(name):
    """
    return distro rule based on distro-specific (file) name
    """
    rule_str, _, ver = name.partition('-')
    if ver:
        rule_str += ' == %s' % ver
    return DistroRule(rule_str)


def sort_by_name(objs, name_attr='name'):
    """
    sort objects by distro-specific (file) name

    Params:
        objs: list of objects with name_attr attribute
        name_attr: object attribute (distro name) to sort by

    Return:
        objs list ordered by name_attr which is assumed to be
        distro name such as 'debian' or 'ubuntu-20.04':

        * names with release first
        * primary sort by name
        * secondary sort by release desc (for determinism)
    """

    def sort_key(o):
        distro_, _, rls = getattr(o, name_attr).rpartition('-')
        try:
            rlsv = version.parse(rls)
        except version.InvalidVersion:
            rlsv = rls
        return distro_, common.SortReversor(rlsv)

    plain_objs = []
    rls_objs = []
    for o in objs:
        if '-' in getattr(o, name_attr):
            rls_objs.append(o)
        else:
            plain_objs.append(o)

    rls_objs.sort(key=sort_key)
    plain_objs.sort(key=lambda x: getattr(x, name_attr))

    return rls_objs + plain_objs


def parse_distro_aliases(config):
    """
    parse distro aliases from config fromat into a dict
    """
    aliases = {}
    for alias in config:
        name = alias.get('name')
        if not name:
            log.warning("Ignoring invalid distro alias:"
                        " missing required option: name")
            continue
        distro_ = alias.get('distro')
        if not name:
            log.warning("Ignoring invalid distro alias:"
                        " missing required option: distro")
            continue
        try:
            rules = distro_rules(distro_)
        except Exception as ex:
            log.warning("Ignoring invalid distro alias '%s':"
                        " invalid distro rule: %s",
                        name, str(ex))
            continue
        aliases[name] = rules
    return aliases


def distro_arg(distro_str, proj=None):
    """
    normalize --distro argument as used by CLI

    set distro aliases from project if supplied (optional)

    return current distro if not set
    """
    if not distro_str:
        # current distro by default
        d = current_distro()
    elif isinstance(distro_str, Distro):
        # already correct format
        d = distro_str
    else:
        # convert custom distro string to Distro
        d = Distro(distro_str)
    if proj:
        d.aliases = proj.distro_aliases
    return d


def distro2idver(distro_name):
    """
    convert generic distro string into idver format
    """
    return re.sub(r'\s+', '-', distro_name.strip().lower())


def parse_idver(idver_str):
    """
    split idver string 'distro-version' into (distro, version)
    """
    id_, _, ver_ = idver_str.partition('-')
    return id_, ver_


def current_idver(sep='-'):
    """
    return current distro in default idver format
    used by apkg to reference individual distros

    examples: debian-10, fedora-32, arch
    """
    idver = distro.id()
    ver = distro.version()
    if ver:
        idver += "%s%s" % (sep, ver)
    return idver


def current_fullname():
    """
    return human readable string describing current distro
    """
    parts = [
        distro.name(),
        distro.version(pretty=True),
    ]
    return " ".join([p for p in parts if p])


def current_distro():
    return Distro(current_idver(sep=' '))
