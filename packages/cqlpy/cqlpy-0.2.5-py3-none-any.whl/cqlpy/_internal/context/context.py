import json
from typing import Optional, Union
from cqlpy._internal.context.cql_value_set_provider import CqlValueSetProvider

from cqlpy._internal.context.fhir.r4.model import FhirR4DataModel
from cqlpy._internal.context.parameter_provider import ParameterProvider
from cqlpy._internal.parameter import Parameter
from cqlpy._internal.types.code import Code
from cqlpy._internal.types.value_set import ValueSet
from cqlpy._internal.valueset_provider import ValueSetProvider


class Context:
    """
    A context is a required parameter on every CQL expression that is converted to python as a function.
    The expected signature of every function that implements a CQL Expression is:

        def EXPRESSION_NAME(context: Context):

    The Context provides access to the data model, parameter values, and value set codes as needed by the internal elements
    of a python function that implements a CQL expression. The Context provides access to these concepts via a retrieve operation
    that is implemented with syntax such as:

        context["Encounter"]    # if a string is requested (assumed to be a FHIR resource type), context returns a
                                # list of Resources from the model, in this case all Encounter resources.

        context["Encounter", ValueSet, "type"]
                                # if a tuple is requested (assumed to be a FHIR resource type), context returns a
                                # list of Resources from the model, in this case Encounter resources, filtered by
                                # checking the specified property to see if it has a coded value in the specified value set.

        context[Parameter]      # if a Parameter is requested, context returns the type specified by the Parameter
                                # with value determined by the parameter_provider from external parameters or the default value.

        context[ValueSet]       # if a ValueSet is requested, context returns a ValueSet that includes with Codes property populated
                                # from the value_set_provider.

    The Context iterates through the bundle (as a json object) to retrieve a list of Resources.

    Properties of Resources can be obtained using syntax such as:

        Encounter["period"]     # The property of the resource is properly typed when requested (in this case, Interval)
                                # by parsing the related bundle json element.

    Context Resource retrieve operations and Resource property retrieve operations are cached so that iterating through the bundle
    and parsing json is only performed once (at time of the first request).
    """

    def __init__(
        self,
        valueset_provider: ValueSetProvider,
        bundle: Optional[Union[str, dict]] = None,
        bundle_file_name: Optional[str] = None,
        parameters: Optional[dict] = None,
    ):
        parsed_bundle = None
        if bundle_file_name:
            with open(bundle_file_name, encoding="utf-8") as f:
                parsed_bundle = json.loads(f.read())

        if isinstance(bundle, str):
            parsed_bundle = json.loads(bundle)

        if isinstance(bundle, dict):
            parsed_bundle = bundle

        if parsed_bundle is None:
            raise ValueError("bundle or bundle_file_name must be specified")

        self.parameter_provider = ParameterProvider(parameters)
        self.model = FhirR4DataModel(parsed_bundle, self.parameter_provider)
        self.cql_valueset_provider = CqlValueSetProvider(
            valueset_provider=valueset_provider
        )

    def __getitem__(self, requested_concept: Union[Parameter, ValueSet, str, tuple]):
        if isinstance(requested_concept, Parameter):
            # In this case, the return type will be the Cql Type specified by the parameter,
            # i.e. Interval<DateTime>, CqlString, etc.
            return self.parameter_provider[requested_concept]

        elif isinstance(requested_concept, ValueSet):
            # In this case, the return type will be ValueSet (which includes all codes specified by the value set).
            return self.cql_valueset_provider[requested_concept]

        elif isinstance(requested_concept, Code):
            # In this case, there is nothing to lookup... the Code is fully populated.
            return requested_concept

        else:
            return self.model[requested_concept]

    def set_context(self, context: str) -> None:
        # At this time, only Patient context is supported and the context is stored without additional action.
        # The current implementation can be extended to support additional contexts by using this stored context in
        # retrieve operations (implemented in __getitem__) to filter the resources returned from the model.
        self.context = context

    def initialize(self, model, parameter_provider, cql_valueset_provider) -> None:
        self.model = model
        self.parameter_provider = parameter_provider
        self.cql_valueset_provider = cql_valueset_provider
