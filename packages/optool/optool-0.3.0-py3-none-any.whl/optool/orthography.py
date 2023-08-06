import humanize
import inflection

# kebab-case, SNAKE_CASE, PascalCase, camelCase, snake_case or space case

camelize = inflection.camelize
dasherize = inflection.dasherize
headerize = inflection.humanize
ordinal = inflection.ordinal
ordinalize = inflection.ordinalize
parameterize = inflection.parameterize
pluralize = inflection.pluralize
singularize = inflection.singularize
tableize = inflection.tableize
titleize = inflection.titleize
transliterate = inflection.transliterate
underscore = inflection.underscore


def textualize(string: str):
    """
    Make a lowercase form consisting of words suitable for regular text from the expression in the string.

    Example::

    >>> textualize("DeviceType")
    >>> 'device type'
    """
    return inflection.humanize(inflection.underscore(string)).lower()


fractional = humanize.fractional
intcomma = humanize.intcomma
intword = humanize.intword
naturaldate = humanize.naturaldate
naturalday = humanize.naturalday
naturaldelta = humanize.naturaldelta
naturalsize = humanize.naturalsize
naturaltime = humanize.naturaltime
precisedelta = humanize.precisedelta
scientific = humanize.scientific
