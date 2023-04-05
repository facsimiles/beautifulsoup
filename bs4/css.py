"""Integration code for CSS selectors using `Soup Sieve <https://facelessuser.github.io/soupsieve/>`_ (pypi: ``soupsieve``).

Acquire a `CSS` object through the `Tag.css` attribute of the `bs4.Tag`
you want to use as the starting point for a CSS selector, or (if you
want to run a selector against the entire document) of the
`BeautifulSoup` object itself.

The main advantage of doing this instead of using ``soupsieve``
functions is that you don't need to keep passing the `bs4.Tag` to be
selected against, since the `CSS` object is permanently scoped to that
`bs4.Tag`.
"""

from __future__ import annotations

from types import ModuleType
from typing import Optional
import warnings
try:
    import soupsieve
except ImportError as e:
    soupsieve = None
    warnings.warn(
        'The soupsieve package is not installed. CSS selectors cannot be used.'
    )

class CSS(object):
    """A proxy object against the ``soupsieve`` library, to simplify its
    CSS selector API.

    You don't need to instantiate this class yourself; instead, use
    `Tag.css`.

    :param tag: All CSS selectors run by this object will use this as
        their starting point.

    :param api: An optional drop-in replacement for the ``soupsieve`` module,
        intended for use in unit tests.
    """
    def __init__(self, tag: Tag, api:Optional[ModuleType]=None):
        if api is None:
            api = soupsieve
        if api is None:
            raise NotImplementedError(
                "Cannot execute CSS selectors because the soupsieve package is not installed."
            )
        self.api = api
        self.tag = tag

    def escape(self, ident:str) -> str:
        """Escape a CSS identifier.

        This is a simple wrapper around `soupsieve.escape() <https://facelessuser.github.io/soupsieve/api/#soupsieveescape>`_. See the
        documentation for that function for more information.
        """
        if soupsieve is None:
            raise NotImplementedError(
                "Cannot escape CSS identifiers because the soupsieve package is not installed."
            )
        return self.api.escape(ident)

    def _ns(self, ns, select):
        """Normalize a dictionary of namespaces."""
        if not isinstance(select, self.api.SoupSieve) and ns is None:
            # If the selector is a precompiled pattern, it already has
            # a namespace context compiled in, which cannot be
            # replaced.
            ns = self.tag._namespaces
        return ns

    def _rs(self, results):
        """Normalize a list of results to a Resultset.

        A ResultSet is more consistent with the rest of Beautiful
        Soup's API, and ResultSet.__getattr__ has a helpful error
        message if you try to treat a list of results as a single
        result (a common mistake).
        """
        # Import here to avoid circular import
        from bs4.element import ResultSet
        return ResultSet(None, results)

    def compile(self,
                select:str,
                namespaces:Optional[dict[str, str]]=None,
                flags:int=0,
                **kwargs
                ):
        """Pre-compile a selector and return the compiled object.

        :param selector: A CSS selector.

        :param namespaces: A dictionary mapping namespace prefixes
           used in the CSS selector to namespace URIs. By default,
           Beautiful Soup will use the prefixes it encountered while
           parsing the document.

        :param flags: Flags to be passed into Soup Sieve's
            `soupsieve.compile() <https://facelessuser.github.io/soupsieve/api/#soupsievecompile>`_ method.

        :param kwargs: Keyword arguments to be passed into Soup Sieve's
           `soupsieve.compile() <https://facelessuser.github.io/soupsieve/api/#soupsievecompile>`_ method.

        :return: A precompiled selector object.
        :rtype: soupsieve.SoupSieve
        """
        return self.api.compile(
            select, self._ns(namespaces, select), flags, **kwargs
        )

    def select_one(
            self, select:str,
            namespaces:Optional[dict[str, str]]=None,
            flags:int=0, **kwargs
    )-> bs4.Tag | None:
        """Perform a CSS selection operation on the current Tag and return the
        first result, if any.

        This uses the Soup Sieve library. For more information, see
        that library's documentation for the `soupsieve.select_one() <https://facelessuser.github.io/soupsieve/api/#soupsieveselect_one>`_ method.

        :param selector: A CSS selector.

        :param namespaces: A dictionary mapping namespace prefixes
           used in the CSS selector to namespace URIs. By default,
           Beautiful Soup will use the prefixes it encountered while
           parsing the document.

        :param flags: Flags to be passed into Soup Sieve's
            `soupsieve.select_one() <https://facelessuser.github.io/soupsieve/api/#soupsieveselect_one>`_ method.

        :param kwargs: Keyword arguments to be passed into Soup Sieve's
           `soupsieve.select_one() <https://facelessuser.github.io/soupsieve/api/#soupsieveselect_one>`_ method.
        """
        return self.api.select_one(
            select, self.tag, self._ns(namespaces, select), flags, **kwargs
        )

    def select(self, select:str,
               namespaces:Optional[dict[str, str]]=None,
               limit:int=0, flags:int=0, **kwargs) -> 'ResultSet[bs4.Tag]':
        """Perform a CSS selection operation on the current `bs4.Tag`.

        This uses the Soup Sieve library. For more information, see
        that library's documentation for the `soupsieve.select() <https://facelessuser.github.io/soupsieve/api/#soupsieveselect>`_ method.

        :param selector: A CSS selector.

        :param namespaces: A dictionary mapping namespace prefixes
            used in the CSS selector to namespace URIs. By default,
            Beautiful Soup will pass in the prefixes it encountered while
            parsing the document.

        :param limit: After finding this number of results, stop looking.

        :param flags: Flags to be passed into Soup Sieve's
            `soupsieve.select() <https://facelessuser.github.io/soupsieve/api/#soupsieveselect>`_ method.

        :param kwargs: Keyword arguments to be passed into Soup Sieve's
           `soupsieve.select() <https://facelessuser.github.io/soupsieve/api/#soupsieveselect>`_ method.
        """
        if limit is None:
            limit = 0

        return self._rs(
            self.api.select(
                select, self.tag, self._ns(namespaces, select), limit, flags,
                **kwargs
            )
        )

    def iselect(self, select:str,
               namespaces:Optional[dict[str, str]]=None,
               limit:int=0, flags:int=0, **kwargs) -> Iterator[bs4.Tag]:
        """Perform a CSS selection operation on the current `bs4.Tag`.

        This uses the Soup Sieve library. For more information, see
        that library's documentation for the `soupsieve.iselect()
        <https://facelessuser.github.io/soupsieve/api/#soupsieveiselect>`_
        method. It is the same as select(), but it returns a generator
        instead of a list.

        :param selector: A string containing a CSS selector.

        :param namespaces: A dictionary mapping namespace prefixes
            used in the CSS selector to namespace URIs. By default,
            Beautiful Soup will pass in the prefixes it encountered while
            parsing the document.

        :param limit: After finding this number of results, stop looking.

        :param flags: Flags to be passed into Soup Sieve's
            `soupsieve.iselect() <https://facelessuser.github.io/soupsieve/api/#soupsieveiselect>`_ method.

        :param kwargs: Keyword arguments to be passed into Soup Sieve's
           `soupsieve.iselect() <https://facelessuser.github.io/soupsieve/api/#soupsieveiselect>`_ method.
        """
        return self.api.iselect(
            select, self.tag, self._ns(namespaces, select), limit, flags, **kwargs
        )

    def closest(self, select:str,
               namespaces:Optional[dict[str, str]]=None,
               flags:int=0, **kwargs) -> bs4.Tag | None:
        """Find the `bs4.Tag` closest to this one that matches the given selector.

        This uses the Soup Sieve library. For more information, see
        that library's documentation for the `soupsieve.closest()
        <https://facelessuser.github.io/soupsieve/api/#soupsieveclosest>`_
        method.

        :param selector: A string containing a CSS selector.

        :param namespaces: A dictionary mapping namespace prefixes
            used in the CSS selector to namespace URIs. By default,
            Beautiful Soup will pass in the prefixes it encountered while
            parsing the document.

        :param flags: Flags to be passed into Soup Sieve's
            `soupsieve.closest() <https://facelessuser.github.io/soupsieve/api/#soupsieveclosest>`_ method.

        :param kwargs: Keyword arguments to be passed into Soup Sieve's
           `soupsieve.closest() <https://facelessuser.github.io/soupsieve/api/#soupsieveclosest>`_ method.

        """
        return self.api.closest(
            select, self.tag, self._ns(namespaces, select), flags, **kwargs
        )

    def match(self, select:str,
              namespaces:Optional[dict[str, str]]=None,
              flags:int=0, **kwargs) -> bool:
        """Check whether or not this `bs4.Tag` matches the given CSS selector.

        This uses the Soup Sieve library. For more information, see
        that library's documentation for the `soupsieve.match()
        <https://facelessuser.github.io/soupsieve/api/#soupsievematch>`_
        method.

        :param: a CSS selector.

        :param namespaces: A dictionary mapping namespace prefixes
            used in the CSS selector to namespace URIs. By default,
            Beautiful Soup will pass in the prefixes it encountered while
            parsing the document.

        :param flags: Flags to be passed into Soup Sieve's
            `soupsieve.match()
            <https://facelessuser.github.io/soupsieve/api/#soupsievematch>`_
            method.

        :param kwargs: Keyword arguments to be passed into SoupSieve's
            `soupsieve.match()
            <https://facelessuser.github.io/soupsieve/api/#soupsievematch>`_
            method.
        """
        return self.api.match(
            select, self.tag, self._ns(namespaces, select), flags, **kwargs
        )

    def filter(self, select:str,
              namespaces:Optional[dict[str, str]]=None,
              flags:int=0, **kwargs) -> ResultSet[bs4.Tag]:
        """Filter this `bs4.Tag`'s direct children based on the given CSS selector.

        This uses the Soup Sieve library. It works the same way as
        passing a `bs4.Tag` into that library's `soupsieve.filter()
        <https://facelessuser.github.io/soupsieve/api/#soupsievefilter>`_
        method. For more information, see the documentation for
        `soupsieve.filter()
        <https://facelessuser.github.io/soupsieve/api/#soupsievefilter>`_.

        :param namespaces: A dictionary mapping namespace prefixes
            used in the CSS selector to namespace URIs. By default,
            Beautiful Soup will pass in the prefixes it encountered while
            parsing the document.

        :param flags: Flags to be passed into Soup Sieve's
            `soupsieve.filter()
            <https://facelessuser.github.io/soupsieve/api/#soupsievefilter>`_
            method.

        :param kwargs: Keyword arguments to be passed into SoupSieve's
            `soupsieve.filter()
            <https://facelessuser.github.io/soupsieve/api/#soupsievefilter>`_
            method.
        """
        return self._rs(
            self.api.filter(
                select, self.tag, self._ns(namespaces, select), flags, **kwargs
            )
        )
