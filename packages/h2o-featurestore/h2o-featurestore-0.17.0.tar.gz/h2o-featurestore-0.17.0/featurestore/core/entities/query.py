from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from functools import reduce
from typing import TYPE_CHECKING, List, Optional, Union

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from . import feature_ref as fref
from . import feature_set_ref as fsref
from .transformation_function import TransformationFunction, TransformedFeature

if TYPE_CHECKING:  # Only imports the below statements during type checking
    from .feature import Feature
    from .feature_set import FeatureSet


class SelectedFeatureWithTransformation:
    def __init__(self, feature: fref.FeatureRef, transformation: Optional[TransformationFunction]):
        self._feature: fref.FeatureRef = feature
        self._transformation = transformation

    @property
    def feature_set_ref(self):
        return self._feature.feature_set_ref

    @property
    def name(self):
        return self._feature.name

    @property
    def transformation(self):
        return self._transformation.function_name if self._transformation else None

    @classmethod
    def create_from(
        cls,
        feature: Union[Feature, SelectedFeatureWithTransformation, TransformedFeature],
    ):
        if isinstance(feature, SelectedFeatureWithTransformation):
            return feature
        if isinstance(feature, TransformedFeature):
            return SelectedFeatureWithTransformation(feature.feature, feature.transformation)

        return SelectedFeatureWithTransformation(feature._reference(), None)

    def __repr__(self):
        if self.transformation:
            return f"{self._transformation.function_name}({self._feature})"
        else:
            return f"{self._feature}"


class Query:
    def __init__(
        self,
        select: SelectedFrom,
        joins: Optional[list[Join]] = None,
        filter: Optional[Condition] = None,
    ):
        self._select = select
        if joins:
            self._joins = joins
        else:
            self._joins = []
        self._filter = filter

    def __repr__(self):
        return f"select: {self._select}, joins: {self._joins}, filter: {self._filter}"

    @classmethod
    def select(
        cls,
        features: list[Union[Feature, SelectedFeatureWithTransformation, TransformedFeature]],
    ):
        return Select([SelectedFeatureWithTransformation.create_from(feature) for feature in features])

    def filter(self, condition: Condition):
        if self._filter:
            new_condition = self._filter & condition
        else:
            new_condition = condition

        return Query(self._select, self._joins, new_condition)

    def _join(self, feature_set: Union[FeatureSet, fsref.FeatureSetRef], alias, join_type: JoinType) -> OpenedJoin:
        return OpenedJoin(
            self,
            feature_set if isinstance(feature_set, fsref.FeatureSetRef) else feature_set._reference(),
            alias,
            join_type,
        )

    def join(self, feature_set: Union[FeatureSet, fsref.FeatureSetRef], alias) -> OpenedJoin:
        return self._join(feature_set, alias, JoinType.INNER)

    def left_join(self, feature_set: Union[FeatureSet, fsref.FeatureSetRef], alias) -> OpenedJoin:
        return self._join(feature_set, alias, JoinType.LEFT)

    def _to_proto(self) -> pb.FeatureQuery:

        fs_to_alias = dict(
            [(join._feature_set, join._alias) for join in self._joins if join._alias]
            + [(self._select.feature_set, self._select.alias)]
            if self._select.alias
            else []
        )

        return pb.FeatureQuery(
            selected_features=[
                pb.SelectedFeature(
                    prefix=fs_to_alias.get(feature.feature_set_ref, ""),
                    feature=feature.name,
                    transformation=feature.transformation,
                )
                for feature in self._select.features
            ],
            from_feature_set=pb.FeatureQuery.From(
                feature_set=pb.VersionedId(
                    id=self._select.feature_set.id,
                    major_version=self._select.feature_set.major_version,
                ),
                alias=self._select.alias,
            ),
            where=self._filter._to_proto(fs_to_alias) if self._filter else None,
            join=[join._to_proto(fs_to_alias) for join in self._joins],
        )

    @classmethod
    def _from_proto(cls, feature_query: pb.FeatureQuery) -> Query:
        def to_feature_set_ref(version_id: pb.VersionedId) -> fsref.FeatureSetRef:
            return fsref.FeatureSetRef(version_id.id, version_id.major_version)

        def to_feature_ref(
            selected_feature: pb.SelectedFeature,
            aliases: dict[str, fsref.FeatureSetRef],
        ) -> fref.FeatureRef:
            return fref.FeatureRef(selected_feature.feature, aliases.get(selected_feature.prefix))

        from_feature_set = to_feature_set_ref(feature_query.from_feature_set.feature_set)

        alias_to_fs = dict(
            [(feature_query.from_feature_set.alias, from_feature_set)]
            if len(feature_query.from_feature_set.alias) > 0
            else []
            + [(join.alias, to_feature_set_ref(join.feature_set)) for join in feature_query.join if len(join.alias) > 0]
        )

        selected_features = [
            SelectedFeatureWithTransformation(
                to_feature_ref(feature, alias_to_fs),
                TransformationFunction(feature.transformation) if feature.transformation else None,
            )
            for feature in feature_query.selected_features
        ]

        def join_proto(query: Query, join: pb.FeatureQuery.Join) -> Query:
            if join.join_type == pb.FeatureQueryJoinType.FEATURE_QUERY_JOIN_INNER:
                join_type = JoinType.INNER
            elif join.join_type == pb.FeatureQueryJoinType.FEATURE_QUERY_JOIN_LEFT:
                join_type = JoinType.LEFT
            else:
                raise Exception(f"Unsupported join type {join.join_type}")

            joined = query._join(to_feature_set_ref(join.feature_set), join.alias, join_type).on(
                to_feature_ref(join.on[0].left, alias_to_fs),
                to_feature_ref(join.on[0].right, alias_to_fs),
            )
            return reduce(
                lambda j, on: j.on(
                    to_feature_ref(on.left, alias_to_fs),
                    to_feature_ref(on.right, alias_to_fs),
                ),
                join.on[1:],
                joined,
            ).end()

        query_after_join = reduce(
            join_proto,
            feature_query.join,
            Query.select(selected_features).from_feature_set(from_feature_set, feature_query.from_feature_set.alias),
        )

        if feature_query.HasField("where"):
            return query_after_join.filter(Condition._from_proto(feature_query.where, alias_to_fs))
        else:
            return query_after_join


class Select:
    def __init__(self, features: list[SelectedFeatureWithTransformation]):
        self._features = features

    def from_feature_set(
        self,
        feature_set: Union[FeatureSet, fsref.FeatureSetRef],
        alias: Optional[str] = None,
    ):
        return Query(
            select=SelectedFrom(
                self._features,
                feature_set if isinstance(feature_set, fsref.FeatureSetRef) else feature_set._reference(),
                alias,
            )
        )


class SelectedFrom:
    def __init__(
        self,
        features: list[SelectedFeatureWithTransformation],
        feature_set: fsref.FeatureSetRef,
        alias: Optional[str],
    ):
        self.features = features
        self.feature_set = feature_set
        self.alias = alias

    def __repr__(self):
        return f"features: {self.features}, feature_set: {self.feature_set}"


class LogicOperator(Enum):
    AND = pb.FeatureFilterLogicOperator.FEATURE_FILTER_LOGIC_OPERATOR_AND
    OR = pb.FeatureFilterLogicOperator.FEATURE_FILTER_LOGIC_OPERATOR_OR

    @classmethod
    def _from_proto(cls, proto_value: pb.FeatureFilterLogicOperator.ValueType) -> LogicOperator:
        found_values = [member for name, member in LogicOperator.__members__.items() if member.value == proto_value]
        if len(found_values) < 1:
            raise Exception(f"Not supported value {proto_value}")
        return found_values[0]


class FilterOperator(Enum):
    EQ = pb.FeatureFilterOperator.FEATURE_FILTER_OPERATOR_EQ
    NE = pb.FeatureFilterOperator.FEATURE_FILTER_OPERATOR_NE
    LT = pb.FeatureFilterOperator.FEATURE_FILTER_OPERATOR_LT
    LE = pb.FeatureFilterOperator.FEATURE_FILTER_OPERATOR_LE
    GT = pb.FeatureFilterOperator.FEATURE_FILTER_OPERATOR_GT
    GE = pb.FeatureFilterOperator.FEATURE_FILTER_OPERATOR_GE

    @classmethod
    def _from_proto(cls, proto_value: pb.FeatureFilterOperator.ValueType) -> FilterOperator:
        found_values = [member for name, member in FilterOperator.__members__.items() if member.value == proto_value]
        if len(found_values) < 1:
            raise Exception(f"Not supported value {proto_value}")
        return found_values[0]


class Condition(ABC):
    def __and__(self, condition: Condition) -> Condition:
        return LogicCondition(self, condition, LogicOperator.AND)

    def __or__(self, condition: Condition) -> Condition:
        return LogicCondition(self, condition, LogicOperator.OR)

    @abstractmethod
    def _to_proto(self, aliases: dict[fsref.FeatureSetRef, str]):
        raise NotImplementedError("Method `_to_proto` needs to be implemented by the child class")

    @classmethod
    def _from_proto(cls, where: pb.FilterConditionUnion, aliases: dict[str, fsref.FeatureSetRef]) -> Condition:
        if where.HasField("filter"):
            return FilterCondition(
                fref.FeatureRef(
                    where.filter.feature.feature,
                    aliases.get(where.filter.feature.prefix),
                ),
                FilterOperator._from_proto(where.filter.operator),
                where.filter.value,
            )
        else:
            return LogicCondition(
                Condition._from_proto(where.logic.left, aliases),
                Condition._from_proto(where.logic.right, aliases),
                LogicOperator._from_proto(where.logic.logic_operator),
            )


class LogicCondition(Condition):
    def __init__(
        self,
        left_condition: Condition,
        right_condition: Condition,
        operator: LogicOperator,
    ):
        self._left_condition = left_condition
        self._right_condition = right_condition
        self._operator = operator

    def __repr__(self):
        return f"{self._left_condition} {self._operator} {self._right_condition}"

    def _to_proto(self, aliases: dict[fsref.FeatureSetRef, str]):
        pb.FilterConditionUnion(
            logic=pb.FeatureFilterLogic(
                left=self._left_condition._to_proto(aliases),
                right=self._right_condition._to_proto(aliases),
                logic_operator=self._operator.value,
            )
        )


class FilterCondition(Condition):
    def __init__(self, selected_feature: fref.FeatureRef, operator: FilterOperator, value: str):
        self._selected_feature = selected_feature
        self._operator = operator
        self._value = value

    def __repr__(self):
        return f"{self._selected_feature} {self._operator} {self._value}"

    def _to_proto(self, aliases: dict[fsref.FeatureSetRef, str]) -> pb.FilterConditionUnion:
        return pb.FilterConditionUnion(
            filter=pb.FeatureFilter(
                feature=pb.SelectedFeature(
                    prefix=aliases.get(self._selected_feature.feature_set_ref, ""),
                    feature=(self._selected_feature.name),
                ),
                operator=self._operator.value,
                value=self._value,
            )
        )


class On:
    def __init__(
        self,
        left_feature: Union[Feature, fref.FeatureRef],
        right_feature: Union[Feature, fref.FeatureRef],
    ):
        if isinstance(left_feature, fref.FeatureRef):
            self._left_feature = left_feature
        else:
            self._left_feature = left_feature._reference()
        if isinstance(right_feature, fref.FeatureRef):
            self._right_feature = right_feature
        else:
            self._right_feature = right_feature._reference()

    def __repr__(self):
        return f"{self._left_feature} == {self._right_feature}"


class OpenedJoin:
    def __init__(self, query, feature_set: fsref.FeatureSetRef, alias: str, join_type: JoinType):
        self.__query = query
        self.__feature_set = feature_set
        self.__alias = str(alias or None)
        self.__join_type = join_type

    def on(
        self,
        left_feature: Union[Feature, fref.FeatureRef],
        right_feature: Union[Feature, fref.FeatureRef],
    ) -> Join:
        return Join(self.__query, self.__feature_set, self.__alias, [On(left_feature, right_feature)], self.__join_type)


class JoinType(Enum):
    INNER = 0
    LEFT = 1

    def _to_proto(self):
        if self == JoinType.INNER:
            return pb.FeatureQueryJoinType.FEATURE_QUERY_JOIN_INNER
        elif self == JoinType.LEFT:
            return pb.FeatureQueryJoinType.FEATURE_QUERY_JOIN_LEFT
        else:
            raise Exception(f"Unsupported type {self.name}")


class Join:
    def __init__(
        self, query: Query, feature_set: fsref.FeatureSetRef, alias: Optional[str], on: List[On], join_type: JoinType
    ):
        self._query = query
        self._feature_set = feature_set
        self._alias = str(alias or None)
        self._on = on
        self._join_type = join_type

    def __repr__(self):
        return f"feature_set: {self._feature_set}, alias: {self._alias}, on: {self._on}, join_type: {self._join_type}"

    def on(
        self,
        left_feature: Union[Feature, fref.FeatureRef],
        right_feature: Union[Feature, fref.FeatureRef],
    ) -> Join:
        return Join(
            self._query, self._feature_set, self._alias, self._on + [(On(left_feature, right_feature))], self._join_type
        )

    def end(self) -> Query:
        return Query(self._query._select, self._query._joins + [self], self._query._filter)

    def _to_proto(self, aliases: dict[fsref.FeatureSetRef, str]) -> pb.FeatureQuery.Join:
        return pb.FeatureQuery.Join(
            feature_set=pb.VersionedId(id=self._feature_set.id, major_version=self._feature_set.major_version),
            alias=self._alias,
            on=[
                pb.FeatureQuery.Join.On(
                    left=pb.SelectedFeature(
                        prefix=aliases.get(on._left_feature.feature_set_ref, ""),
                        feature=on._left_feature.name,
                    ),
                    right=pb.SelectedFeature(
                        prefix=aliases.get(on._right_feature.feature_set_ref, ""),
                        feature=on._right_feature.name,
                    ),
                )
                for on in self._on
            ],
            join_type=self._join_type._to_proto(),
        )
