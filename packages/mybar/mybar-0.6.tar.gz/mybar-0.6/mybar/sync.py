from .bar import Bar, BarTemplate
import asyncio
import json
import os
import sys
import threading
import time
from copy import deepcopy
from string import Formatter

from .constants import CONFIG_FILE, DEBUG
from . import cli
from . import utils
from .errors import *
from .field import Field, FieldPrecursor
from .formatting import FormatterFieldSig
from ._types import (
    Args,
    BarSpec,
    BarTemplateSpec,
    ConsoleControlCode,
    FieldName,
    FieldOrder,
    FmtStrStructure,
    FormatStr,
    Icon,
    JSONText,
    Kwargs,
    Line,
    PTY_Icon,
    PTY_Separator,
    Pattern,
    Separator,
    TTY_Icon,
    TTY_Separator,
)

from collections.abc import Iterable, Iterator, Sequence
from os import PathLike
from typing import IO, NoReturn, Required, Self, TypeAlias, TypedDict, TypeVar


# Unix terminal escape code (control sequence introducer):
CSI: ConsoleControlCode = '\033['
CLEAR_LINE: ConsoleControlCode = '\x1b[2K'  # VT100 escape code to clear line
HIDE_CURSOR: ConsoleControlCode = '?25l'
UNHIDE_CURSOR: ConsoleControlCode = '?25h'



class SyncField(Field):
    # For threaded fields, still run continuously!!!

    def _do_setup(self,) : #-> SetupVars|Content?  # side-effects?

        # Use the pre-defined _setupfunc() to gather constant variables
        # for func() which might only be evaluated at runtime:
        if self._setupfunc is not None:
            try:
##                if asyncio.iscoroutinefunction(self._setupfunc):
##                    setupvars = (
##                        await self._setupfunc(*self.args, **self.kwargs)
##                    )
##                else:
                setupvars = self._setupfunc(*self.args, **self.kwargs)

            # If _setupfunc raises FailedSetup with a backup value,
            # use it as the field's new constant_output:
            except FailedSetup as e:
                backup = e.backup
                contents = self._auto_format(backup)
                self.constant_output = contents  # strcontents() everywhere?
##                return contents

            # On success, give new values to kwargs to pass to func().
            return setupvars
            self.kwargs['setupvars'] = setupvars  # Do we want side-effects???


    def _auto_format(self, text: str) -> 'Contents':
        '''Non-staticmethod _format_contents...'''
        if self.fmt is None:
            if self.always_show_icon or text:
                return self.icon + text
            else:
                return text
        else:
            return self.fmt.format(text, icon=self.icon)

    def run(self, once: bool = None) -> 'Contents':
        # hook into setup() beforehand
        if asyncio.iscoroutinefunction(self._func):
            return asyncio.run(self._func(*self.args, **self.kwargs))
        return self._func(*self.args, **self.kwargs)

        # Do not run fields which have a constant output;
        # only set their bar buffer.
        if self.constant_output is not None:
            return self._auto_contents(self.constant_output)

        result = _func(*self.args, **self.kwargs)
        contents = self._auto_format(result)

        return contents


class SyncBar(Bar):
    @classmethod
    def from_template(
        cls,
        tmpl: BarTemplate,
        *,
        ignore_with: Pattern | tuple[Pattern] | None = '//'
    ) -> Self:
        '''
        Return a new :class:`Bar` from a :class:`BarTemplate`
        or a dict of :class:`Bar` parameters.
        Ignore keys and list elements starting with `ignore_with`,
        which is ``'//'`` by default.
        If :param ignore_with: is ``None``, do not remove any values.

        :param tmpl: The :class:`dict` to convert
        :type tmpl: :class:`dict`

        :param ignore_with: A pattern to ignore, defaults to ``'//'``
        :type ignore_with: :class:`_types.Pattern` | tuple[:class:`_types.Pattern`] | ``None``, optional

        :returns: A new :class:`Bar`
        :rtype: :class:`Bar`

        :raises: :exc:`errors.IncompatibleArgsError` when
            no `field_order` is defined
            or when no `fmt` is defined
        :raises: :exc:`errors.DefaultFieldNotFoundError` when either
            a field in `field_order` or
            a field in `fmt`
            cannot be found in :attr:`Field._default_fields`
        :raises: :exc:`errors.UndefinedFieldError` when
            a custom field name in `field_order` or
            a custom field name in `fmt`
            is not properly defined in `field_definitions`
        :raises: :exc:`errors.InvalidFieldSpecError` when
            a field definition is not of the form :class:`_types.FieldSpec`

        .. note:: `tmpl` can be a regular :class:`dict`
        as long as it matches the form of :class:`_types.BarSpec`.

        '''


##        if SYNC:
##            Field = SyncField


        if ignore_with is None:
            data = deepcopy(tmpl)
        else:
            data = utils.scrub_comments(tmpl, ignore_with)

        bar_params = cls._default_params | data
        field_order = bar_params.pop('field_order', None)
        field_icons = bar_params.pop('field_icons', {})  # From the CLI
        field_defs = bar_params.pop('field_definitions', {})

        if (fmt := bar_params.get('fmt')) is None:
            if field_order is None:
                raise IncompatibleArgsError(
                    "A bar format string 'fmt' is required when field "
                    "order list 'field_order' is undefined."
                )
        else:
            field_order, field_sigs = cls.parse_fmt(fmt)

        # Ensure icon assignments correspond to valid fields:
        for name in field_icons:
            if name not in field_order:
                deduped = dict.fromkeys(field_order)  # Preserve order
                expctd_from_icons = utils.join_options(deduped)
                exc = utils.make_error_message(
                    InvalidFieldError,
                    doing_what="parsing custom Field icons",
                    blame=f"{name!r}",
                    expected=f"a Field name from among {expctd_from_icons}",
                    epilogue="Only assign icons to Fields that will be in the Bar."
                )
                raise exc from None

        # Gather Field parameters and instantiate them:
        fields = {}
        expctd_name="the name of a default or properly defined `custom` Field"

        for name in field_order:
            field_params = field_defs.get(name)

            match field_params:
                case None:
                    # The field is strictly default.
                    if name in fields:
                        continue

                    try:
                        field = SyncField.from_default(name)
                    except DefaultFieldNotFoundError:
                        exc = utils.make_error_message(
                            DefaultFieldNotFoundError,
                            # doing_what="parsing 'field_order'",  # Only relevant to config file parsing
                            blame=f"{name!r}",
                            expected=expctd_name
                        )
                        raise exc from None

                case {'custom': True}:
                    # The field is custom, so it is only defined in
                    # 'field_definitions' and will not be found as a default.
                    name = field_params.pop('name', name)
                    del field_params['custom']
                    field = SyncField(**field_params, name=name)

                case {}:
                    # The field is a default overridden by the user.
                    # Are there custom icons given from the CLI?
                    if name in field_icons:
                        cust_icon = field_icons.pop(name)
                        field_params['icons'] = (cust_icon, cust_icon)

                    try:
                        field = SyncField.from_default(name, overrides=field_params)
                    except DefaultFieldNotFoundError:
                        exc = utils.make_error_message(
                            UndefinedFieldError,
                            # doing_what="parsing 'field_order'",
                            blame=f"{name!r}",
                            expected=expctd_name,
                            epilogue=(
                                f"(In config files, remember to set "
                                f"`custom=true` "
                                f"for custom field definitions.)"
                            ),
                        )
                        raise exc from None

                case _:
                    # Edge cases.
                    exc = utils.make_error_message(
                        InvalidFieldSpecError,
                        # doing_what="parsing 'field_definitions'",
                        doing_what=f"parsing {name!r} definition",
                        details=(
                            f"Invalid Field specification: {field_params!r}",
                        ),
                        indent_level=1
                    )
                    raise exc from None

            fields[name] = field

        bar = cls(
            fields=tuple(fields.values()),
            field_order=field_order,
            **bar_params
        )
        return bar

    def run(self, once: bool = None, stream: IO = None) -> None:
        '''
        Run the bar in the specified output stream.
        Block until an exception is raised and exit smoothly.

        :param stream: The IO stream in which to run the bar,
            defaults to :attr:`Bar._stream`
        :type stream: :class:`IO`

        :param once: Whether to print the bar only once, defaults to ``False``
        :type once: :class:`bool`

        :returns: ``None``
        '''
        if stream is not None:
            self._stream = stream
        if once is None:
            once = self.run_once

        try:
            self._can_run.set()
            overriding = False

            for field in self:
                if field.overrides_refresh:
                    overriding = True

                if field.threaded:
                    field.sync_send_to_thread(run_once=once)

            if once:
                for field in self:
                    field.run()
                # Wait for threads to finish:
                while self._threads:
                    time.sleep(self._thread_cooldown)
                self._print_one_line()

            else:
                if overriding:
                    self._handle_overrides()
                self._continuous_line_printer()

        except KeyboardInterrupt:
            pass

        finally:
            self._shutdown()


    def _continuous_line_printer(self, end: str = '\r') -> None:
        using_format_str = (self.fmt is not None)
        sep = self.separator
        running = self._can_run.is_set
        clock = time.monotonic

        if self.in_a_tty:
            beginning = self.clearline_char + end
            self._stream.write(CSI + HIDE_CURSOR)
        else:
            beginning = self.clearline_char

        # fields = set(self._fields) - self._threads
        fields = tuple(f for f in self if not f.threaded)
        print(fields)

        # Flushing the buffer before writing to it fixes poor i3bar alignment.
        self._stream.flush()

##        # Print something right away just so that the bar is not empty:
##        self._print_one_line()

        if self.align_to_seconds:
            # Begin every refresh at the start of a clock second:
            clock = time.time
            time.sleep(1 - (clock() % 1))

        start_time = clock()
        for f in fields:
            print(f._func)
        while running():
            self._buffers.update((f.name, f.run()) for f in fields)
                
            if using_format_str:
                line = self.fmt.format_map(self._buffers)
            else:
                line = sep.join(
                    buf for field in fields
                        if (buf := self._buffers[field.name])
                        or self.join_empty_fields
                )

            self._stream.write(beginning + line + end)
            self._stream.flush()

            # Sleep only until the next possible refresh to keep the
            # refresh cycle length consistent and prevent drifting.
            time.sleep(
                # Time until next refresh:
                self.refresh_rate - (
                    # Get the current latency, which can vary:
                    (clock() - start_time) % self.refresh_rate  # Preserve offset
                )
            )

        if self.in_a_tty:
            self._stream.write('\n')
            self._stream.write(CSI + UNHIDE_CURSOR)

    def line_generator(self):
        using_format_str = (self.fmt is not None)
        sep = self.separator
        running = self._can_run.is_set

        while running():
            if using_format_str:
                line = self.fmt.format_map(self._buffers)
            else:
                line = sep.join(
                    buf for field in self._field_order
                        if (buf := self._buffers[field])
                        or self.join_empty_fields
                )
            yield line



