from datetime import datetime
import json
from typing import Iterator, Optional, Protocol, Sequence, Union

from cqlpy._internal.context.parameter_provider import ParameterProvider
from cqlpy._internal.context.resource_query import ResourceQuery
from cqlpy._internal.context.type_factory import TypeFactory
from cqlpy._internal.operators.comparison.in_list import in_list
from cqlpy._internal.operators.list.exists import exists
from cqlpy._internal.operators.list.intersect import intersect
from cqlpy._internal.operators.nullological.is_null import is_null
from cqlpy._internal.parameter import Parameter
from cqlpy._internal.types.any import CqlAny
from cqlpy._internal.types.code import Code
from cqlpy._internal.types.concept import Concept
from cqlpy._internal.types.datetime import DateTime
from cqlpy._internal.types.interval import Interval
from cqlpy._internal.types.null import Null
from cqlpy._internal.types.value_set import ValueSet
from cqlpy._internal.types.string import String
from cqlpy._internal.context.fhir.r4.map import FHIR_TO_CQL_MAP


class FhirBase:
    def __init__(self, fhir_json: dict, base_type: str):
        self._fhir_json = fhir_json
        self._base_type = base_type

    def __str__(self) -> str:
        return json.dumps(self._fhir_json)

    def __getitem__(self, property_name: str):
        if property_name in ["resourceType", "derivedFromResourceType"]:
            if property_name in self._fhir_json:
                return self._fhir_json[property_name]
            else:
                return None

        elif (self._base_type in FHIR_TO_CQL_MAP) and (
            property_name in FHIR_TO_CQL_MAP[self._base_type]
        ):
            cql_type_name = FHIR_TO_CQL_MAP[self._base_type][property_name]

            if cql_type_name == "Choice:Interval<DateTime>":
                if f"{property_name}DateTime" in self._fhir_json:
                    cql_type, _ = TypeFactory.get_type("DateTime")
                    value = cql_type.parse_fhir_json(
                        self._fhir_json[f"{property_name}DateTime"]
                    )
                    assert isinstance(value, DateTime)
                    return Interval(value, True, value, True)

            elif cql_type_name == "Choice:String":
                if any(prop.startswith(property_name) for prop in self._fhir_json):
                    cql_type, _ = TypeFactory.get_type("String")
                    value = cql_type.parse_fhir_json(self._fhir_json[property_name])
                    assert isinstance(value, str)
                    return String(value)

            elif "List<BackboneElement:" in cql_type_name:
                element_name = cql_type_name.split(":")[1].replace(">", "")

                if property_name in self._fhir_json:
                    return [
                        BackboneElement(item, element_name)
                        for item in self._fhir_json[property_name]
                    ]
                else:
                    return []

            elif cql_type_name.startswith("List<"):
                element_name = cql_type_name.split("<")[1].replace(">", "")

                if property_name in self._fhir_json:
                    cql_type, subtype = TypeFactory.get_type(element_name)
                    return [
                        cql_type.parse_fhir_json(item, subtype)
                        for item in self._fhir_json[property_name]
                    ]

            elif cql_type_name.startswith("BackboneElement:"):
                element_name = cql_type_name.split(":")[1]

                if property_name in self._fhir_json:
                    return BackboneElement(self._fhir_json[property_name], element_name)
                else:
                    return BackboneElement({}, element_name)

            elif property_name in self._fhir_json:
                cql_type, subtype = TypeFactory.get_type(cql_type_name)
                return cql_type.parse_fhir_json(self._fhir_json[property_name], subtype)

        return Null()

    @property
    def value(self) -> str:
        return json.dumps(self._fhir_json)

    def set_property(self, property_name: str, property_value: object) -> None:
        if property_value:
            self._fhir_json[property_name] = property_value

    def get_property(self, property_name: str) -> object:
        if property_name in self._fhir_json:
            return self._fhir_json[property_name]
        else:
            return None


class _RelatedFhirResourceProvider(Protocol):
    def __getitem__(self, resource_name: str) -> Sequence[FhirBase]:
        ...


class Resource(FhirBase):
    def __init__(
        self,
        fhir_json: dict,
        resource_type: str,
        related_resource_provider: _RelatedFhirResourceProvider,
    ):
        self.__related_resource_provider = related_resource_provider
        super().__init__(fhir_json, resource_type)

    def __getitem__(
        self, property_name: str
    ) -> Union[list[FhirBase], FhirBase, list[CqlAny], CqlAny]:
        if "Related:" in property_name:
            resource_name = property_name.split(":")[1]

            return [
                resource
                for resource in self.__related_resource_provider[resource_name]
                if str(self["id"]) in str(resource[self._base_type.lower()])
            ]
        else:
            return super().__getitem__(property_name)


class BackboneElement(FhirBase):
    def __init__(self, fhir_json: dict, element_type: str):
        super().__init__(fhir_json, element_type)


class Element(FhirBase):
    def __init__(self, fhir_json: dict, element_type: str):
        super().__init__(fhir_json, element_type)


class Reference(FhirBase):
    def __init__(self, fhir_json: dict):
        super().__init__(fhir_json, "Reference")


FILTER_PROPERTY_PROXIES = {
    "cpt": {"Procedure": "code", "Encounter": "type"},
    "http://www.ama-assn.org/go/cpt": {"Procedure": "code", "Encounter": "type"},
    "https://www.cms.gov/Medicare/Coding/HCPCSReleaseCodeSets": {
        "Procedure": "code",
        "Encounter": "type",
    },
    "http://loinc.org": {"Observation": "code", "DiagnosticReport": "type"},
    "http://snomed.info/sct": {"Condition": "code", "DiagnosticReport": "type"},
}


RESOURCE_PROXIES = {
    "DiagnosticReport~Procedure": {
        "effectiveDateTime": "performedDateTime",
        "status": "literal:final",
    },
    "Encounter~Procedure": {
        "period": "period:performedDateTime",
        "status": "literal:finished",
    },
}


def _get_filter_codes(
    filter_: Optional[Union[ValueSet, list[Code], Code]]
) -> list[Code]:
    if filter_ is None:
        return []
    if isinstance(filter_, ValueSet):
        return filter_.codes
    if isinstance(filter_, list):
        return filter_
    return [filter_]


class FhirR4DataModel:
    def __init__(self, bundle: dict, parameter_provider: ParameterProvider) -> None:
        self.__parameter_provider = parameter_provider
        self.resource_id_index = {}
        self.resource_type_index: dict[str, list[str]] = {}
        self.retrieve_cache: dict[ResourceQuery, list[Resource]] = {}

        if "entry" not in bundle:
            return

        for entry in bundle["entry"]:
            if not (
                (resource_json := entry.get("resource"))
                and ("resourceType" in resource_json)
                and ("id" in resource_json)
            ):
                continue

            resource_type: str = resource_json["resourceType"]
            resource_id = f"{resource_type}/{resource_json['id']}"

            self.resource_id_index[resource_id] = resource_json
            if not (resource_type in self.resource_type_index):
                self.resource_type_index[resource_type] = [resource_id]
            else:
                self.resource_type_index[resource_type].append(resource_id)

    def __get_filter_resource_properties(
        self, resource_type: str, filter_codes: list[Code], property_name: Optional[str]
    ) -> list[tuple[str, Optional[str]]]:
        filter_resource_properties = [(resource_type, property_name)]

        if self.__parameter_provider[Parameter("strict", "String")] == "True":
            return filter_resource_properties

        added_code_systems = []
        for code in filter_codes:
            if code.system in added_code_systems:
                continue

            code_system = None
            if code.system is not None:
                if isinstance(code.system, str):
                    code_system = code.system
                else:
                    code_system, _ = code.system.value

            added_code_systems.append(code_system)
            if code_system not in FILTER_PROPERTY_PROXIES:
                continue

            filter_property_proxies = FILTER_PROPERTY_PROXIES[code_system]
            for filter_resource_type in filter_property_proxies:
                filter_property_exists = False
                for filter_resource_property in filter_resource_properties:
                    if (filter_resource_property[0] == filter_resource_type) and (
                        filter_resource_property[1]
                        == filter_property_proxies[filter_resource_type]
                    ):
                        filter_property_exists = True
                if not filter_property_exists:
                    filter_resource_properties.append(
                        (
                            filter_resource_type,
                            filter_property_proxies[filter_resource_type],
                        )
                    )

        return filter_resource_properties

    def __retrieve_resources(self, resource_query: ResourceQuery) -> Iterator[Resource]:
        filter_codes = _get_filter_codes(resource_query.property_filter)
        filter_resource_properties = self.__get_filter_resource_properties(
            resource_type=resource_query.resource_type,
            filter_codes=filter_codes,
            property_name=resource_query.property_name,
        )

        if resource_query.property_filter is None:
            yield from (
                Resource(self.resource_id_index[id], resource_query.resource_type, self)
                for id in self.resource_type_index[resource_query.resource_type]
                if resource_query.resource_type in self.resource_type_index
            )
            return

        print(filter_resource_properties)
        for filter_resource_type, filter_property_name in filter_resource_properties:
            if filter_resource_type not in self.resource_type_index:
                continue

            for id in self.resource_type_index[filter_resource_type]:
                resource = Resource(
                    self.resource_id_index[id],
                    filter_resource_type,
                    self,
                )

                resource_property = (
                    resource[filter_property_name]
                    if filter_property_name is not None
                    else None
                )

                if isinstance(resource_property, list):
                    for concept in resource_property:
                        if not isinstance(concept, Concept):
                            continue

                        intersection = intersect(concept.codes, filter_codes)
                        assert isinstance(intersection, list)
                        if exists(intersection):
                            yield resource

                elif isinstance(resource_property, Code) and in_list(
                    resource_property, filter_codes
                ):
                    yield resource

                elif isinstance(resource_property, Concept):
                    intersection = intersect(resource_property.codes, filter_codes)
                    assert isinstance(intersection, list)
                    if exists(intersection):
                        yield resource

    def __build_resource_proxies(
        self,
        resource_type: str,
        resources: list[Resource],
    ) -> Iterator[Resource]:
        for resource in resources:
            if resource._base_type == resource_type:
                yield resource

            # special handling for the case 1) Procedure or Condition matched a filter, but 2) an Encounter was requested
            elif (
                resource._base_type in ["Procedure", "Condition", "Observation"]
                and (resource_type == "Encounter")
                and (isinstance(encounter := resource["encounter"], FhirBase))
                and not is_null(encounter["reference"])
                and (encounter["reference"] in self.resource_id_index)
            ):
                # possibility 1: Procedure or Encounter reference an Encounter- look up the Encounter and return it
                related_encounter_resouce = Resource(
                    self.resource_id_index[encounter["reference"]],
                    "Encounter",
                    self,
                )
                related_encounter_resouce.set_property("status", "finished")
                yield related_encounter_resouce

            else:
                yield self.__generate_resource_proxy(resource, resource_type)

    def __getitem__(
        self,
        resource_query: Union[str, tuple[str, Union[ValueSet, list[Code], Code], str]],
    ) -> Sequence[FhirBase]:
        duration_start_time = datetime.now()

        query = ResourceQuery.from_query(resource_query)

        if query in self.retrieve_cache:
            print(
                f"retrieve from cache duration={(datetime.now() - duration_start_time).total_seconds()} resourceType={query.resource_type} filter={query.description}"
            )
            return self.retrieve_cache[query]

        resources = list(self.__retrieve_resources(query))

        if query.property_filter is None:
            return resources

        if self.__parameter_provider[Parameter("strict", "String")] == "True":
            print(
                f"retrieve strict=True resources={len(resources)} duration={(datetime.now() - duration_start_time).total_seconds()} resourceType={query.resource_type} filter={query.description}"
            )
            self.retrieve_cache[query] = resources

            return resources

        resource_proxies = list(
            self.__build_resource_proxies(
                resource_type=query.resource_type, resources=resources
            )
        )
        print(
            f"retrieve resources={len(resource_proxies)} duration={(datetime.now() - duration_start_time).total_seconds()} resourceType={query.resource_type} filter={query.description}"
        )
        self.retrieve_cache[query] = resource_proxies

        return resource_proxies

    def __generate_resource_proxy(
        self, resource: Resource, preferred_type: str
    ) -> Resource:
        resource_translation = f"{preferred_type}~{resource._base_type}"

        proxy_resource = Resource(
            json.loads(json.dumps(resource._fhir_json)),
            preferred_type,
            self,
        )
        proxy_resource._base_type = preferred_type
        proxy_resource.set_property("derivedFromResourceType", resource._base_type)
        proxy_resource.set_property("resourceType", preferred_type)

        proxy_properties = {}
        if resource_translation in RESOURCE_PROXIES:
            proxy_properties = RESOURCE_PROXIES[resource_translation]

        for property in proxy_properties:
            if "literal:" in proxy_properties[property]:
                proxy_resource.set_property(
                    property, proxy_properties[property].replace("literal:", "")
                )
            elif "period:" in proxy_properties[property]:
                proxy_resource.set_property(
                    property,
                    {
                        "start": resource.get_property(
                            proxy_properties[property].replace("period:", "")
                        )
                    },
                )
            else:
                proxy_resource.set_property(
                    property, resource.get_property(proxy_properties[property])
                )

        return proxy_resource
