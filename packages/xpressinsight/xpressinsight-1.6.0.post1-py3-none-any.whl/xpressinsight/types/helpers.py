"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2022 Fair Isaac Corporation. All rights reserved.
"""

import sys

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated
from typing import Union, List
import xpressinsight as xi
from xpressinsight.entities import BASIC_TYPE, BASIC_TYPE_MAP, Hidden, Manage
import pandas as pd


#
def Scalar(
        default: Union[str, bool, int, float] = None,
        dtype: BASIC_TYPE = None,
        #
        alias: str = "",
        format: str = "",
        hidden: Hidden = Hidden.FALSE,
        manage: Manage = Manage.INPUT,
        read_only: bool = False,
        transform_labels_entity: str = "",
        update_after_execution: bool = False,
        *,
        update_progress: bool = False,
        #
) -> type:
    """
    Creates an annotation for a *scalar* entity,.

    Examples
    --------
    Some examples of declaring scalar entities in the data model.

    >>> @xi.AppConfig(name="My First Insight Python App",
    ...               version=xi.AppVersion(0, 1, 2))
    ... class MyApp(xi.AppBase):
    ...
    ...     # Examples where data type is inferred from default value
    ...     # Scalar "NumFactory" of type "xi.integer"; default value 10
    ...     NumFactory: xi.types.Scalar(10)
    ...     # Scalar "IsOn" of type "xi.boolean"; default value True
    ...     IsOn: xi.types.Scalar(True)
    ...
    ...     # Examples where data type is explicitly given.
    ...     RealScalar: xi.types.Scalar(dtype=xi.real)      # default value 0.0
    ...     StringScalar: xi.types.Scalar(dtype=xi.string)  # default value ""

    Parameters
    ----------
    default : Union[str, bool, int, float] = None
        The default value.
    dtype : BASIC_TYPE
        The data-type.
    alias : str = ""
        Used to provide an alternative name for an entity in the UI.
        The value is used in place of the entity name where appropriate in the UI.
    format : str = ""
        The formatting string used for displaying numeric values.
    hidden : Hidden = Hidden.FALSE
        Indicates whether the UI should hide the entity where appropriate.
    manage : Manage = Manage.INPUT
        How and whether Insight handles an entity. Defines how the system manages the entity data.
    read_only : bool = False
        Whether an entity is readonly. Specifies that the value(s) of the entity cannot be modified. See also
        `hidden`.
    transform_labels_entity : str = ""
        An entity in the schema to be used as a labels entity. The value is the name of the entity.
        The type of the index set of the labels entity must match the data type of this entity.
        The data type of the labels entity can be any primitive type.
    update_after_execution : bool = False
        Whether the value of the entity in the scenario is updated with the value of
        the corresponding model entity at the end of the scenario execution.
        If `True` the value of the entity is updated to correspond with the model entity after execution.
    update_progress : bool = False
        Whether the value of the entity in the scenario is sent on progress updates.
        If `True` the value of the entity will be written back to the Insight repository when
        :fct-ref:`insight.send_progress_update` is called from an execution mode where the `send_progress`
        attribute is `True`.

    Notes
    -----
    This function returns an `Annotated` type containing the `Scalar` entity object; for example,
    `xi.types.Scalar(dtype=xi.integer)` is equivalent to `Annotated[int, xi.Scalar(dtype=xi.integer)]`.

    Parameters before `update_progress` can be specified positionally for reasons of backwards compatibility,
    but it's recommended that you always use named arguments if you're specifying parameters other than `default`,
    `dtype` and `alias`.

    See Also
    --------
    Scalar
    types.Param
    """
    entity = xi.Scalar(
        default=default,
        dtype=dtype,
        alias=alias,
        format=format,
        hidden=hidden,
        manage=manage,
        read_only=read_only,
        transform_labels_entity=transform_labels_entity,
        update_after_execution=update_after_execution,
        update_progress=update_progress
    )
    return Annotated[BASIC_TYPE_MAP[entity.dtype], entity]


#
def Param(
        default: Union[str, int, bool, float] = None,
        dtype: BASIC_TYPE = None
) -> type:
    """
    Creates an annotation for a *parameter* entity. Parameters can be used to configure an Xpress Insight app. When
    parameters are declared, their name, data type, and default value must be specified. Parameters are typically
    read-only.

    Examples
    --------
    Some examples of declaring parameter entities in the data model.

    >>> @xi.AppConfig(name="My First Insight Python App",
    ...               version=xi.AppVersion(0, 1, 2))
    ... class MyApp(xi.AppBase):
    ...
    ...     # examples where data type is inferred from the default value
    ...     # Param "P" of type "xi.integer" with default value 100
    ...     P: xi.types.Param(100)
    ...     # Param "DEBUG" of type "xi.boolean" with default value False
    ...     DEBUG: xi.types.Param(False)
    ...     # Param "PI" of type "xi.real" with default value 3.14
    ...     PI: xi.types.Param(3.14)
    ...     # Param "STR_PARAM" of type xi.string with a default value
    ...     STR_PARAM: xi.types.Param('My String Param')
    ...
    ...     # examples where data type is explicitly given
    ...     BOOL_PARAM: xi.types.Param(dtype=xi.boolean)  # default value False
    ...     INT_PARAM: xi.types.Param(dtype=xi.integer)  # default value 0
    ...     REAL_PARAM: xi.types.Param(dtype=xi.real)  # default value 0.0
    ...     STRING_PARAM: xi.types.Param(dtype=xi.string)  # default value ""

    Parameters
    ----------
    default: Union[str, int, bool, float]
        The default value.
    dtype: BASIC_TYPE
        The data type of the parameter.

    Notes
    -----
    This function returns an `Annotated` type containing the `Param` entity object; for example,
    `xi.types.Param(dtype=xi.integer)` is equivalent to `Annotated[int, xi.Param(dtype=xi.integer)]`.

    See Also
    --------
    Param
    types.Scalar
    """
    entity = xi.Param(
        default=default,
        dtype=dtype
    )
    return Annotated[BASIC_TYPE_MAP[entity.dtype], entity]


#
def Index(
        dtype: BASIC_TYPE,
        #
        alias: str = "",
        format: str = "",
        hidden: Hidden = Hidden.FALSE,
        manage: Manage = Manage.INPUT,
        read_only: bool = False,
        transform_labels_entity: str = "",
        update_after_execution: bool = False,
        *,
        update_progress: bool = False,
        #
) -> type:
    """
    Creates an annotation for an *index* entity. To be used in conjunction with `xpressinsight.types.Series` or
    `xpressinsight.types.DataFrame` entities.

    Examples
    --------
    Example creating an index of integer values with an alias.

    >>> Indices: xi.types.Index(dtype=xi.integer, alias='Array Indices')

    Parameters
    ----------
    dtype : BASIC_TYPE
        The data-type.
    alias : str = ""
        Used to provide an alternative name for an entity in the UI.
        The value is used in place of the entity name where appropriate in the UI.
    format : str = ""
        The formatting string used for displaying numeric values.
    hidden : Hidden = Hidden.FALSE
        Indicates whether the UI should hide the entity where appropriate.
    manage : Manage = Manage.INPUT
        How and whether Insight handles an entity. Defines how the system manages the entity data.
    read_only : bool = False
        Whether an entity is readonly. Specifies that the value(s) of the entity cannot be modified. See also
        `hidden`.
    transform_labels_entity : str = ""
        An entity in the schema to be used as a labels entity. The value is the name of the entity.
        The type of the index set of the labels entity must match the data type of this entity.
        The data type of the labels entity can be any primitive type.
    update_after_execution : bool = False
        Whether the value of the entity in the scenario is updated with the value of
        the corresponding model entity at the end of the scenario execution.
        If `True` the value of the entity is updated to correspond with the model entity after execution.
    update_progress : bool = False
        Whether the value of the entity in the scenario is sent on progress updates.
        If `True` the value of the entity will be written back to the Insight repository when
        :fct-ref:`insight.send_progress_update` is called from an execution mode where the `send_progress`
        attribute is `True`.

    Notes
    -----
    This function returns an `Annotated` type containing the `Index` entity object; for example,
    `xi.types.Index(dtype=xi.integer)` is equivalent to `Annotated[pandas.Index, xi.Index(dtype=xi.integer)]`.

    Parameters before `update_progress` can be specified positionally for reasons of backwards compatibility,
    but it's recommended that you always use named arguments if you're specifying parameters other than
    `dtype` and `alias`.

    See Also
    --------
    types.Series
    types.DataFrame
    Index
    """
    entity = xi.Index(
        dtype=dtype,
        alias=alias,
        format=format,
        hidden=hidden,
        manage=manage,
        read_only=read_only,
        transform_labels_entity=transform_labels_entity,
        update_after_execution=update_after_execution,
        update_progress=update_progress
    )
    return Annotated[pd.Index, entity]


#
def Series(
        index: Union[str, List[str]],
        dtype: BASIC_TYPE,
        #
        alias: str = "",
        format: str = "",
        hidden: Hidden = Hidden.FALSE,
        manage: Manage = Manage.INPUT,
        read_only: bool = False,
        transform_labels_entity: str = "",
        update_after_execution: bool = False,
        *,
        update_progress: bool = False,
) -> type:
    """
    Creates an annotation for a *Series* entity, a declaration of a pandas `Series` datastructure.
    Every series must have at least one index.

    Examples
    --------
    Example of creating a `Result` series containing floating-point values, and is managed by Insight as a result
    entity.
    It is indexed by `Indices`, which must have been declared previously.

    >>> Indices: xi.types.Index(...) # previous declaration
    ... Result: xi.types.Series(index=['Indices'], dtype=xi.real,
    ...                   manage=xi.Manage.RESULT, alias='Result Array')


    Parameters
    ----------
    index : Union[str, List[str]]
        The name of the index to use, or list of names for multiple indices. The same index may appear in the list
        multiple times.
    dtype : BASIC_TYPE
        The data-type.
    alias : str = ""
        Used to provide an alternative name for an entity in the UI.
        The value is used in place of the entity name where appropriate in the UI.
    format : str = ""
        The formatting string used for displaying numeric values.
    hidden : Hidden = Hidden.FALSE
        Indicates whether the UI should hide the entity where appropriate.
    manage : Manage = Manage.INPUT
        How and whether Insight handles an entity. Defines how the system manages the entity data.
    read_only : bool = False
        Whether an entity is readonly. Specifies that the value(s) of the entity cannot be modified. See also
        `hidden`.
    transform_labels_entity : str = ""
        An entity in the schema to be used as a labels entity. The value is the name of the entity.
        The type of the index set of the labels entity must match the data type of this entity.
        The data type of the labels entity can be any primitive type.
    update_after_execution : bool = False
        Whether the value of the entity in the scenario is updated with the value of
        the corresponding model entity at the end of the scenario execution.
        If `True` the value of the entity is updated to correspond with the model entity after execution.
    update_progress : bool = False
        Whether the value of the entity in the scenario is sent on progress updates.
        If `True` the value of the entity will be written back to the Insight repository when
        :fct-ref:`insight.send_progress_update` is called from an execution mode where the `send_progress`
        attribute is `True`.

    Notes
    -----
    This function returns an `Annotated` type containing the `Series` entity object; for example,
    `xi.types.Series(index='idx', dtype=xi.integer)` is equivalent to
    `Annotated[pandas.Series, xi.Series(index='idx', dtype=xi.integer)]`.

    Parameters before `update_progress` can be specified positionally for reasons of backwards compatibility,
    but it's recommended that you always use named arguments if you're specifying parameters other than
    `dtype` and `alias`.

    See Also
    --------
    types.Index
    Series
    """
    entity = xi.Series(
        index=index,
        dtype=dtype,
        alias=alias,
        format=format,
        hidden=hidden,
        manage=manage,
        read_only=read_only,
        transform_labels_entity=transform_labels_entity,
        update_after_execution=update_after_execution,
        update_progress=update_progress
    )
    return Annotated[pd.Series, entity]


#
def DataFrame(
        index: Union[str, List[str]],
        columns: Union[xi.Column, List[xi.Column]]
) -> type:
    """
    Creates an annotation for a *DataFrame* entity.

    Examples
    --------
    Example declaring a data-frame `MixedTable` which has three columns.

    >>> MixedTable: xi.types.DataFrame(index='Years', columns=[
    ...     xi.Column("IntCol", dtype=xi.integer, default=-1,
    ...               alias="Input Integer Column"),
    ...     xi.Column("StrCol", dtype=xi.string,
    ...               alias="Input String Column",
    ...               update_after_execution=True),
    ...     xi.Column("ResultCol", dtype=xi.real,
    ...               alias="Result Real Column",
    ...               manage=xi.Manage.RESULT)
    ... ])

    Parameters
    ----------
    index : Union[str, List[str]]
        The name of the index to use, or list of names for multiple indices. The same index may appear in the list
        multiple times.
    columns : Union[Column, List[Column]])
        The columns which make up this data-frame.

    Notes
    -----
    This function returns an `Annotated` type containing the `DataFrame` entity object; for example,
    `xi.types.DataFrame(index='idx', columns=[xi.Column("c1", dtype=xi.integer)])` is equivalent to
    `Annotated[pandas.DataFrame, xi.DataFrame(index='idx', columns=[xi.Column("c1", dtype=xi.integer)])]`.

    See Also
    --------
    Column
    types.Index
    """
    entity = xi.DataFrame(
        index=index,
        columns=columns
    )
    return Annotated[pd.DataFrame, entity]
