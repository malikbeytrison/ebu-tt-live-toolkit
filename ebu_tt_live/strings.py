
from gettext import gettext

# ERRORS
ERR_CONV_NO_INPUT = gettext('The converter has no input set')
ERR_TIME_WRONG_FORMAT = gettext('Wrong time format. datetime.timedelta is expected')
ERR_TIME_FORMAT_OVERFLOW = gettext('Time value is out of format range')
ERR_DOCUMENT_SEQUENCE_MISMATCH = gettext('sequenceIdentifier mismatch')
ERR_DECODING_XML_FAILED = gettext('XML document parsing failed')
ERR_SEMANTIC_VALIDATION_TIMING_TYPE = gettext('{attr_type}({attr_value}) is not a valid type for {attr_name} in timeBase={time_base}')
ERR_SEMANTIC_VALIDATION_MISSING_ATTRIBUTES = gettext('{elem_name} is missing attributes: {attr_names}')
ERR_SEMANTIC_VALIDATION_INVALID_ATTRIBUTES = gettext('{elem_name} has invalid attributes: {attr_names}')
ERR_SEMANTIC_STYLE_MISSING = gettext('Style: {style} is not found.')
ERR_SEMANTIC_STYLE_CIRCLE = gettext('Style: {style} is in a circular reference.')
ERR_SEMANTIC_VALIDATION_EXPECTED = gettext('Please run semantic validation before calling this function')
ERR_SEMANTIC_ELEMENT_BY_ID_MISSING = gettext('Element with {id} is not found')
ERR_SEMANTIC_REGION_MISSING = gettext('Region: {region} is not found.')
ERR_SEMANTIC_ID_UNIQUENESS = gettext('XML ID is not unique: {id}')
ERR_DOCUMENT_NOT_COMPATIBLE = gettext('Document is not compatible with the sequence. Conflicting attributes: {attr_names}')
ERR_DOCUMENT_NOT_PART_OF_SEQUENCE = gettext('Document is not part of any sequence')
ERR_DOCUMENT_SEQUENCE_INCONSISTENCY = gettext('Timeline consistency problem.')
ERR_DOCUMENT_EXTENT_MISSING = gettext('{type} cannot be instantiated from {value} because document extent is missing (from the tt element)')
END_OF_DATA = gettext('End of available data reached')


DOC_SYNTACTIC_VALIDATION_SUCCESSFUL = gettext('Syntactic validation successful')
DOC_SEMANTIC_VALIDATION_SUCCESSFUL = gettext('Document {sequence_identifier}__{sequence_number} semantic validation successful')
DOC_DISCARDED = gettext('Document {sequence_identifier}__{sequence_number} is discarded')
DOC_INSERTED = gettext('Document {sequence_identifier}__{sequence_number} inserted into sequence')
DOC_TRIMMED = gettext('Document {sequence_identifier}__{sequence_number} activation change: [{resolved_begin_time}; {resolved_end_time}]')
DOC_RECEIVED = gettext('Document {sequence_identifier}__{sequence_number} received. Calculated activation: [{computed_begin_time}; {computed_end_time}]')
DOC_REQ_SEGMENT = gettext('{sequence_identifier}__{sequence_number}: requesting segment ({begin} - {end})')
DOC_SEQ_REQ_SEGMENT = gettext('{sequence_identifier}: requesting segment ({begin} - {end})')
