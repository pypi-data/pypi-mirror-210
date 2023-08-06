from datetime import datetime  # this is important to have at the top

from typing import List, Optional, Sequence, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore


from pydantic import Field

from fhirkit.Resource import DomainResource, ResourceWithMultiIdentifier
from fhirkit.primitive_datatypes import Code, time
from fhirkit.elements import (
    CodeableConcept,
    Identifier,
    Period,
    Quantity,
    Range,
    Ratio,
    Reference,
    BackboneElement,
)

ValueType = Union[
    str, Quantity, int, CodeableConcept, bool, Range, Ratio, time, datetime, Period
]

ObservationStatus = Literal[
    "registered",
    "preliminary",
    "final",
    "amended",
    "corrected",
    "cancelled",
    "enterred-in-error",
    "unknown",
    ] 
    
class ObservationComponent(BackboneElement):
    code: CodeableConcept
    valueString: Optional[str] = Field(None, repr=True)
    valueQuantity: Optional[Quantity] = Field(None, repr=True)
    valueInteger: Optional[int] = Field(None, repr=True)
    valueCodeableConcept: Optional[CodeableConcept] = Field(None, repr=True)
    valueBoolean: Optional[bool] = Field(None, repr=True)
    valueRatio: Optional[Ratio] = Field(None, repr=True)
    valueTime: Optional[time] = Field(None, repr=True)
    valueDateTime: Optional[datetime] = Field(None, repr=True)
    valuePeriod: Optional[Period] = Field(None, repr=True)


class Observation(DomainResource, ResourceWithMultiIdentifier):

    resourceType: Literal["Observation"] = Field("Observation", const=True)
    identifier: Sequence[Identifier] = Field([], repr=True)
    partOf: Optional[List[Reference]] = Field([], repr=True)
    status: ObservationStatus = Field("final", repr=True)
    category: Optional[Sequence[CodeableConcept]] = Field([], repr=True)
    code: CodeableConcept = Field(..., repr=True)
    subject: Optional[Reference]
    encounter: Optional[Reference]
    
    effectivePeriod: Optional[Period] = Field(None, repr=True)
    effectiveDateTime: Optional[datetime] = Field(None, repr=True)
    
    performer: Optional[Reference]
    
    valueString: Optional[str] = Field(None, repr=True)
    valueQuantity: Optional[Quantity] = Field(None, repr=True)
    valueInteger: Optional[int] = Field(None, repr=True)
    valueCodeableConcept: Optional[CodeableConcept] = Field(None, repr=True)
    valueBoolean: Optional[bool] = Field(None, repr=True)
    valueRatio: Optional[Ratio] = Field(None, repr=True)
    valueTime: Optional[time] = Field(None, repr=True)
    valueDateTime: Optional[datetime] = Field(None, repr=True)
    valuePeriod: Optional[Period] = Field(None, repr=True)
    
    method: Optional[Code] = Field(None, repr=False)
    derivedFrom: Optional[Reference]
    component: List[ObservationComponent] = Field([], repr=True)
