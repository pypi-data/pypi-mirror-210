import logging
from copy import copy
from functools import wraps
from time import time
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from sgqlc.operation import Fragment, Operation

from .core.kb_sync.kb_iterator_config import KBIteratorConfig
from .core.kb_sync.object_time_interval import ObjectTimeInterval
from .core.type_mapper.data_model.base_data_model import TypeMapping
from .core.type_mapper.modules.type_mapping_loader.type_mapping_loader import TypeMappingLoader
from .core.type_mapper.modules.type_mapping_loader.type_mapping_loader_interface import TypeMappingLoaderInterface
from .core.values.value_mapping import get_map_helper
from .providers.gql_providers import AbstractGQLClient
from .schema import tcontroller_api_schema as tc
from .schema import utils_api_schema as uas
from .schema.api_schema import (
    ComponentValueInput,
    CompositeConcept,
    CompositeConceptWidgetRowPagination,
    CompositePropertyTypeFilterSettings,
    CompositePropertyTypeSorting,
    CompositePropertyValueTemplate,
    CompositePropertyValueType,
    CompositeValue,
    Concept,
    ConceptCandidateFact,
    ConceptFact,
    ConceptFactPagination,
    ConceptFilterSettings,
    ConceptLink,
    ConceptLinkCreationMutationInput,
    ConceptLinkFilterSettings,
    ConceptLinkPagination,
    ConceptLinkPropertyInput,
    ConceptLinkPropertyTypeCreationInput,
    ConceptLinkPropertyTypeUpdateInput,
    ConceptLinkType,
    ConceptLinkTypeFilterSettings,
    ConceptLinkTypePagination,
    ConceptLinkTypeSorting,
    ConceptMergeInput,
    ConceptMutationInput,
    ConceptPagination,
    ConceptProperty,
    ConceptPropertyCreateInput,
    ConceptPropertyFilterSettings,
    ConceptPropertyPagination,
    ConceptPropertyType,
    ConceptPropertyTypeCreationInput,
    ConceptPropertyTypeFilterSettings,
    ConceptPropertyTypePagination,
    ConceptPropertyTypeSorting,
    ConceptPropertyUpdateInput,
    ConceptPropertyValueType,
    ConceptPropertyValueTypeFilterSettings,
    ConceptPropertyValueTypePagination,
    ConceptPropertyValueTypeSorting,
    ConceptPropertyValueTypeUpdateInput,
    ConceptSorting,
    ConceptType,
    ConceptTypeFilterSettings,
    ConceptTypePagination,
    ConceptTypeSorting,
    ConceptUnmergeInput,
    ConceptUpdateInput,
    DateTimeValue,
    DateTimeValueInput,
    Document,
    DocumentFilterSettings,
    DocumentGrouping,
    DocumentLinkFilterSetting,
    DocumentSorting,
    DoubleValue,
    DoubleValueInput,
    ExtraSettings,
    FactInput,
    IntValue,
    IntValueInput,
    LinkValue,
    LinkValueInput,
    Mutation,
    PerformSynchronously,
    PropertyFilterSettings,
    Query,
    SortDirection,
    State,
    Story,
    StoryPagination,
    StringFilter,
    StringLocaleValue,
    StringLocaleValueInput,
    StringValue,
    StringValueInput,
    TimestampInterval,
    ValueInput,
)
from .schema.crawlers_api_schema import Crawler, CrawlerPagination
from .schema.crawlers_api_schema import Query as CrQuery
from .tdm_builder.tdm_builder import AbstractTdmBuilder

logger = logging.getLogger(__name__)


def check_utils_gql_client(f):
    @wraps(f)
    def wrapper(self: "TalismanAPIAdapter", *args, **kwargs):
        if self._utils_gql_client is None:
            raise Exception("Utils methods cannot be used because the corresponding gql_client is not specified.")
        return f(self, *args, **kwargs)

    return wrapper


class TalismanAPIAdapter:
    def __init__(
        self,
        gql_client: AbstractGQLClient,
        type_mapping: Optional[Union[str, dict, TypeMapping]] = None,
        type_mapping_loader: Optional[TypeMappingLoaderInterface] = None,
        tdm_builder: Optional[AbstractTdmBuilder] = None,
        utils_gql_client: Optional[AbstractGQLClient] = None,
        kb_iterator_config: Optional[KBIteratorConfig] = None,
        limit: int = 100,
        perform_synchronously: bool = True,
    ) -> None:
        self._gql_client = gql_client
        self._utils_gql_client = utils_gql_client
        self._type_mapping_loader = type_mapping_loader if type_mapping_loader else TypeMappingLoader(logger)
        self._type_mapping = self._type_mapping_loader.load_type_mapping(type_mapping)
        self._limit = limit
        self._perform_synchronously = perform_synchronously

        self.document_fields_truncated = (
            "id",
            "external_url",
            "uuid",
        )
        self.document_fields = (
            "id",
            "title",
            "external_url",
            "publication_author",
            "publication_date",
            "internal_url",
            "markers",
            "system_registration_date",
            "system_update_date",
            "notes",
            "access_level",
            "trust_level",
            "uuid",
        )

        self.document_text_fields_truncated = ("text",)
        self.document_text_fields = (
            "node_id",
            "text",
        )
        self.document_text_metadata_fields = ("paragraph_type",)

        self.document_platform_fields = (
            "id",
            "name",
        )
        self.document_account_fields = (
            "id",
            "name",
        )

        self.user_fields = ("id",)

        self.concept_fields = (
            "id",
            "name",
            "notes",
            "metric",
            "markers",
            "system_registration_date",
            "system_update_date",
        )
        self.concept_type_fields = ("id", "name")

        self.concept_property_fields = ("is_main", "id", "system_registration_date")
        self.concept_property_type_fields_truncated = ("id",)
        self.concept_property_type_fields = ("id", "name")
        self.cpvt_fields_truncated = ("id", "name", "value_type")
        self.cpvt_fields = ("id", "name", "value_type", "value_restriction", "pretrained_nercmodels")

        self.concept_link_fields = ("id", "notes")
        self.concept_link_concept_from_fields = ("id",)
        self.concept_link_concept_to_fields = ("id",)
        self.concept_link_type_fields = ("id", "name", "is_directed", "is_hierarchical")
        self.concept_link_type_fields_truncated = ("id", "name", "is_directed")

        self.concept_fact_fields = ("id",)

        self.composite_concept_widget_type = ("id", "name")
        self.composite_concept_widget_type_columns_info = ("name",)

        self.date_time_value_date_fields = ("year", "month", "day")
        self.date_time_value_time_fields = ("hour", "minute", "second")

        self.pipeline_config_fields = ("id", "description")

        self.pipeline_topic_fields = ("topic", "description", "stopped", "metrics", "pipeline")
        self.pipeline_metrics_fields = ("duplicate", "failed", "messages", "ok")

        self.tdm_builder = tdm_builder

        if kb_iterator_config:
            self.kb_iterator_config = kb_iterator_config
        else:
            self.kb_iterator_config = KBIteratorConfig(1000, 1609448400)  # Fri Jan 01 2021 00:00:00 GMT+0300

    def get_tdm_builder(self) -> Optional[AbstractTdmBuilder]:
        return self.tdm_builder

    @property
    def type_mapping(self):
        return self._type_mapping

    @type_mapping.setter
    def type_mapping(self, new_type_mapping: TypeMapping):
        self._type_mapping = new_type_mapping

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, new_limit: int):
        self._limit = new_limit

    @property
    def perform_synchronously(self):
        return self._perform_synchronously

    @perform_synchronously.setter
    def perform_synchronously(self, new_perform_synchronously: bool):
        self._perform_synchronously = new_perform_synchronously

    def get_take_value(self, take: Optional[int]) -> int:
        return self.limit if take is None else take

    def get_perform_synchronously_value(self, perform_synchronously: Optional[bool]) -> bool:
        return self.perform_synchronously if perform_synchronously is None else perform_synchronously

    def _configure_property_value_type_fields(self, graphql_value, truncated: bool = True):
        conpvt_frag: Fragment = Fragment(ConceptPropertyValueType, "ConceptPropertyValueType")
        for f in self.cpvt_fields_truncated if truncated else self.cpvt_fields:
            conpvt_frag.__getattr__(f)()

        compvt_frag = Fragment(CompositePropertyValueTemplate, "CompositePropertyValueTemplate")
        compvt_frag.__fields__("id", "name")
        compvt_frag.component_value_types()

        graphql_value.__fragment__(conpvt_frag)
        graphql_value.__fragment__(compvt_frag)

    def _configure_output_value_fields(self, graphql_value):
        dtv_frag = Fragment(DateTimeValue, "DateTimeFull")
        dtv_frag.date().__fields__(*self.date_time_value_date_fields)
        dtv_frag.time().__fields__(*self.date_time_value_time_fields)

        slv_frag = Fragment(StringLocaleValue, "StringLocaleFull")
        slv_frag.value()
        slv_frag.locale()

        sv_frag = Fragment(StringValue, "StringFull")
        sv_frag.value()

        lv_frag = Fragment(LinkValue, "LinkFull")
        lv_frag.link()

        dv_frag = Fragment(DoubleValue, "DoubleFull")
        dv_frag.value(__alias__="double")

        iv_frag = Fragment(IntValue, "IntFull")
        iv_frag.value(__alias__="number")

        cv_frag = Fragment(CompositeValue, "CompFull")
        cv_frag.list_value().id()
        cv_frag.list_value().property_value_type()
        cv_frag.list_value().value().__fragment__(slv_frag)
        cv_frag.list_value().value().__fragment__(sv_frag)
        cv_frag.list_value().value().__fragment__(lv_frag)
        cv_frag.list_value().value().__fragment__(dv_frag)
        cv_frag.list_value().value().__fragment__(iv_frag)
        cv_frag.list_value().value().__fragment__(dtv_frag)

        graphql_value.__fragment__(slv_frag)
        graphql_value.__fragment__(sv_frag)
        graphql_value.__fragment__(lv_frag)
        graphql_value.__fragment__(dv_frag)
        graphql_value.__fragment__(iv_frag)
        graphql_value.__fragment__(dtv_frag)
        graphql_value.__fragment__(cv_frag)

    def _configure_output_concept_fields(
        self,
        concept_object,
        with_aliases=False,
        with_properties=False,
        with_links=False,
        with_link_properties=False,
        with_facts=False,
        with_potential_facts=False,
    ):
        concept_object.__fields__(*self.concept_fields)
        concept_object.concept_type.__fields__(*self.concept_type_fields)
        if with_aliases:
            sv_frag = Fragment(StringValue, "StringFull")
            sv_frag.value()
            concept_object.list_alias.value.__fragment__(sv_frag)
        if with_properties:
            pcp: ConceptPropertyPagination = concept_object.pagination_concept_property(
                offset=0, limit=10000, filter_settings={}
            )
            lcp = pcp.list_concept_property()
            lcp.__fields__(*self.concept_property_fields)
            lcp.property_type().__fields__(*self.concept_property_type_fields)
            self._configure_output_value_fields(lcp.value)
        if with_links:
            pcl: ConceptLinkPagination = concept_object.pagination_concept_link(
                offset=0, limit=10000, filter_settings={}
            )
            self._configure_output_link_fields(pcl.list_concept_link(), with_link_properties=with_link_properties)
        if with_facts:
            pcf: ConceptFactPagination = concept_object.pagination_concept_fact(
                offset=0, limit=10000, filter_settings={}
            )
            lcf = pcf.list_concept_fact()
            lcf.__fields__(*self.concept_fact_fields)
            d = lcf.document()
            d.__fields__(*self.document_fields)
            dm = d.metadata()
            dm.platform().__fields__(*self.document_platform_fields)
            dm.account().__fields__(*self.document_account_fields)
        if with_potential_facts:
            lccf: List[ConceptCandidateFact] = concept_object.list_concept_candidate_fact()
            lccf.__fields__(*self.concept_fact_fields)
            d = lccf.document()
            d.__fields__(*self.document_fields)
            dm = d.metadata()
            dm.platform().__fields__(*self.document_platform_fields)
            dm.account().__fields__(*self.document_account_fields)

    def _configure_output_link_fields(self, link_object, with_link_properties=False):
        link_object.__fields__(*self.concept_link_fields)
        link_object.concept_from().__fields__(*self.concept_link_concept_from_fields)
        link_object.concept_to().__fields__(*self.concept_link_concept_to_fields)
        link_object.concept_link_type().__fields__(*self.concept_link_type_fields_truncated)
        if with_link_properties:
            pcp: ConceptPropertyPagination = link_object.pagination_concept_link_property(
                offset=0, limit=10000, filter_settings={}
            )
            lcp = pcp.list_concept_property()
            lcp.__fields__(*self.concept_property_fields)
            lcp.property_type().__fields__(*self.concept_property_type_fields)
            self._configure_output_value_fields(lcp.value)

    def _create_concept_with_input(
        self,
        form: ConceptMutationInput,
        with_properties=False,
        with_links=False,
        with_link_properties=False,
        perform_synchronously: Optional[bool] = None,
    ) -> Concept:
        perform_synchronously = self.get_perform_synchronously_value(perform_synchronously)
        op = Operation(Mutation)
        ac = op.add_concept(
            performance_control=PerformSynchronously(perform_synchronously=perform_synchronously), form=form
        )
        self._configure_output_concept_fields(
            ac, with_properties=with_properties, with_links=with_links, with_link_properties=with_link_properties
        )
        res = self._gql_client.execute(op)
        res = op + res

        if self.tdm_builder is not None:
            self.tdm_builder.add_concept_fact(res.add_concept)

        return res.add_concept

    def _get_components_mapping(
        self, component_values: Dict[str, str], component_value_types: List[CompositePropertyValueType]
    ) -> Dict[str, CompositePropertyValueType]:
        components_type_mapping = {}
        for component_value in component_values:
            for component_value_type in component_value_types:
                if component_value_type.name != component_values[component_value]:
                    continue
                components_type_mapping[component_value] = component_value_type
        return components_type_mapping

    def _get_value_input(
        self, values: dict, components_type_mapping: Dict[str, CompositePropertyValueType]
    ) -> List[ComponentValueInput]:
        value_input = []
        for field in values:
            if field not in components_type_mapping:
                continue
            value_id = components_type_mapping[field].id
            value_input.append(
                ComponentValueInput(
                    id=value_id,
                    value=get_map_helper(components_type_mapping[field].value_type.value_type).get_value_input(
                        values[field]
                    ),
                )
            )
        return value_input

    def _configure_pipeline_topic_fields(self, kafka_topic: tc.KafkaTopic):
        kafka_topic.__fields__(*self.pipeline_topic_fields)
        kafka_topic.metrics().__fields__(*self.pipeline_metrics_fields)
        kafka_topic.pipeline().pipeline_config().__fields__(*self.pipeline_config_fields)

    def get_all_documents(
        self,
        grouping: DocumentGrouping = "none",
        filter_settings: Optional[DocumentFilterSettings] = None,
        direction: SortDirection = "descending",
        sort_field: DocumentSorting = "score",
        extra_settings: Optional[ExtraSettings] = None,
        with_extended_information: bool = False,
    ) -> Iterable[Story]:
        if filter_settings is None:
            filter_settings = DocumentFilterSettings()
        if extra_settings is None:
            extra_settings = ExtraSettings()

        total = self.get_documents_count(filter_settings=filter_settings)

        if total > self.kb_iterator_config.max_total_count:
            had_creation_date = hasattr(filter_settings, "registration_date")
            old_timestamp_interval = None
            if had_creation_date:
                old_timestamp_interval = copy(filter_settings.registration_date)
            start: int = getattr(old_timestamp_interval, "start", self.kb_iterator_config.earliest_created_time)
            end: int = getattr(old_timestamp_interval, "end", int(time()))
            middle: int = (end + start) // 2

            for next_start, next_end in (start, middle), (middle + 1, end):
                if next_start == start and next_end == end:
                    logger.info(
                        f"Processed only {self.kb_iterator_config.max_total_count} documents, "
                        f"{total - self.kb_iterator_config.max_total_count} ignored"
                    )
                    continue
                filter_settings.registration_date = TimestampInterval(start=next_start, end=next_end)
                yield from self.get_all_documents(
                    grouping=grouping,
                    filter_settings=filter_settings,
                    direction=direction,
                    sort_field=sort_field,
                    extra_settings=extra_settings,
                    with_extended_information=with_extended_information,
                )

            if had_creation_date:
                filter_settings.registration_date = old_timestamp_interval
            else:
                delattr(filter_settings, "registration_date")
            return
        elif not total:
            return

        documents: Iterable = [None]
        i: int = 0
        while documents:
            documents = self.get_documents(
                skip=i * self._limit,
                take=self._limit,
                grouping=grouping,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
                extra_settings=extra_settings,
                with_extended_information=with_extended_information,
            )
            yield from documents
            i += 1

    def get_documents(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        grouping: DocumentGrouping = "none",
        filter_settings: Optional[DocumentFilterSettings] = None,
        direction: SortDirection = "descending",
        sort_field: DocumentSorting = "score",
        extra_settings: Optional[ExtraSettings] = None,
        with_extended_information: bool = False,
    ) -> Sequence[Story]:
        take = self.get_take_value(take)
        pagination_story_kwargs = {}
        if filter_settings is None:
            filter_settings = DocumentFilterSettings()
        if extra_settings is None:
            extra_settings = ExtraSettings()

        op = Operation(Query)
        ps: StoryPagination = op.pagination_story(
            offset=skip,
            limit=take,
            grouping=grouping,
            filter_settings=filter_settings,
            direction=direction,
            sort_field=sort_field,
            extra_settings=extra_settings,
            **pagination_story_kwargs,
        )
        ps.list_story().list_document().__fields__(*self.document_fields_truncated)
        m = ps.list_story().main()
        if with_extended_information:
            m.__fields__(*self.document_fields)
            mdm = m.metadata()
            mdm.platform().__fields__(*self.document_platform_fields)
            mdm.account().__fields__(*self.document_account_fields)
        else:
            m.__fields__(*self.document_fields_truncated)
        m.text().__fields__(*self.document_text_fields_truncated)

        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_story.list_story

    def get_documents_count(self, filter_settings: Optional[DocumentFilterSettings] = None) -> int:
        if filter_settings is None:
            filter_settings = DocumentFilterSettings()

        op = Operation(Query)
        ps: StoryPagination = op.pagination_story(
            limit=1, filter_settings=filter_settings, extra_settings=ExtraSettings()
        )
        ps.show_total()
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_story.show_total

    def get_documents_by_limit_offset_filter_extra_settings(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[DocumentFilterSettings] = None,
        extra_settings: Optional[ExtraSettings] = None,
    ) -> Sequence[Story]:
        take = self.get_take_value(take)
        op = Operation(Query)
        ps: StoryPagination = op.pagination_story(
            offset=skip,
            limit=take,
            extra_settings=extra_settings if extra_settings else ExtraSettings(),
            filter_settings=filter_settings if filter_settings else DocumentFilterSettings(),
        )
        ps.list_story().list_document().__fields__(*self.document_fields_truncated)
        m = ps.list_story().main()
        m.__fields__(*self.document_fields_truncated)
        m.text().__fields__(*self.document_text_fields_truncated)

        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_story.list_story

    def get_document(self, document_id: str) -> Document:
        op = Operation(Query)
        d: Document = op.document(id=document_id)
        d.__fields__(*self.document_fields)
        d.last_updater().__fields__(*self.user_fields)
        d.metadata().platform().__fields__(*self.document_platform_fields)
        d.metadata().account().__fields__(*self.document_account_fields)
        d.creator().__fields__(*self.user_fields)
        dt = d.text(show_hidden=True)
        dt.__fields__(*self.document_text_fields)
        dt.metadata().__fields__(*self.document_text_metadata_fields)
        dt.metadata().text_translations().text()
        dt.metadata().text_translations().language().id()
        cd = d.list_child()
        cd.__fields__(*self.document_fields)
        cd.last_updater().__fields__(*self.user_fields)
        cd.metadata().platform().__fields__(*self.document_platform_fields)
        cd.metadata().account().__fields__(*self.document_account_fields)
        cd.creator().__fields__(*self.user_fields)
        cdt = cd.text(show_hidden=True)
        cdt.__fields__(*self.document_text_fields)
        cdt.metadata().__fields__(*self.document_text_metadata_fields)
        fc = d.list_concept_fact()
        fc.__fields__(*self.concept_fact_fields)

        res = self._gql_client.execute(op)
        res = op + res
        return res.document

    def get_concept_count(self, filter_settings: Optional[ConceptFilterSettings] = None) -> int:
        op = Operation(Query)
        pc: ConceptPagination = op.pagination_concept(
            filter_settings=filter_settings if filter_settings else ConceptFilterSettings()
        )
        pc.show_total()
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept.show_total

    def get_concept_link_count(self, filter_settings: Optional[ConceptLinkFilterSettings] = None) -> int:
        op = Operation(Query)
        pcl: ConceptLinkPagination = op.pagination_concept_link(
            filter_settings=filter_settings if filter_settings else ConceptLinkFilterSettings()
        )
        pcl.total()
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_link.total

    def get_concept(
        self,
        concept_id: str,
        with_aliases: bool = False,
        with_properties: bool = True,
        with_links: bool = True,
        with_link_properties: bool = True,
        with_facts: bool = False,
        with_potential_facts: bool = False,
    ) -> Concept:
        op = Operation(Query)
        c: Concept = op.concept(id=concept_id)
        self._configure_output_concept_fields(
            c,
            with_aliases=with_aliases,
            with_properties=with_properties,
            with_links=with_links,
            with_link_properties=with_link_properties,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res

        if self.tdm_builder is not None:
            self.tdm_builder.add_concept_fact(res.concept)

        return res.concept

    def get_concept_property(self, concept_property_id: str) -> Concept:
        op = Operation(Query)
        cp: ConceptProperty = op.concept_property(id=concept_property_id)

        cp.__fields__(*self.concept_property_fields)
        cp.property_type().__fields__(*self.concept_property_type_fields)
        self._configure_output_value_fields(cp.value)
        res = self._gql_client.execute(op)
        res = op + res

        return res.concept_property

    def get_concept_facts(
        self, concept_id: str, filter_settings: Optional[DocumentLinkFilterSetting] = None
    ) -> Sequence[ConceptFact]:
        op = Operation(Query)
        c: Concept = op.concept(id=concept_id)
        pcf: ConceptFactPagination = c.pagination_concept_fact(
            filter_settings=filter_settings if filter_settings else DocumentLinkFilterSetting()
        )
        lcf = pcf.list_concept_fact()
        lcf.__fields__(*self.concept_fact_fields)
        d = lcf.document()
        d.__fields__(*self.document_fields)
        dm = d.metadata()
        dm.platform().__fields__(*self.document_platform_fields)
        dm.account().__fields__(*self.document_account_fields)

        res = self._gql_client.execute(op)
        res = op + res

        return res.concept.pagination_concept_fact.list_concept_fact

    def get_concept_link(self, link_id: str, with_facts: bool = False) -> ConceptLink:
        op = Operation(Query)
        cl: ConceptLink = op.concept_link(id=link_id)
        cl.__fields__(*self.concept_link_fields)
        self._configure_output_concept_fields(cl.concept_from)
        self._configure_output_concept_fields(cl.concept_to)
        cl.concept_link_type.__fields__(*self.concept_link_type_fields_truncated)
        if with_facts:
            cl.__fields__("list_concept_link_fact")
        res = self._gql_client.execute(op)
        res = op + res

        if self.tdm_builder is not None:
            self.tdm_builder.add_link_fact(res.concept_link)

        return res.concept_link

    def get_all_concepts(
        self,
        filter_settings: Optional[ConceptFilterSettings] = None,
        direction: SortDirection = "descending",
        sort_field: ConceptSorting = "score",
        with_aliases: bool = False,
        with_properties: bool = False,
        with_links: bool = False,
        with_link_properties: bool = False,
        with_facts: bool = False,
        with_potential_facts: bool = False,
    ) -> Iterable[Concept]:
        if not filter_settings:
            filter_settings = ConceptFilterSettings()
        total = self.get_concept_count(filter_settings=filter_settings)

        if total > self.kb_iterator_config.max_total_count:
            had_creation_date = hasattr(filter_settings, "creation_date")
            old_timestamp_interval = None
            if had_creation_date:
                old_timestamp_interval = copy(filter_settings.creation_date)
            start: int = getattr(old_timestamp_interval, "start", self.kb_iterator_config.earliest_created_time)
            end: int = getattr(old_timestamp_interval, "end", int(time()))
            middle: int = (end + start) // 2

            for next_start, next_end in (start, middle), (middle + 1, end):
                if next_start == start and next_end == end:
                    logger.info(
                        f"Processed only {self.kb_iterator_config.max_total_count} concepts, "
                        f"{total - self.kb_iterator_config.max_total_count} ignored"
                    )
                    continue
                filter_settings.creation_date = TimestampInterval(start=next_start, end=next_end)
                yield from self.get_all_concepts(
                    filter_settings=filter_settings,
                    direction=direction,
                    sort_field=sort_field,
                    with_aliases=with_aliases,
                    with_properties=with_properties,
                    with_links=with_links,
                    with_link_properties=with_link_properties,
                    with_facts=with_facts,
                    with_potential_facts=with_potential_facts,
                )

            if had_creation_date:
                filter_settings.creation_date = old_timestamp_interval
            else:
                delattr(filter_settings, "creation_date")
            return
        elif not total:
            return

        concepts: Iterable = [None]
        i: int = 0
        while concepts:
            concepts = self.get_concepts(
                skip=i * self._limit,
                take=self._limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
                with_aliases=with_aliases,
                with_properties=with_properties,
                with_links=with_links,
                with_link_properties=with_link_properties,
                with_facts=with_facts,
                with_potential_facts=with_potential_facts,
            )
            yield from concepts
            i += 1

    def get_concepts(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptFilterSettings] = None,
        direction: SortDirection = "descending",
        sort_field: ConceptSorting = "score",
        with_aliases: bool = False,
        with_properties: bool = False,
        with_links: bool = False,
        with_link_properties: bool = False,
        with_facts: bool = False,
        with_potential_facts=False,
    ) -> Sequence[Concept]:
        take = self.get_take_value(take)
        pagination_concept_kwargs = {}
        if not filter_settings:
            filter_settings = ConceptFilterSettings()

        op = Operation(Query)
        cp: ConceptPagination = op.pagination_concept(
            limit=take,
            offset=skip,
            filter_settings=filter_settings,
            direction=direction,
            sort_field=sort_field,
            **pagination_concept_kwargs,
        )
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_properties=with_properties,
            with_links=with_links,
            with_link_properties=with_link_properties,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept.list_concept

    def get_concepts_by_limit_offset_filter_settings(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptFilterSettings] = None,
        with_aliases: bool = False,
        with_facts: bool = False,
        with_potential_facts=False,
    ) -> Sequence[Concept]:
        take = self.get_take_value(take)
        op = Operation(Query)
        cp: ConceptPagination = op.pagination_concept(
            filter_settings=filter_settings if filter_settings else ConceptFilterSettings(), offset=skip, limit=take
        )
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept.list_concept

    def get_all_concept_links(
        self, filter_settings: Optional[ConceptLinkFilterSettings] = None, with_link_properties: bool = False
    ) -> Iterable[ConceptLink]:
        if not filter_settings:
            filter_settings = ConceptLinkFilterSettings()

        total = self.get_concept_link_count(filter_settings=filter_settings)

        if total > self.kb_iterator_config.max_total_count:
            had_creation_date = hasattr(filter_settings, "creation_date")
            old_timestamp_interval = None
            if had_creation_date:
                old_timestamp_interval = copy(filter_settings.creation_date)
            start: int = getattr(old_timestamp_interval, "start", self.kb_iterator_config.earliest_created_time)
            end: int = getattr(old_timestamp_interval, "end", int(time()))
            middle: int = (end + start) // 2

            for next_start, next_end in (start, middle), (middle + 1, end):
                if next_start == start and next_end == end:
                    logger.info(
                        f"Processed only {self.kb_iterator_config.max_total_count} links, "
                        f"{total - self.kb_iterator_config.max_total_count} ignored"
                    )
                    continue
                filter_settings.creation_date = TimestampInterval(start=next_start, end=next_end)
                for c in self.get_all_concept_links(
                    filter_settings=filter_settings, with_link_properties=with_link_properties
                ):
                    yield c

            if had_creation_date:
                filter_settings.creation_date = old_timestamp_interval
            else:
                delattr(filter_settings, "creation_date")
            return
        elif not total:
            return

        links: Iterable = [None]
        i: int = 0
        while links:
            links = self.get_concept_links_by_limit_offset_filter_settings(
                skip=i * self._limit,
                take=self._limit,
                filter_settings=filter_settings,
                with_link_properties=with_link_properties,
            )
            yield from links
            i += 1

    def get_concept_links_by_limit_offset_filter_settings(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptLinkFilterSettings] = None,
        with_link_properties: bool = False,
    ) -> Sequence[ConceptLink]:
        take = self.get_take_value(take)
        op = Operation(Query)
        pcl: ConceptLinkPagination = op.pagination_concept_link(
            filter_settings=filter_settings if filter_settings else ConceptLinkFilterSettings(), offset=skip, limit=take
        )
        self._configure_output_link_fields(pcl.list_concept_link(), with_link_properties=with_link_properties)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_link.list_concept_link

    def get_concepts_by_type_id_with_offset(
        self,
        type_id: str,
        skip: int,
        take: Optional[int] = None,
        direction="descending",
        sort_field="systemRegistrationDate",
        with_aliases: bool = False,
        with_properties: bool = False,
        with_links: bool = False,
        with_link_properties: bool = False,
        with_facts: bool = False,
        with_potential_facts=False,
    ) -> ConceptPagination:
        take = self.get_take_value(take)
        op = Operation(Query)
        cp: ConceptPagination = op.pagination_concept(
            filter_settings=ConceptFilterSettings(concept_type_ids=[type_id]),
            limit=take,
            offset=skip,
            direction=direction,
            sort_field=sort_field,
        )
        cp.total()
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_properties=with_properties,
            with_links=with_links,
            with_link_properties=with_link_properties,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept

    def get_concepts_by_type_id_with_offset_with_markers(
        self,
        type_id: str,
        skip: int = 0,
        take: Optional[int] = None,
        markers: Optional[List[str]] = None,
        direction="descending",
        sort_field="systemRegistrationDate",
        with_aliases: bool = False,
        with_facts: bool = False,
        with_potential_facts=False,
    ) -> ConceptPagination:
        take = self.get_take_value(take)
        op = Operation(Query)
        cp: ConceptPagination = op.pagination_concept(
            filter_settings=ConceptFilterSettings(
                concept_type_ids=[type_id],
                markers=markers,
            ),
            limit=take,
            offset=skip,
            direction=direction,
            sort_field=sort_field,
        )
        cp.total()
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept

    def get_concepts_by_name(
        self,
        name: str,
        type_id: Optional[str] = None,
        with_aliases: bool = False,
        with_facts: bool = False,
        with_potential_facts=False,
    ) -> Sequence[Concept]:
        op = Operation(Query)
        if type_id:
            concept_filter_settings: ConceptFilterSettings = ConceptFilterSettings(
                exact_name=name, concept_type_ids=[type_id]
            )
        else:
            concept_filter_settings: ConceptFilterSettings = ConceptFilterSettings(exact_name=name)
        cp: ConceptPagination = op.pagination_concept(filter_settings=concept_filter_settings)
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept.list_concept

    def get_concepts_by_near_name(
        self,
        name: str,
        type_id: Optional[str] = None,
        with_aliases: bool = False,
        with_facts: bool = False,
        with_potential_facts=False,
    ) -> Sequence[Concept]:
        op = Operation(Query)
        if type_id:
            concept_filter_settings: ConceptFilterSettings = ConceptFilterSettings(
                name=name, concept_type_ids=[type_id]
            )
        else:
            concept_filter_settings: ConceptFilterSettings = ConceptFilterSettings(name=name)
        cp: ConceptPagination = op.pagination_concept(filter_settings=concept_filter_settings)
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept.list_concept

    def get_concepts_by_property_name(
        self,
        property_type_id: str,
        string_filter: str,
        property_type: str = "concept",
        with_aliases: bool = False,
        with_facts: bool = False,
        with_potential_facts=False,
    ) -> Sequence[Concept]:
        op = Operation(Query)
        cp: ConceptPagination = op.pagination_concept(
            filter_settings=ConceptFilterSettings(
                property_filter_settings=[
                    PropertyFilterSettings(
                        property_type=property_type,
                        property_type_id=property_type_id,
                        string_filter=StringFilter(str=string_filter),
                    )
                ]
            )
        )
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept.list_concept

    def get_concept_properties(self, concept_id: str, with_facts: bool = False) -> Sequence[ConceptProperty]:
        op = Operation(Query)
        concept: Concept = op.concept(id=concept_id)
        pcp: ConceptPropertyPagination = concept.pagination_concept_property(
            offset=0, limit=10000, filter_settings=ConceptPropertyFilterSettings()
        )
        lcp = pcp.list_concept_property()
        lcp.__fields__(*self.concept_property_fields)
        lcp.property_type().__fields__(*self.concept_property_type_fields)
        self._configure_output_value_fields(lcp.value)
        if with_facts:
            lcp.__fields__("list_concept_property_fact")

        res = self._gql_client.execute(op)
        res = op + res  # type: Query
        return res.concept.pagination_concept_property.list_concept_property

    def get_concept_links(self, concept_id: str, with_link_properties: bool = False) -> Sequence[ConceptLink]:
        op = Operation(Query)

        concept: Concept = op.concept(id=concept_id)
        pcl: ConceptLinkPagination = concept.pagination_concept_link(
            offset=0, limit=10000, filter_settings=ConceptLinkFilterSettings()
        )
        self._configure_output_link_fields(pcl.list_concept_link(), with_link_properties=with_link_properties)
        res = self._gql_client.execute(op)
        res = op + res  # type: Query
        return res.concept.pagination_concept_link.list_concept_link

    def get_concept_links_concept(
        self, concept_id: str, link_type_id: str, with_link_properties: bool = False
    ) -> Sequence[ConceptLink]:
        op = Operation(Query)

        concept = op.concept(id=concept_id)
        pcl = concept.pagination_concept_link(
            offset=0, limit=10000, filter_settings=ConceptLinkFilterSettings(concept_link_type=[link_type_id])
        )
        self._configure_output_link_fields(pcl.list_concept_link(), with_link_properties=with_link_properties)
        res = self._gql_client.execute(op)
        res = op + res  # type: Query
        return res.concept.pagination_concept_link.list_concept_link

    def get_link_properties(self, link_id: str, with_facts: bool = False) -> Sequence[ConceptProperty]:
        op = Operation(Query)
        concept_link: ConceptLink = op.concept_link(id=link_id)
        pcp: ConceptPropertyPagination = concept_link.pagination_concept_link_property(
            offset=0, limit=10000, filter_settings=ConceptPropertyFilterSettings()
        )
        lcp = pcp.list_concept_property()
        lcp.__fields__(*self.concept_property_fields)
        lcp.property_type().__fields__(*self.concept_property_type_fields)
        self._configure_output_value_fields(lcp.value)
        if with_facts:
            lcp.__fields__("list_concept_property_fact")

        res = self._gql_client.execute(op)
        res = op + res  # type: Query
        return res.concept_link.pagination_concept_link_property.list_concept_property

    def get_concept_time_intervals(
        self, filter_settings: Optional[ConceptFilterSettings] = None, max_interval_size: Optional[int] = None
    ) -> Iterable[ObjectTimeInterval]:
        if not filter_settings:
            filter_settings = ConceptFilterSettings()
        yield from self._get_object_time_intervals(filter_settings, max_interval_size)

    def get_concept_link_time_intervals(
        self, filter_settings: Optional[ConceptLinkFilterSettings] = None, max_interval_size: Optional[int] = None
    ) -> Iterable[ObjectTimeInterval]:
        if not filter_settings:
            filter_settings = ConceptLinkFilterSettings()
        yield from self._get_object_time_intervals(filter_settings, max_interval_size)

    def get_document_time_intervals(
        self, filter_settings: Optional[DocumentFilterSettings] = None, max_interval_size: Optional[int] = None
    ) -> Iterable[ObjectTimeInterval]:
        if not filter_settings:
            filter_settings = DocumentFilterSettings()
        yield from self._get_object_time_intervals(filter_settings, max_interval_size)

    def _get_object_time_intervals(
        self,
        filter_settings: Union[ConceptFilterSettings, ConceptLinkFilterSettings, DocumentFilterSettings],
        max_interval_size: Optional[int] = None,
    ) -> Iterable[ObjectTimeInterval]:
        max_interval_size = max_interval_size if max_interval_size else self.kb_iterator_config.max_total_count

        creation_date_field_name = "creation_date"
        if isinstance(filter_settings, ConceptFilterSettings):
            object_count = self.get_concept_count(filter_settings)
        elif isinstance(filter_settings, ConceptLinkFilterSettings):
            object_count = self.get_concept_link_count(filter_settings)
        elif isinstance(filter_settings, DocumentFilterSettings):
            object_count = self.get_documents_count(filter_settings)
            creation_date_field_name = "registration_date"
        else:
            raise Exception("Time division is only available for concepts, links and documents")
        creation_date = getattr(filter_settings, creation_date_field_name, None)
        start: int = getattr(creation_date, "start", self.kb_iterator_config.earliest_created_time)
        end: int = getattr(creation_date, "end", int(time()))

        if (object_count > max_interval_size) and (start < end):
            middle = (end + start) // 2

            for mod_start, mod_end in (start, middle), (middle + 1, end):
                setattr(filter_settings, creation_date_field_name, TimestampInterval(start=mod_start, end=mod_end))
                for time_interval in self._get_object_time_intervals(filter_settings, max_interval_size):
                    yield time_interval
        elif object_count > 0:
            yield ObjectTimeInterval(
                start_time=start, end_time=end, object_count=object_count, max_interval_size=max_interval_size
            )

    def create_concept(
        self,
        name: str,
        type_id: str,
        notes: Optional[str] = None,
        with_properties: bool = False,
        with_links: bool = False,
        with_link_properties: bool = False,
        perform_synchronously: Optional[bool] = None,
    ) -> Concept:
        cmi: ConceptMutationInput = ConceptMutationInput(name=name, concept_type_id=type_id, notes=notes)
        return self._create_concept_with_input(
            cmi,
            with_properties=with_properties,
            with_links=with_links,
            with_link_properties=with_link_properties,
            perform_synchronously=perform_synchronously,
        )

    def update_concept(
        self, c: Concept, markers: List[str] = None, notes: str = None, perform_synchronously: Optional[bool] = None
    ) -> Concept:
        perform_synchronously = self.get_perform_synchronously_value(perform_synchronously)
        op = Operation(Mutation)
        uc: Concept = op.update_concept(
            performance_control=PerformSynchronously(perform_synchronously=perform_synchronously),
            form=ConceptUpdateInput(
                concept_id=c.id,
                name=c.name,
                concept_type_id=c.concept_type.id,
                markers=markers if markers is not None else c.markers,
                notes=notes if notes is not None else c.notes,
            ),
        )
        self._configure_output_concept_fields(uc)
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_concept

    def update_concept_property_value_types(self, cpvt: ConceptPropertyValueType) -> ConceptPropertyValueType:
        op = Operation(Mutation)
        ucpvt = op.update_concept_property_value_type(
            form=ConceptPropertyValueTypeUpdateInput(
                id=cpvt.id,
                name=cpvt.name,
                value_type=cpvt.value_type,
                pretrained_nercmodels=cpvt.pretrained_nercmodels,
                value_restriction=cpvt.value_restriction,
            )
        )
        ucpvt.__fields__("id")
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_concept_property_value_type

    def update_concept_string_property(self, cp: ConceptProperty) -> ConceptProperty:
        op = Operation(Mutation)
        ucp: ConceptProperty = op.update_concept_property(
            form=ConceptPropertyUpdateInput(
                property_id=cp.id,
                is_main=cp.is_main,
                value_input=[
                    ComponentValueInput(value=ValueInput(string_value_input=StringValueInput(value=cp.value.value)))
                ],
            )
        )
        ucp.__fields__("id")
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_concept_property

    def update_concept_int_property(self, cp: ConceptProperty) -> ConceptProperty:
        op = Operation(Mutation)
        ucp: ConceptProperty = op.update_concept_property(
            form=ConceptPropertyUpdateInput(
                property_id=cp.id,
                is_main=cp.is_main,
                value_input=[
                    ComponentValueInput(value=ValueInput(int_value_input=IntValueInput(value=cp.value.number)))
                ],
            )
        )
        ucp.__fields__("id")
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_concept_property

    def update_concept_composite_property(self, cp: ConceptProperty) -> ConceptProperty:
        value_input = []
        for value in cp.value.list_value:
            if type(value.value) is StringValue or type(value.value) is uas.StringValue:
                value_input.append(
                    ComponentValueInput(
                        id=value.id, value=ValueInput(string_value_input=StringValueInput(value=value.value.value))
                    )
                )
            elif type(value.value) is IntValue or type(value.value) is uas.IntValue:
                value_input.append(
                    ComponentValueInput(
                        id=value.id, value=ValueInput(int_value_input=IntValueInput(value=value.value.number))
                    )
                )
            elif type(value.value) is DateTimeValue or type(value.value) is uas.DateTimeValue:
                value_input.append(
                    ComponentValueInput(
                        id=value.id,
                        value=ValueInput(
                            date_time_value_input=DateTimeValueInput(date=value.value.date, time=value.value.time)
                        ),
                    )
                )
            elif type(value.value) is StringLocaleValue or type(value.value) is uas.StringLocaleValue:
                value_input.append(
                    ComponentValueInput(
                        id=value.id,
                        value=ValueInput(
                            string_locale_value_input=StringLocaleValueInput(
                                value=value.value.value, locale=value.value.locale
                            )
                        ),
                    )
                )
            elif type(value.value) is LinkValue or type(value.value) is uas.LinkValue:
                value_input.append(
                    ComponentValueInput(
                        id=value.id, value=ValueInput(link_value_input=LinkValueInput(link=value.value.link))
                    )
                )
            elif type(value.value) is DoubleValue or type(value.value) is uas.DoubleValue:
                value_input.append(
                    ComponentValueInput(
                        id=value.id, value=ValueInput(double_value_input=DoubleValueInput(double=value.value.double))
                    )
                )
        op = Operation(Mutation)
        ucp: ConceptProperty = op.update_concept_property(
            form=ConceptPropertyUpdateInput(property_id=cp.id, is_main=cp.is_main, value_input=value_input)
        )
        ucp.__fields__("id")
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_concept_property

    def delete_concept_property(self, cp_id: str) -> bool:
        op = Operation(Mutation)
        dcp = op.delete_concept_property(id=cp_id)
        dcp.__fields__("is_success")
        res = self._gql_client.execute(op)
        res = op + res

        return res.delete_concept_property.is_success

    def get_all_concept_types(
        self,
        filter_settings: Optional[ConceptTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptTypeSorting = "id",
    ) -> Iterable[ConceptType]:
        current_step = 0
        while True:
            concept_types = self.get_concept_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_types) < 1:
                break
            current_step += self.limit
            yield from concept_types

    def get_concept_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptTypeSorting = "id",
    ) -> Sequence[ConceptType]:
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = ConceptTypeFilterSettings()

        op = Operation(Query)
        pct: ConceptTypePagination = op.pagination_concept_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        pct.list_concept_type().__fields__(*self.concept_type_fields)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_type.list_concept_type

    def get_concept_types_by_name(self, name: str) -> Sequence[ConceptType]:
        op = Operation(Query)
        ctp: ConceptTypePagination = op.pagination_concept_type(filter_settings=ConceptTypeFilterSettings(name=name))
        ctp.list_concept_type().__fields__(*self.concept_type_fields)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_type.list_concept_type

    def get_concept_type_info(self, concept_type_id: str) -> ConceptType:
        op = Operation(Query)
        ct = op.concept_type(id=concept_type_id)
        ct.__fields__(*self.concept_type_fields)
        lcpt = ct.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        lclt = ct.list_concept_link_type()
        lclt.__fields__(*self.concept_link_type_fields)
        lclt.list_concept_link_property_type().__fields__(*self.concept_property_type_fields)

        res = self._gql_client.execute(op)
        res = op + res
        return res.concept_type

    def get_concept_type(self, concept_type_code: str) -> Optional[ConceptType]:
        concept_type = self._type_mapping.get_concept_type(concept_type_code)
        if concept_type:
            return concept_type

        concept_type_name = self._type_mapping.get_concept_type_name(concept_type_code)
        concept_types = self.get_concept_types_by_name(concept_type_name)
        for concept_type in concept_types:
            if concept_type.name == concept_type_name:
                self._type_mapping.add_concept_type(concept_type_code, concept_type)
                return concept_type
        return None

    def get_all_concept_property_types(
        self,
        filter_settings: Optional[ConceptPropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptPropertyTypeSorting = "name",
    ) -> Iterable[ConceptPropertyType]:
        current_step = 0
        while True:
            concept_property_types = self.get_concept_property_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_property_types) < 1:
                break
            current_step += self.limit
            yield from concept_property_types

    def get_concept_property_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptPropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptPropertyTypeSorting = "name",
    ) -> Sequence[ConceptPropertyType]:
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = ConceptPropertyTypeFilterSettings()

        op = Operation(Query)
        pcpt: ConceptPropertyTypePagination = op.pagination_concept_property_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        lcpt = pcpt.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_property_type.list_concept_property_type

    def get_concept_properties_types_by_name(
        self, concept_type_id: str, prop_name: str
    ) -> Sequence[ConceptPropertyType]:
        op = Operation(Query)
        cptp: ConceptPropertyTypePagination = op.pagination_concept_property_type(
            filter_settings=ConceptPropertyTypeFilterSettings(name=prop_name, concept_type_id=concept_type_id)
        )
        lcpt = cptp.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_property_type.list_concept_property_type

    def get_all_concept_composite_property_types(
        self,
        filter_settings: Optional[CompositePropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: CompositePropertyTypeSorting = "name",
    ) -> Iterable[ConceptPropertyType]:
        current_step = 0
        while True:
            concept_composite_property_types = self.get_concept_composite_property_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_composite_property_types) < 1:
                break
            current_step += self.limit
            yield from concept_composite_property_types

    def get_concept_composite_property_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[CompositePropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: CompositePropertyTypeSorting = "name",
    ) -> Sequence[ConceptPropertyType]:
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = CompositePropertyTypeFilterSettings()

        op = Operation(Query)
        pccpt: ConceptPropertyTypePagination = op.pagination_composite_concept_property_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        lcpt = pccpt.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_composite_concept_property_type.list_concept_property_type

    def get_concept_property_type(
        self, concept_type_code: str, property_type_code: str
    ) -> Optional[ConceptPropertyType]:
        property_type = self._type_mapping.get_concept_property_type(concept_type_code, property_type_code)
        if property_type:
            return property_type

        concept_type = self.get_concept_type(concept_type_code)
        if not concept_type:
            raise Exception("Cannot get concept property type: no concept type id")

        property_type_name = self._type_mapping.get_concept_property_type_name(concept_type_code, property_type_code)
        property_types = self.get_concept_properties_types_by_name(concept_type.id, property_type_name)
        for property_type in property_types:
            if property_type.name == property_type_name:
                self._type_mapping.add_concept_property_type(concept_type_code, property_type_code, property_type)
                return property_type
        return None

    def get_all_concept_property_value_types(
        self,
        filter_settings: Optional[ConceptPropertyValueTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptPropertyValueTypeSorting = "id",
    ) -> Iterable[ConceptPropertyValueType]:
        current_step = 0
        while True:
            concept_property_value_types = self.get_concept_property_value_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_property_value_types) < 1:
                break
            current_step += self.limit
            yield from concept_property_value_types

    def get_concept_property_value_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptPropertyValueTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptPropertyValueTypeSorting = "id",
    ) -> Sequence[ConceptPropertyValueType]:
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = ConceptPropertyValueTypeFilterSettings()

        op = Operation(Query)
        pcpvt: ConceptPropertyValueTypePagination = op.pagination_concept_property_value_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        pcpvt.list_concept_property_value_type().__fields__(*self.cpvt_fields)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_property_value_type.list_concept_property_value_type

    def get_concept_property_value_types_by_name(
        self, prop_value_type_name: str, limit: int = 20, offset: int = 0
    ) -> Sequence[ConceptPropertyValueType]:
        op = Operation(Query)
        cpvtp: ConceptPropertyValueTypePagination = op.pagination_concept_property_value_type(
            filter_settings=ConceptPropertyValueTypeFilterSettings(name=prop_value_type_name),
            limit=limit,
            offset=offset,
        )
        cpvtp.list_concept_property_value_type().__fields__(*self.cpvt_fields)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_property_value_type.list_concept_property_value_type

    def get_concept_property_value_type(
        self, concept_property_value_type_code: str
    ) -> Optional[ConceptPropertyValueType]:
        property_value_type = self._type_mapping.get_concept_property_value_type(concept_property_value_type_code)
        if property_value_type:
            return property_value_type

        value_type_name = self._type_mapping.get_concept_property_value_type_name(concept_property_value_type_code)
        value_types = self.get_concept_property_value_types_by_name(value_type_name)
        for value_type in value_types:
            if value_type.name == value_type_name:
                self._type_mapping.add_concept_property_value_type(concept_property_value_type_code, value_type)
                return value_type
        return None

    def get_all_concept_link_property_types(
        self,
        filter_settings: Optional[ConceptPropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptPropertyTypeSorting = "name",
    ) -> Iterable[ConceptPropertyType]:
        current_step = 0
        while True:
            concept_link_property_types = self.get_link_property_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_link_property_types) < 1:
                break
            current_step += self.limit
            yield from concept_link_property_types

    def get_link_property_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptPropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptPropertyTypeSorting = "name",
    ) -> Sequence[ConceptPropertyType]:
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = ConceptPropertyTypeFilterSettings()

        op = Operation(Query)
        pclpt: ConceptPropertyTypePagination = op.pagination_concept_link_property_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        lcpt = pclpt.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_link_property_type.list_concept_property_type

    def get_link_properties_types_by_name(self, link_type_id: str, prop_name: str) -> Sequence[ConceptPropertyType]:
        op = Operation(Query)
        cptp: ConceptPropertyTypePagination = op.pagination_concept_link_property_type(
            filter_settings=ConceptPropertyTypeFilterSettings(name=prop_name, concept_link_type_id=link_type_id)
        )
        lcpt = cptp.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_link_property_type.list_concept_property_type

    def get_all_concept_link_composite_property_types(
        self,
        filter_settings: Optional[CompositePropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: CompositePropertyTypeSorting = "name",
    ) -> Iterable[ConceptPropertyType]:
        current_step = 0
        while True:
            concept_link_composite_property_types = self.get_link_composite_property_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_link_composite_property_types) < 1:
                break
            current_step += self.limit
            yield from concept_link_composite_property_types

    def get_link_composite_property_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[CompositePropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: CompositePropertyTypeSorting = "name",
    ) -> Sequence[ConceptPropertyType]:
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = CompositePropertyTypeFilterSettings()

        op = Operation(Query)
        pclpt: ConceptPropertyTypePagination = op.pagination_composite_link_property_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        lcpt = pclpt.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_composite_link_property_type.list_concept_property_type

    def get_composite_link_properties_types_by_name(
        self, link_type_id: str, prop_name: str
    ) -> Sequence[ConceptPropertyType]:
        op = Operation(Query)
        cptp: ConceptPropertyTypePagination = op.pagination_composite_link_property_type(
            filter_settings=CompositePropertyTypeFilterSettings(name=prop_name, link_type_id=link_type_id)
        )
        lcpt = cptp.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_composite_link_property_type.list_concept_property_type

    def get_link_property_type(self, link_type_code: str, property_type_code: str) -> Optional[ConceptPropertyType]:
        property_type = self._type_mapping.get_concept_link_property_type(link_type_code, property_type_code)
        if property_type:
            return property_type
        link_type = self.get_link_type(link_type_code)

        property_type_name = self._type_mapping.get_concept_link_property_type_name(link_type_code, property_type_code)
        property_types = self.get_link_properties_types_by_name(link_type.id, property_type_name)
        for property_type in property_types:
            if property_type.name == property_type_name:
                self._type_mapping.add_concept_link_property_type(link_type_code, property_type_code, property_type)
                return property_type
        return None

    def get_link_composite_property_type(
        self, link_type_code: str, property_type_code: str
    ) -> Optional[ConceptPropertyType]:
        property_type = self._type_mapping.get_concept_link_composite_property_type(link_type_code, property_type_code)
        if property_type:
            return property_type
        link_type = self.get_link_type(link_type_code)

        property_type_name = self._type_mapping.get_concept_link_composite_property_type_name(
            link_type_code, property_type_code
        )
        property_types = self.get_composite_link_properties_types_by_name(link_type.id, property_type_name)
        for property_type in property_types:
            if property_type.name == property_type_name:
                self._type_mapping.add_concept_link_composite_property_type(
                    link_type_code, property_type_code, property_type
                )
                return property_type
        return None

    def add_property_by_id(
        self,
        id: str,
        type_id: str,
        value: Any,
        is_main: bool,
        value_type: str,
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        perform_synchronously = self.get_perform_synchronously_value(perform_synchronously)
        op = Operation(Mutation)
        acp = op.add_concept_property(
            performance_control=PerformSynchronously(perform_synchronously=perform_synchronously),
            form=ConceptPropertyCreateInput(
                concept_id=id,
                property_type_id=type_id,
                is_main=is_main,
                value_input=[ComponentValueInput(value=get_map_helper(value_type).get_value_input(value))],
            ),
        )
        acp.__fields__("id")
        acp.property_type().__fields__(*self.concept_property_type_fields)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_property

    def add_property(
        self,
        concept_id: str,
        concept_type_code: str,
        property_type_code: str,
        value: Any,
        is_main: bool = False,
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        property_type: ConceptPropertyType = self.get_concept_property_type(concept_type_code, property_type_code)
        if not property_type:
            raise Exception("Cannot add property: no property type id")
        if type(property_type.value_type) is CompositePropertyValueTemplate:
            component_values = self._type_mapping.get_concept_composite_property_component_values(
                concept_type_code, property_type_code
            )
            components_type_mapping: Dict[str, CompositePropertyValueType] = self._get_components_mapping(
                component_values, property_type.value_type.component_value_types
            )
            prop = self.add_composite_property_by_id(
                concept_id, property_type.id, value, is_main, components_type_mapping, perform_synchronously
            )
        else:
            prop = self.add_property_by_id(
                concept_id, property_type.id, value, is_main, property_type.value_type.value_type, perform_synchronously
            )
        if self.tdm_builder is not None:
            self.tdm_builder.add_concept_property_fact(prop, self.get_concept(concept_id), value, property_type)

        return prop

    def add_link_property_by_id(
        self,
        link_id: str,
        type_id: str,
        value: str,
        is_main: bool,
        value_type: str,
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        perform_synchronously = self.get_perform_synchronously_value(perform_synchronously)
        op = Operation(Mutation)

        aclp = op.add_concept_link_property(
            performance_control=PerformSynchronously(perform_synchronously=perform_synchronously),
            form=ConceptLinkPropertyInput(
                property_type_id=type_id,
                link_id=link_id,
                is_main=is_main,
                value_input=[ComponentValueInput(value=get_map_helper(value_type).get_value_input(value))],
            ),
        )
        aclp.__fields__("id")
        aclp.property_type().__fields__(*self.concept_property_type_fields)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_link_property

    def add_concept_link_property_type(self, link_type_id: str, name: str, value_type_id: str) -> ConceptPropertyType:
        op = Operation(Mutation)

        aclpt = op.add_concept_link_property_type(
            form=ConceptLinkPropertyTypeCreationInput(
                link_type_id=link_type_id,
                name=name,
                value_type_id=value_type_id,
            )
        )
        aclpt.__fields__(*self.concept_property_type_fields)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_link_property_type

    def update_concept_link_property_type(
        self, link_property_type_id: str, name: str, value_type_id: str
    ) -> ConceptPropertyType:
        op = Operation(Mutation)

        acpt = op.update_concept_link_property_type(
            form=ConceptLinkPropertyTypeUpdateInput(
                id=link_property_type_id,
                name=name,
                value_type_id=value_type_id,
            )
        )
        acpt.__fields__(*self.concept_property_type_fields)
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_concept_link_property_type

    def delete_concept_link_property_type(self, property_type_id: str) -> State:
        op = Operation(Mutation)

        op.delete_concept_link_property_type(id=property_type_id)
        res = self._gql_client.execute(op)
        res = op + res

        return res.delete_concept_link_property_type

    def add_concept_property_type(self, concept_type_id: str, name: str, value_type_id: str) -> ConceptPropertyType:
        op = Operation(Mutation)

        acpt = op.add_concept_property_type(
            form=ConceptPropertyTypeCreationInput(
                concept_type_id=concept_type_id,
                name=name,
                value_type_id=value_type_id,
            )
        )
        acpt.__fields__(*self.concept_property_type_fields)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_property_type

    def delete_concept_property_type(self, property_type_id: str) -> State:
        op = Operation(Mutation)

        op.delete_concept_property_type(id=property_type_id)
        res = self._gql_client.execute(op)
        res = op + res

        return res.delete_concept_property_type

    def add_link_composite_property_by_id(
        self,
        link_id: str,
        property_type_id: str,
        values: dict,
        components_type_mapping: Dict[str, CompositePropertyValueType],
        is_main: bool,
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        value_input = self._get_value_input(values, components_type_mapping)
        perform_synchronously = self.get_perform_synchronously_value(perform_synchronously)

        op = Operation(Mutation)
        aclp = op.add_concept_link_property(
            performance_control=PerformSynchronously(perform_synchronously=perform_synchronously),
            form=ConceptLinkPropertyInput(
                property_type_id=property_type_id, link_id=link_id, is_main=is_main, value_input=value_input
            ),
        )
        aclp.__fields__("id")
        aclp.property_type().__fields__(*self.concept_property_type_fields)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_link_property

    def add_composite_property_by_id(
        self,
        id: str,
        type_id: str,
        values: dict,
        is_main: bool,
        components_type_mapping: Dict[str, CompositePropertyValueType],
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        value_input = self._get_value_input(values, components_type_mapping)
        perform_synchronously = self.get_perform_synchronously_value(perform_synchronously)

        op = Operation(Mutation)
        acp = op.add_concept_property(
            performance_control=PerformSynchronously(perform_synchronously=perform_synchronously),
            form=ConceptPropertyCreateInput(
                concept_id=id, property_type_id=type_id, is_main=is_main, value_input=value_input
            ),
        )
        acp.__fields__("id")
        acp.property_type().__fields__(*self.concept_property_type_fields)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_property

    def add_link_property(
        self,
        link_id: str,
        link_type_code: str,
        property_type_code: str,
        value: Any,
        is_composite: Optional[bool] = False,
        is_main: bool = False,
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        property_type = (
            self.get_link_composite_property_type(link_type_code, property_type_code)
            if is_composite
            else self.get_link_property_type(link_type_code, property_type_code)
        )
        if not property_type:
            raise Exception("Cannot add property: no property type id")

        if is_composite:
            component_values = self._type_mapping.get_concept_link_composite_property_component_values(
                link_type_code, property_type_code
            )
            components_type_mapping: Dict[str, CompositePropertyValueType] = self._get_components_mapping(
                component_values, property_type.value_type.component_value_types
            )

            link_property = self.add_link_composite_property_by_id(
                link_id,
                property_type.id,
                value,
                components_type_mapping,
                is_main,
                perform_synchronously,
            )
        else:
            link_property = self.add_link_property_by_id(
                link_id,
                property_type.id,
                value,
                is_main,
                property_type.value_type.value_type,
                perform_synchronously,
            )

        if self.tdm_builder is not None:
            self.tdm_builder.add_link_property_fact(link_property, self.get_concept_link(link_id), value, property_type)

        return link_property

    def get_all_concept_link_types(
        self,
        filter_settings: Optional[ConceptLinkTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptLinkTypeSorting = "id",
    ) -> Iterable[ConceptLinkType]:
        current_step = 0
        while True:
            concept_link_types = self.get_concept_link_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_link_types) < 1:
                break
            current_step += self.limit
            yield from concept_link_types

    def get_concept_link_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptLinkTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptLinkTypeSorting = "id",
    ) -> Sequence[ConceptLinkType]:
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = ConceptLinkTypeFilterSettings()

        op = Operation(Query)
        pclt: ConceptLinkTypePagination = op.pagination_concept_link_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        lclt = pclt.list_concept_link_type()
        lclt.__fields__(*self.concept_link_type_fields)
        lclt.concept_from_type().__fields__(*self.concept_type_fields)
        lclt.concept_to_type().__fields__(*self.concept_type_fields)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_link_type.list_concept_link_type

    def get_concept_link_type_by_name(
        self, link_name: str, from_type_id: str, to_type_id: str, limit: int = 20
    ) -> Sequence[ConceptLinkType]:
        op = Operation(Query)
        pclt: ConceptLinkTypePagination = op.pagination_concept_link_type(
            filter_settings=ConceptLinkTypeFilterSettings(
                name=link_name, concept_from_type_id=from_type_id, concept_to_type_id=to_type_id
            ),
            limit=limit,
        )
        lclt = pclt.list_concept_link_type()
        lclt.__fields__(*self.concept_link_type_fields)
        lclt.concept_from_type().__fields__(*self.concept_type_fields)
        lclt.concept_to_type().__fields__(*self.concept_type_fields)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_link_type.list_concept_link_type

    def get_link_type(self, link_type_code: str) -> Optional[ConceptLinkType]:
        link_type = self._type_mapping.get_concept_link_type(link_type_code)
        if link_type:
            return link_type

        concept_from_type_code = self._type_mapping.get_source_concept_type_code(link_type_code)
        concept_to_type_code = self._type_mapping.get_target_concept_type_code(link_type_code)
        concept_from_type = self.get_concept_type(concept_from_type_code)
        concept_to_type = self.get_concept_type(concept_to_type_code)
        link_type_name = self._type_mapping.get_concept_link_type_name(link_type_code)
        link_types = self.get_concept_link_type_by_name(link_type_name, concept_from_type.id, concept_to_type.id)
        for link_type in link_types:
            if link_type.name == link_type_name:
                self._type_mapping.add_concept_link_type(link_type_code, link_type)
                return link_type
        return None

    def add_relation_by_id(
        self, from_id: str, to_id: str, link_type_id: str, perform_synchronously: Optional[bool] = None
    ) -> ConceptLink:
        perform_synchronously = self.get_perform_synchronously_value(perform_synchronously)
        op = Operation(Mutation)
        acl = op.add_concept_link(
            performance_control=PerformSynchronously(perform_synchronously=perform_synchronously),
            form=ConceptLinkCreationMutationInput(
                concept_from_id=from_id, concept_to_id=to_id, link_type_id=link_type_id
            ),
        )
        acl.__fields__(*self.concept_link_fields)
        acl.concept_link_type.__fields__(*self.concept_property_type_fields)
        acl.concept_link_type.__fields__(*self.concept_link_type_fields_truncated)
        self._configure_output_concept_fields(acl.concept_from)
        self._configure_output_concept_fields(acl.concept_to)

        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_link

    def add_relation(
        self,
        concept_from_id: str,
        concept_to_id: str,
        type_code: str,
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptLink:
        link_type = self.get_link_type(type_code)
        if not link_type:
            raise Exception("Cannot add relation: no link type")
        relation = self.add_relation_by_id(
            concept_from_id, concept_to_id, link_type.id, perform_synchronously=perform_synchronously
        )

        if self.tdm_builder is not None:
            self.tdm_builder.add_link_fact(relation)

        return relation

    def delete_concept(self, concept_id: str) -> bool:
        op = Operation(Mutation)
        dc: Concept = op.delete_concept(id=concept_id)
        dc.__fields__("is_success")
        res = self._gql_client.execute(op)
        res = op + res

        return res.delete_concept.is_success

    def delete_concept_link(self, link_id: str) -> bool:
        op = Operation(Mutation)
        dcl: ConceptLink = op.delete_concept_link(id=link_id)
        dcl.__fields__("is_success")
        res = self._gql_client.execute(op)
        res = op + res

        return res.delete_concept_link.is_success

    def delete_concept_link_property(self, link_property_id: str) -> bool:
        op = Operation(Mutation)
        clp: ConceptProperty = op.delete_concept_link_property(id=link_property_id)
        clp.__fields__("is_success")
        res = self._gql_client.execute(op)
        res = op + res

        return res.delete_concept_link_property.is_success

    def add_concept_markers(
        self, concept_id: str, markers: List[str], perform_synchronously: Optional[bool] = None
    ) -> Concept:
        c = self.get_concept(concept_id)
        c.markers.extend(markers)
        new_markers = list(set(c.markers))
        return self.update_concept(c, markers=new_markers, perform_synchronously=perform_synchronously)

    def set_concept_markers(
        self, concept_id: str, markers: List[str], perform_synchronously: Optional[bool] = None
    ) -> Concept:
        c = self.get_concept(concept_id)
        return self.update_concept(c, markers=markers, perform_synchronously=perform_synchronously)

    def get_composite_concept(self, root_concept_id: str, composite_concept_type_id: str) -> CompositeConcept:
        op = Operation(Query)
        cc: CompositeConcept = op.composite_concept(
            root_concept_id=root_concept_id, composite_concept_type_id=composite_concept_type_id
        )
        self._configure_output_concept_fields(
            cc.root_concept, with_aliases=False, with_link_properties=False, with_links=False, with_properties=False
        )
        lwt = cc.composite_concept_type().list_widget_type()
        lwt.__fields__(*self.composite_concept_widget_type)
        lwt.columns_info.__fields__(*self.composite_concept_widget_type_columns_info)

        res = self._gql_client.execute(op)
        res = op + res
        return res.composite_concept

    def get_single_widget(
        self,
        root_concept_id: str,
        composite_concept_type_id: str,
        widget_type_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> CompositeConceptWidgetRowPagination:
        op = Operation(Query)
        cc: CompositeConcept = op.composite_concept(
            root_concept_id=root_concept_id, composite_concept_type_id=composite_concept_type_id
        )
        psw: CompositeConceptWidgetRowPagination = cc.paginate_single_widget(
            widget_type_id=widget_type_id, limit=limit, offset=offset
        )
        psw.__fields__("total")
        self._configure_output_value_fields(psw.rows)

        res = self._gql_client.execute(op)
        res = op + res
        return res.composite_concept.paginate_single_widget

    def add_concept_fact(self, concept_id: str, document_id: str) -> State:
        op = Operation(Mutation)
        op.add_concept_fact(id=concept_id, fact=FactInput(document_id=document_id))
        res = self._gql_client.execute(op)
        res = op + res
        return res.add_concept_fact

    def delete_concept_fact(self, fact_id: str) -> State:
        op = Operation(Mutation)
        op.delete_concept_fact(
            id=fact_id,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.delete_concept_fact

    def add_concept_property_fact(self, property_id: str, document_id: str) -> State:
        op = Operation(Mutation)
        op.add_concept_property_fact(id=property_id, fact=FactInput(document_id=document_id))
        res = self._gql_client.execute(op)
        res = op + res
        return res.add_concept_property_fact

    def delete_concept_property_fact(self, fact_id: str) -> State:
        op = Operation(Mutation)
        op.delete_concept_property_fact(
            id=fact_id,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.delete_concept_property_fact

    def add_concept_link_fact(self, link_id: str, document_id: str) -> State:
        op = Operation(Mutation)
        op.add_concept_link_fact(id=link_id, fact=FactInput(document_id=document_id))
        res = self._gql_client.execute(op)
        res = op + res
        return res.add_concept_link_fact

    def delete_concept_link_fact(self, fact_id: str) -> State:
        op = Operation(Mutation)
        op.delete_concept_link_fact(
            id=fact_id,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.delete_concept_link_fact

    def add_concept_link_property_fact(self, link_property_id: str, document_id: str) -> State:
        op = Operation(Mutation)
        op.add_concept_link_property_fact(id=link_property_id, fact=FactInput(document_id=document_id))
        res = self._gql_client.execute(op)
        res = op + res
        return res.add_concept_link_property_fact

    def delete_concept_link_property_fact(self, fact_id: str) -> State:
        op = Operation(Mutation)
        op.delete_concept_link_property_fact(
            id=fact_id,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.delete_concept_link_property_fact

    def merge_concepts(self, c_main_id: str, c_merged_id: str) -> Concept:
        op = Operation(Mutation)
        mc: Concept = op.merge_concepts(
            form=ConceptMergeInput(main_concept_id=c_main_id, merged_concept_id=c_merged_id)
        )
        self._configure_output_concept_fields(mc)
        res = self._gql_client.execute(op)
        res = op + res

        return res.merge_concepts

    def unmerge_concepts(self, c_main_id: str, c_merged_id: List[str]) -> Concept:
        op = Operation(Mutation)
        umc: Concept = op.unmerge_concepts(
            form=ConceptUnmergeInput(main_concept_id=c_main_id, merged_concept_id=c_merged_id)
        )
        self._configure_output_concept_fields(umc)
        res = self._gql_client.execute(op)
        res = op + res

        return res.unmerge_concepts

    # region Crawlers methods

    def get_crawler_start_urls(self, take: Optional[int] = None) -> Sequence[Crawler]:
        take = self.get_take_value(take)
        op = Operation(CrQuery)
        pc: CrawlerPagination = op.pagination_crawler(limit=take)
        lc = pc.list_crawler()
        lc.__fields__("start_urls")

        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_crawler.list_crawler

    # endregion

    # region Utils methods

    @check_utils_gql_client
    def create_or_get_concept_by_name(
        self,
        name: str,
        type_id: str,
        notes: Optional[str] = None,
        take_first_result: bool = False,
        with_properties: bool = False,
        with_links: bool = False,
        with_link_properties: bool = False,
        with_facts: bool = False,
        with_potential_facts: bool = False,
    ) -> Concept:
        """Finds concept by near name"""

        if type_id:
            concept_filter_settings: ConceptFilterSettings = uas.ConceptFilterSettings(
                exact_name=name, concept_type_ids=[type_id]
            )
        else:
            concept_filter_settings: ConceptFilterSettings = uas.ConceptFilterSettings(exact_name=name)

        op = Operation(uas.Mutation)
        goac = op.get_or_add_concept(
            filter_settings=concept_filter_settings,
            form=uas.ConceptMutationInput(name=name, concept_type_id=type_id, notes=notes),
            take_first_result=take_first_result,
        )
        self._configure_output_concept_fields(
            goac,
            with_properties=with_properties,
            with_links=with_links,
            with_link_properties=with_link_properties,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )

        res = self._utils_gql_client.execute(op)
        res = op + res  # type: uas.Mutation

        if self.tdm_builder is not None:
            self.tdm_builder.add_concept_fact(res.get_or_add_concept)

        return res.get_or_add_concept

    @check_utils_gql_client
    def get_tdm(self, doc_id: str):
        op = Operation(uas.Query)
        op.tdm(id=doc_id)
        res = self._utils_gql_client.execute(op)
        res = op + res
        return res

    # endregion

    # region tcontroller methods

    def get_pipeline_configs(
        self,
        with_transforms: bool = True,
        filter_settings: Optional[tc.PipelineConfigFilter] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: tc.PipelineConfigSort = "id",
        sort_direction: tc.SortDirection = "ascending",
    ) -> tc.PipelineConfigList:
        op = Operation(tc.Query)
        pcl: tc.PipelineConfigList = op.pipeline_configs(
            filter=filter_settings, limit=limit, offset=offset, sort_by=sort_by, sort_direction=sort_direction
        )
        pc = pcl.pipeline_configs()
        pc.__fields__(*self.pipeline_config_fields)
        if with_transforms:
            pc.transforms().__fields__("id")
            pc.transforms().__fields__("params")
        res = self._gql_client.execute(op)
        res = op + res
        return res.pipeline_configs

    def get_pipeline_topics(
        self,
        filter_settings: Optional[tc.KafkaTopicFilter] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: tc.KafkaTopicSort = "topic",
        sort_direction: tc.SortDirection = "ascending",
    ) -> tc.KafkaTopicList:
        op = Operation(tc.Query)
        ktl: tc.KafkaTopicList = op.kafka_topics(
            filter=filter_settings, limit=limit, offset=offset, sort_by=sort_by, sort_direction=sort_direction
        )
        self._configure_pipeline_topic_fields(ktl.topics())
        res = self._gql_client.execute(op)
        res = op + res
        return res.kafka_topics

    def upsert_pipeline_topic(self, topic_id: str, config_id: str, stopped: bool) -> tc.KafkaTopic:
        op = Operation(tc.Mutation)
        kt: tc.KafkaTopic = op.put_kafka_topic(
            topic=topic_id, pipeline=tc.PipelineSetupInput(pipeline_config=config_id), stopped=stopped
        )
        self._configure_pipeline_topic_fields(kt)
        res = self._gql_client.execute(op)
        res = op + res
        return res.put_kafka_topic

    def get_failed_messages_from_topic(
        self,
        topic_id: str,
        filter_settings: Optional[tc.MessageFilter] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: tc.MessageSort = "timestamp",
        sort_direction: tc.SortDirection = "descending",
    ) -> tc.FailedMessageList:
        op = Operation(tc.Query)
        fm: tc.FailedMessageList = op.failed_messages(
            topic=topic_id,
            filter=filter_settings,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )
        fm.messages().id()
        fm.messages().info().error().description()
        fm.messages().info().message()
        res = self._gql_client.execute(op)
        res = op + res
        return res.failed_messages

    def get_ok_messages_from_topic(
        self,
        topic_id: str,
        filter_settings: Optional[tc.MessageFilter] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: tc.MessageSort = "timestamp",
        sort_direction: tc.SortDirection = "descending",
    ) -> tc.CompletedOkMessageList:
        op = Operation(tc.Query)
        om: tc.CompletedOkMessageList = op.completed_ok_messages(
            topic=topic_id,
            filter=filter_settings,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )
        om.messages().id()
        om.messages().info().message()
        res = self._gql_client.execute(op)
        res = op + res
        return res.completed_ok_messages

    def get_active_messages_from_topic(
        self,
        topic_id: str,
        filter_settings: Optional[tc.MessageFilter] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: tc.MessageSort = "timestamp",
        sort_direction: tc.SortDirection = "descending",
    ) -> tc.CompletedOkMessageList:
        op = Operation(tc.Query)
        am: tc.CompletedOkMessageList = op.active_messages(
            topic=topic_id,
            filter=filter_settings,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )
        am.messages().id()
        am.messages().info().message()
        res = self._gql_client.execute(op)
        res = op + res
        return res.active_messages

    def retry_failed_in_topic(self, topic_id: str) -> int:
        op = Operation(tc.Mutation)
        op.retry_failed_in_topic(topic=topic_id)
        res = self._gql_client.execute(op)
        res = op + res
        return res.retry_failed_in_topic

    # endregion
