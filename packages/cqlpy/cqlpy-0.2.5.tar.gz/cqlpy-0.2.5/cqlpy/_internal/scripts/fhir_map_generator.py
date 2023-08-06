# %%
from argparse import ArgumentParser
from dataclasses import dataclass, field
from pathlib import Path
from itertools import groupby
from typing import Optional
import json


# %%
def identify_shared_prefix(texts: list[str]) -> str:
    shared_text = None
    for text in texts:
        if shared_text is None:
            shared_text = text
            continue

        last_index = min(len(shared_text), len(text))
        for index in range(last_index):
            if shared_text[index] != text[index]:
                shared_text = shared_text[:index]
                break

    if shared_text is None:
        raise ValueError("No shared text found")
    return shared_text


def extract_choices(resource: dict) -> dict[str, list[str]]:
    property_descriptions = {
        property: value
        for property, attributes in resource["properties"].items()
        for key, value in attributes.items()
        if key == "description"
    }
    sorted_descriptions = dict(
        sorted(property_descriptions.items(), key=lambda x: x[1])
    )
    grouped_descriptions = groupby(
        sorted_descriptions, lambda value: property_descriptions[value]
    )
    shared_descriptions = []
    for _, group in grouped_descriptions:
        shared = list(group)
        if len(shared) > 1:
            shared_descriptions.append(shared)

    return {identify_shared_prefix(shared): shared for shared in shared_descriptions}


def extract_resources(
    schema: dict,
) -> tuple[list[str], list[str], list[str]]:
    resources = [
        one_of["$ref"].replace("#/definitions/", "")
        for one_of in schema["definitions"]["ResourceList"]["oneOf"]
    ]
    backbone_keys = sorted(
        [
            key
            for key in schema["definitions"].keys()
            if any(
                key.startswith(f"{resource}_") and key != resource
                for resource in resources
            )
        ]
    )
    not_resources = [
        key
        for key in schema["definitions"].keys()
        if key not in resources and key != "ResourceList" and key not in backbone_keys
    ]
    return resources, backbone_keys, not_resources


def _get_property_item_type(items: dict) -> str:
    item_type = items.get("type")
    if item_type is not None:
        return item_type

    ref = items.get("$ref")
    if ref is not None:
        return ref

    if "enum" in items:
        return "string"

    raise ValueError("PropertyDeclaration must have type or ref")


@dataclass
class PropertyDeclaration:
    name: str
    type: str
    ref: Optional[str] = None
    item_type: Optional[str] = None
    choices: list["PropertyDeclaration"] = field(default_factory=list)

    @property
    def declared_type(self) -> str:
        if self.ref is not None:
            return self.ref
        return self.type

    @classmethod
    def from_schema(cls, name: str, schema: dict) -> "PropertyDeclaration":
        ref = schema.get("$ref")
        enum = schema.get("enum")

        type = None
        if enum is not None:
            type = "enum"
        elif ref is not None:
            type = "ref"
        else:
            type = schema.get("type")

        if type is None:
            raise ValueError("PropertyDeclaration type cannot be determined")
        item_type = None
        if type == "array":
            item_type = _get_property_item_type(schema["items"])

        return cls(
            name=name,
            type=type,
            ref=ref,
            item_type=item_type,
        )

    def __post_init__(self):
        if self.type is None and self.ref is None:
            raise ValueError("PropertyDeclaration must have type or ref")
        if self.type == "array" and self.item_type is None:
            raise ValueError("PropertyDeclaration must have item_type for array")
        if self.type == "choice" and len(self.choices) == 0:
            raise ValueError("PropertyDeclaration must have choices for choice")

    def __str__(self):
        return f"{self.name}: {self.declared_type}"

    def __repr__(self):
        declared_type = self.declared_type
        if self.type == "array":
            declared_type = f"array<{self.item_type}>"
        if self.type == "choice":
            declared_type = (
                f"choice<{'|'.join([str(choice) for choice in self.choices])}>"
            )
        return f"PropertyDeclaration({self.name}, {declared_type})"


def build_resource_declaration(resource: dict) -> dict[str, PropertyDeclaration]:
    choices = extract_choices(resource)
    property_declarations = {
        prop: PropertyDeclaration.from_schema(prop, attributes)
        for prop, attributes in resource["properties"].items()
        if any(
            type_property in attributes for type_property in ["$ref", "type", "enum"]
        )
        and not prop.startswith("_")
    }
    choice_declarations = {}
    for name, declaration in property_declarations.items():
        choice = next(
            (choice for choice, values in choices.items() if name in values), None
        )
        if choice is None:
            choice_declarations[name] = declaration
            continue

        if choice not in choice_declarations:
            choice_declarations[choice] = PropertyDeclaration(
                name=choice,
                type="choice",
                choices=[declaration],
            )
            continue

        choice_declarations[choice].choices.append(declaration)

    return choice_declarations


_DIRECTLY_MAPPED_TYPES = {
    "boolean": "Boolean",
    "integer": "Integer",
    "decimal": "Decimal",
    "date": "Date",
    "dateTime": "DateTime",
    "code": "Code",
    "Coding": "Code",
    "CodeableConcept": "Concept",
    "Quantity": "Decimal",
    "Period": "Interval<DateTime>",
    "Range": "Interval<Decimal>",
}


class DeclarationMapper:
    def __init__(
        self,
        backbone_elements: list[str],
    ) -> None:
        self.__backbone_elements = backbone_elements

    def map_fhir_to_cql_type(self, fhir_type: str) -> str:
        directly_mapped_type = _DIRECTLY_MAPPED_TYPES.get(fhir_type)
        if directly_mapped_type is not None:
            return directly_mapped_type
        return "String"

    def map_ref_to_cql_type(self, ref: Optional[str]) -> str:
        if ref is None:
            raise ValueError("PropertyDeclaration must have ref for ref")
        identifier = ref.replace("#/definitions/", "")
        if identifier in _DIRECTLY_MAPPED_TYPES:
            return self.map_fhir_to_cql_type(identifier)
        if identifier in self.__backbone_elements:
            return f"BackboneElement:{identifier}"

        return self.map_fhir_to_cql_type(identifier)

    def map_array_to_cql_type(self, item_type: Optional[str]) -> str:
        if item_type is None:
            raise ValueError("PropertyDeclaration must have item_type for array")
        if item_type.startswith("#/definitions/"):
            return f"List<{self.map_ref_to_cql_type(item_type)}>"
        return f"List<{self.map_fhir_to_cql_type(item_type)}>"

    def map_declaration_to_cql_type(self, declaration: PropertyDeclaration) -> str:
        if declaration.type == "choice":
            choices = "|".join(
                list(
                    {
                        self.map_declaration_to_cql_type(choice)
                        for choice in declaration.choices
                    }
                )
            )
            if "Interval<DateTime>" in choices:
                return "Choice:Interval<DateTime>"
            return f"Choice:String"
        if declaration.type == "enum":
            return "String"
        if declaration.type == "array":
            return self.map_array_to_cql_type(declaration.item_type)
        if declaration.type == "ref":
            return self.map_ref_to_cql_type(declaration.ref)

        return self.map_fhir_to_cql_type(declaration.type)


# %%
def main(file_path: str):
    schema_file = Path(file_path)
    schema = json.loads(schema_file.read_text(encoding="utf-8"))

    resources, backbone_elements, not_resources = extract_resources(schema)
    ersatz_backbones = [
        not_resource
        for not_resource in not_resources
        if "properties" in schema["definitions"][not_resource]
        and not_resource not in _DIRECTLY_MAPPED_TYPES.values()
    ]
    resource_declarations = {
        resource: build_resource_declaration(schema["definitions"][resource])
        for resource in resources
    }
    backbone_declarations = {
        backbone: build_resource_declaration(schema["definitions"][backbone])
        for backbone in backbone_elements + ersatz_backbones
    }

    mapper = DeclarationMapper(backbone_elements + ersatz_backbones)

    resource_cql_declarations = {
        resource: {
            name: mapper.map_declaration_to_cql_type(declaration)
            for name, declaration in declarations.items()
        }
        for resource, declarations in resource_declarations.items()
    }
    backbone_cql_declarations = {
        backbone: {
            name: mapper.map_declaration_to_cql_type(declaration)
            for name, declaration in declarations.items()
        }
        for backbone, declarations in backbone_declarations.items()
    }

    return {
        **dict(sorted(resource_cql_declarations.items(), key=lambda x: x[0])),
        **dict(sorted(backbone_cql_declarations.items(), key=lambda x: x[0])),
    }


# %%
if __name__ == "__main__":
    argument_parser = ArgumentParser()
    argument_parser.add_argument("file_path", type=str)
    args = argument_parser.parse_args()
    print(main(args.file_path))
    # print(main("C:/Users/jerem/Downloads/fhir.schema.json/fhir.schema.json"))
