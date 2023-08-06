from cqlpy._internal.types.value_set import ValueSet
from cqlpy._internal.valueset_provider import ValueSetProvider


class CqlValueSetProvider:
    def __init__(self, valueset_provider: ValueSetProvider) -> None:
        self._valueset_provider = valueset_provider

    def __getitem__(self, value_set: ValueSet) -> ValueSet:
        if value_set.id is None:
            raise ValueError("value set id must be specified")

        name = value_set.id.replace("http://cts.nlm.nih.gov/fhir/ValueSet/", "")
        result = self._valueset_provider.get_valueset(name=name, scope=None)

        if result:
            return ValueSet.parse_fhir_json(result)

        print(f"value set 'scopeless:{value_set.name}' not found")

        return value_set
