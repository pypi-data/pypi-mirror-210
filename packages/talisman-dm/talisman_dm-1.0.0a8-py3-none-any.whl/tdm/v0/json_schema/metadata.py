from typing import Optional, Tuple, Union

from tdm.legacy import MetadataModel


class FactMetadataModel(MetadataModel):
    created_time: Optional[int]
    modified_time: Optional[int]
    fact_confidence: Optional[Tuple[float]]
    value_confidence: Union[float, Tuple[float, ...], None]  # same as Optional[float, Tuple[float, ...]] (pydantic bug workaround)

    class Config:
        extra = 'allow'  # any other extra fields will be kept
