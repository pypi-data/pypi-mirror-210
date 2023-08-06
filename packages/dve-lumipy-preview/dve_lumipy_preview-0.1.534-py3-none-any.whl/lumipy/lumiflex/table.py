from __future__ import annotations

from typing import Tuple, Union

from pydantic import StrictStr, Field, root_validator

from lumipy.lumiflex._column.make import make
from lumipy.lumiflex._column.ordering import Ordering
from lumipy.lumiflex._common.node import Node
from lumipy.lumiflex._metadata import TableMeta
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex._table.base_table import BaseTable
from lumipy.lumiflex._table.join import Join
from lumipy.lumiflex._table.parameter import Parameter
from lumipy.lumiflex.column import Column

from functools import reduce


def _add_prefix(meta, item) -> Node:
    if meta.alias is None:
        return item

    def _prefix(c: Column, parents):
        kwargs = {'parents': parents}
        if c.label_ == 'data' and c.meta.table_name == meta.name:
            c_meta = c.meta.update(prefix=meta.alias)
            kwargs.update(fn=lambda: f'{meta.alias}.[{c.meta.field_name}]', label='prefix', meta=c_meta)
        return c.update_node(**kwargs)

    return item.apply_map(_prefix)


class Table(BaseTable):
    """The table class represents a table of data from a data provider or a table variable.

    Tables are a data source in the lumiflex syntax. You build queries from them by chaining .select() and then
    (optionally) other methods to build up your Luminesce SQL query.

    Attributes:
        A dynamic set of column objects that can be used as arguments to methods such as select. Columns live as
        snake case named attributes on the table, or as str indexed objects much like a pandas DataFrame.

    @DynamicAttrs
    """

    label_: StrictStr = Field('data_table', const=True, alias='label')
    meta_: TableMeta = Field(alias='meta')
    parameters_: tuple = Field(alias='parameters')

    @root_validator
    def _validate_table(cls, values):

        if 'meta_' not in values:
            return values
        meta = values['meta_']

        values['from_'] = f'@{meta.name}' if meta.type == 'TableVar' else f'[{meta.name}]'

        for c in meta.columns:
            values[c.python_name()] = _add_prefix(meta, make(c))

        if meta.alias is not None:
            values['from_'] += f' AS {meta.alias}'
            values['parameters_'] = [p.with_prefix(meta.alias) for p in values['parameters_']]

        if any(p.label_ != 'parameter' for p in values['parameters_']):
            raise TypeError('Some of the input parameters were not Parameter objects. '
                            'something has gone wrong with upstream validation.')

        values['parents_'] = tuple(values['parents_']) + tuple(values['parameters_'])

        return values

    def _get_name(self):
        return self.meta_.name

    @input_constraints(..., Is.table, Is.boolean, ..., ..., name='table.left_join()')
    def left_join(self, other: Table, on: Column, left_alias='lhs', right_alias='rhs') -> Join:
        """Apply a left join between this table and another.

        Args:
            other (Table): The table on the right-hand side of the join.
            on (Column): The join condition. Must be a column or function of columns that resolves to bool.
            left_alias (str): the alias to grant the left table if it hasn't already been given one.
            right_alias (str): the alias to grant the right tabl if it hasn't already been given one.

        Returns:
            Join: a join table instance representing this join.

        """
        lhs = self.with_alias(left_alias) if self.meta_.alias is None else self
        rhs = other.with_alias(right_alias) if other.meta_.alias is None else other
        return Join(join_type='left', client=self.client_, parents=(lhs, rhs, on))

    @input_constraints(..., Is.table, Is.boolean, ..., ..., name='table.inner_join()')
    def inner_join(self, other: Table, on: Column, left_alias='lhs', right_alias='rhs') -> Join:
        """Apply an inner join between this table and another.

        Args:
            other (Table): The table on the right-hand side of the join.
            on (Column): The join condition. Must be a column or function of columns that resolves to bool.
            left_alias (str): the alias to grant the left table if it hasn't already been given one.
            right_alias (str): the alias to grant the right tabl if it hasn't already been given one.

        Returns:
            Join: a join table instance representing this join.

        """
        lhs = self.with_alias(left_alias) if self.meta_.alias is None else self
        rhs = other.with_alias(right_alias) if other.meta_.alias is None else other
        return Join(join_type='inner', client=self.client_, parents=(lhs, rhs, on))

    def with_alias(self, alias: str) -> Table:
        meta = self.meta_.update_fields(alias=alias)
        return Table(meta=meta, client=self.client_, parameters=self.parameters_, parents=(self,))

    def _get_param_assignments(self) -> Tuple[Parameter]:
        return self.parameters_

    def __contains__(self, item: Union[Column, str]) -> bool:

        cols = self.meta_.columns

        if isinstance(item, (Column, Ordering)):
            if item.label_ == 'data':
                return item.meta in cols
            else:
                # Remove ancestors that come from const nodes
                # As far as this table's concerned scalar vars and sub-queries are just constant values.
                # It should not be decomposing them and checking their dependencies.
                get_data_nodes = lambda a: [an for an in a.get_ancestors() if an.get_label() == 'data']
                consts = [get_data_nodes(a) for a in item.get_ancestors() if a.get_label() == 'const']
                consts = set(reduce(lambda x, y: x + y, consts, []))

                return all(a.meta in cols for a in item.get_ancestors() if a.label_ == 'data' and a not in consts)
        return False

    def _add_prefix(self, item) -> Node:
        return _add_prefix(self.meta_, item)

    def _add_suffix(self, c: Column):
        if self.meta_.alias is None or c.get_label() != 'prefix':
            return c
        return c._with_alias(f'{c.meta.field_name}_{c.meta.prefix}')
