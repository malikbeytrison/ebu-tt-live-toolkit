# -*- coding: utf-8 -*-
from .raw import *
from . import raw

# Let's import customizations
from . import _ebuttdt as ebuttdt
from . import _ebuttm as ebuttm
from . import _ebuttp as ebuttp
from . import _ebutts as ebutts
from . import _ttm as ttm
from . import _ttp as ttp
from . import _tts as tts
from .pyxb_utils import xml_parsing_context, get_xml_parsing_context
from .validation.base import SemanticDocumentMixin, SemanticValidationMixin, IDMixin
from ebu_tt_live.bindings.validation.presentation import SizingValidationMixin, StyledElementMixin, RegionedElementMixin
from ebu_tt_live.bindings.validation.timing import TimingValidationMixin, BodyTimingValidationMixin
from ebu_tt_live.bindings.validation.content import SubtitleContentContainer, ContentContainerMixin
from .validation.validator import SemanticValidator
from ebu_tt_live.errors import SemanticValidationError, OutsideSegmentError
from ebu_tt_live.strings import ERR_SEMANTIC_VALIDATION_MISSING_ATTRIBUTES, \
    ERR_SEMANTIC_VALIDATION_INVALID_ATTRIBUTES, ERR_SEMANTIC_STYLE_CIRCLE, ERR_SEMANTIC_STYLE_MISSING, \
    ERR_SEMANTIC_ELEMENT_BY_ID_MISSING, ERR_SEMANTIC_VALIDATION_EXPECTED
from pyxb.exceptions_ import SimpleTypeValueError
from pyxb.utils.domutils import BindingDOMSupport
from pyxb.binding.basis import ElementContent, NonElementContent
from datetime import timedelta
import threading
import copy
import logging


log = logging.getLogger(__name__)


namespace_prefix_map = {
    'tt': raw.Namespace,
    'ebuttdt': ebuttdt.Namespace,
    'ttp': ttp.Namespace,
    'tts': tts.Namespace,
    'ttm': ttm.Namespace,
    'ebuttm': ebuttm.Namespace,
    'ebutts': ebutts.Namespace,
    'ebuttp': ebuttp.Namespace
}


def CreateFromDocument(*args, **kwargs):
    """
    Resetting the parsing context on start
    :return:
    """
    with xml_parsing_context():
        result = raw.CreateFromDocument(*args, **kwargs)
    return result


def CreateFromDOM(*args, **kwargs):
    """
    Resetting the parsing context on start
    :return:
    """
    with xml_parsing_context():
        result = raw.CreateFromDOM(*args, **kwargs)
    return result


# Customizing validation mixins before application
# ================================================


class LiveStyledElementMixin(StyledElementMixin):

    @classmethod
    def assign_style_type(cls, style_type_in):
        cls._compatible_style_type = style_type_in


# EBU TT Live classes
# ===================


class tt_type(SemanticDocumentMixin, raw.tt_type):

    def __post_time_base_set_attribute(self, attr_use):
        context = get_xml_parsing_context()
        if context is not None:
            # This means we are in XML parsing mode
            context['timeBase'] = self.timeBase

    _attr_en_post = {
        (pyxb.namespace.ExpandedName(ttp.Namespace, 'timeBase')).uriTuple(): __post_time_base_set_attribute
    }
    _elements_by_id = None
    _validator_class = SemanticValidator

    def __copy__(self):
        copied_tt = tt_type(
            lang=self.lang,
            extent=self.extent,
            timeBase=self.timeBase,
            frameRate=self.frameRate,
            frameRateMultiplier=self.frameRateMultiplier,
            markerMode=self.markerMode,
            dropMode=self.dropMode,
            clockMode=self.clockMode,
            cellResolution=self.cellResolution,
            sequenceIdentifier=self.sequenceIdentifier,
            sequenceNumber=self.sequenceNumber,
            authoringDelay=self.authoringDelay,
            authorsGroupIdentifier=self.authorsGroupIdentifier,
            authorsGroupControlToken=self.authorsGroupControlToken,
            authorsGroupControlRequest=self.authorsGroupControlRequest,
            referenceClockIdentifier=self.referenceClockIdentifier,
            _strict_keywords=False
        )
        return copied_tt

    def merge(self, other, dataset):
        # TODO: compatibility check, rules of merging TBD
        # merged_tt = tt_type(
        #     lang=self.lang,
        #     extent=self.extent,
        #     timeBase=self.timeBase,
        #     frameRate=self.frameRate,
        #     frameRateMultiplier=self.frameRateMultiplier,
        #     markerMode=self.markerMode,
        #     dropMode=self.dropMode,
        #     clockMode=self.clockMode,
        #     cellResolution=self.cellResolution,
        #     sequenceIdentifier=self.sequenceIdentifier,
        #     sequenceNumber=self.sequenceNumber,
        #     authoringDelay=self.authoringDelay,
        #     authorsGroupIdentifier=self.authorsGroupIdentifier,
        #     authorsGroupControlToken=self.authorsGroupControlToken,
        #     authorsGroupControlRequest=self.authorsGroupControlRequest,
        #     referenceClockIdentifier=self.referenceClockIdentifier,
        #     _strict_keywords=False
        # )
        return self

    @classmethod
    def __check_bds(cls, bds):
        if bds:
            return bds
        else:
            return BindingDOMSupport(
                namespace_prefix_map=namespace_prefix_map
            )

    def toDOM(self, bds=None, parent=None, element_name=None):
        return super(tt_type, self).toDOM(
            bds=self.__check_bds(bds),
            parent=parent,
            element_name=element_name
        )

    def toxml(self, encoding=None, bds=None, root_only=False, element_name=None):
        dom = self.toDOM(self.__check_bds(bds), element_name=element_name)
        if root_only:
            dom = dom.documentElement
        return dom.toprettyxml(
            encoding=encoding,
            indent='  '
        )

    def _semantic_after_subtree_copy(self, copied_instance, dataset, element_content=None):
        # This one does not have another parent to link with but it can make itself an element
        copied_instance._setElement(raw.tt)

    def __semantic_test_smpte_attrs_present(self):
        smpte_attrs = [
            'frameRate',
            # 'frameRateMultiplier',
            'dropMode',
            'markerMode'
        ]
        missing_attrs = self._semantic_attributes_missing(smpte_attrs)
        if missing_attrs:
            raise SemanticValidationError(
                ERR_SEMANTIC_VALIDATION_MISSING_ATTRIBUTES.format(
                    elem_name='tt:tt',
                    attr_names=missing_attrs
                )
            )

    def __semantic_test_smpte_attrs_absent(self):
        smpte_attrs = [
            'dropMode',
            'markerMode'
        ]
        extra_attrs = self._semantic_attributes_present(smpte_attrs)
        if extra_attrs:
            raise SemanticValidationError(
                ERR_SEMANTIC_VALIDATION_INVALID_ATTRIBUTES.format(
                    elem_name='tt:tt',
                    attr_names=extra_attrs
                )
            )

    def __semantic_test_time_base_clock_attrs_present(self):
        clock_attrs = [
            'clockMode'
        ]
        missing_attrs = self._semantic_attributes_missing(clock_attrs)
        if missing_attrs:
            raise SemanticValidationError(
                ERR_SEMANTIC_VALIDATION_MISSING_ATTRIBUTES.format(
                    elem_name='tt:tt',
                    attr_names=missing_attrs
                )
            )


    def __semantic_test_time_base_clock_attrs_absent(self):
        clock_attrs = [
            'clockMode'
        ]
        extra_attrs = self._semantic_attributes_present(clock_attrs)
        if extra_attrs:
            raise SemanticValidationError(
                ERR_SEMANTIC_VALIDATION_MISSING_ATTRIBUTES.format(
                    elem_name='tt:tt',
                    attr_names=extra_attrs
                )
            )

    def __semantic_test_smpte_attr_combinations(self):
        # TODO: SMPTE validation(low priority) #52
        pass

    def _semantic_before_validation(self):
        """
        Here before anything semantic happens I check some SYNTACTIC errors.
        :raises ComplexTypeValidationError, SimpleTypeValueError
        """
        # The following edge case is ruined by the XSD associating the same extent type to this extent element.
        if self.extent is not None and not isinstance(self.extent, ebuttdt.pixelExtentType):
            raise SimpleTypeValueError(type(self.extent), self.extent)

    def _semantic_before_traversal(self, dataset, element_content=None):
        # The tt element adds itself to the semantic dataset to help classes lower down the line to locate constraining
        # attributes.
        dataset['timing_begin_stack'] = []
        dataset['timing_end_stack'] = []
        dataset['timing_syncbase'] = timedelta()
        dataset['timing_end_limit'] = None
        dataset['timing_begin_limit'] = None
        dataset['tt_element'] = self
        dataset['styles_stack'] = []
        self._elements_by_id = {}
        dataset['elements_by_id'] = self._elements_by_id
        if self.timeBase == 'smpte':
            self.__semantic_test_smpte_attrs_present()
        else:
            self.__semantic_test_smpte_attrs_absent()
        if self.timeBase == 'clock':
            self.__semantic_test_time_base_clock_attrs_present()
        else:
            self.__semantic_test_time_base_clock_attrs_absent()

    def _semantic_after_traversal(self, dataset, element_content=None):
        # Save this for id lookup.
        self._elements_by_id = dataset['elements_by_id']

    def get_element_by_id(self, elem_id, elem_type=None):
        """
        Lookup an element and return it. Optionally type is checked as well.
        :param elem_id:
        :param elem_type:
        :return:
        """
        if self._elements_by_id is None:
            raise SemanticValidationError(ERR_SEMANTIC_VALIDATION_EXPECTED)
        element = self._elements_by_id.get(elem_id, None)
        if element is None or elem_type is not None and not isinstance(element, elem_type):
            raise LookupError(ERR_SEMANTIC_ELEMENT_BY_ID_MISSING.format(id=elem_id))
        return element

    def get_timing_type(self, timedelta_in):
        if self.timeBase == 'clock':
            return ebuttdt.LimitedClockTimingType(timedelta_in)
        if self.timeBase == 'media':
            return ebuttdt.FullClockTimingType(timedelta_in)
        if self.timeBase == 'smpte':
            return ebuttdt.SMPTETimingType(timedelta_in)


raw.tt_type._SetSupersedingClass(tt_type)


# Head classes
# ============


class head_type(SemanticValidationMixin, raw.head_type):

    def __copy__(self):
        copied_head = head_type()
        return copied_head

    def merge(self, other_elem, dataset):
        return self

raw.head_type._SetSupersedingClass(head_type)


# Body classes
# ============


class p_type(RegionedElementMixin, SubtitleContentContainer, raw.p_type):

    _attr_en_pre = {
        (pyxb.namespace.ExpandedName(None, 'begin')).uriTuple(): TimingValidationMixin._pre_timing_set_attribute,
        (pyxb.namespace.ExpandedName(None, 'end')).uriTuple(): TimingValidationMixin._pre_timing_set_attribute
    }

    def _semantic_copy(self, dataset):
        copied_p = p_type(
            id=self.id,
            space=self.space,
            lang=self.lang,
            region=self._semantic_deconflicted_ids(attr_name='region', dataset=dataset),
            style=self._semantic_deconflicted_ids(attr_name='style', dataset=dataset),
            begin=self.begin,
            end=self.end,
            agent=self.agent,
            role=self.role,
            _strict_keywords=False
        )
        return copied_p

    def __copy__(self):
        copied_p = p_type(
            id=self.id,
            space=self.space,
            lang=self.lang,
            region=self.region,
            style=self.style,
            begin=self.begin,
            end=self.end,
            agent=self.agent,
            role=self.role,
            _strict_keywords=False
        )
        return copied_p

    def _semantic_before_traversal(self, dataset, element_content=None):
        self._semantic_register_id(dataset=dataset)
        self._semantic_timebase_validation(dataset=dataset, element_content=element_content)
        self._semantic_preprocess_timing(dataset=dataset, element_content=element_content)
        self._semantic_set_region(dataset=dataset, region_type=region_type)
        self._semantic_collect_applicable_styles(dataset=dataset, style_type=style_type)
        self._semantic_push_styles(dataset=dataset)

    def _semantic_after_traversal(self, dataset, element_content=None):
        self._semantic_postprocess_timing(dataset=dataset, element_content=element_content)
        self._semantic_manage_timeline(dataset=dataset, element_content=element_content)
        self._semantic_unset_region(dataset=dataset)
        self._semantic_pop_styles(dataset=dataset)

    def _semantic_before_copy(self, dataset, element_content=None):
        self._assert_in_segment(dataset=dataset, element_content=element_content)

    def _is_timed_leaf(self):
        if len(self.span):
            return False
        else:
            return True

    def _semantic_after_subtree_copy(self, copied_instance, dataset, element_content=None):
        copied_instance._assert_empty_container()
        self._semantic_copy_apply_leaf_timing(
            copied_instance=copied_instance, dataset=dataset, element_content=element_content)
        self._semantic_copy_verify_referenced_styles(dataset=dataset)
        self._semantic_copy_verify_referenced_region(dataset=dataset)


raw.p_type._SetSupersedingClass(p_type)


class span_type(SubtitleContentContainer, raw.span_type):

    _attr_en_pre = {
        (pyxb.namespace.ExpandedName(None, 'begin')).uriTuple(): TimingValidationMixin._pre_timing_set_attribute,
        (pyxb.namespace.ExpandedName(None, 'end')).uriTuple(): TimingValidationMixin._pre_timing_set_attribute
    }

    def _semantic_copy(self, dataset):
        copied_span = span_type(
            id=self.id,
            style=self._semantic_deconflicted_ids(attr_name='style', dataset=dataset),
            begin=self.begin,
            end=self.end,
            space=self.space,
            lang=self.lang,
            agent=self.agent,
            role=self.role,
            _strict_keywords=False
        )
        return copied_span

    def __copy__(self):
        copied_span = span_type(
            id=self.id,
            style=self.style,
            begin=self.begin,
            end=self.end,
            space=self.space,
            lang=self.lang,
            agent=self.agent,
            role=self.role,
            _strict_keywords=False
        )
        return copied_span

    def _semantic_before_traversal(self, dataset, element_content=None):
        self._semantic_register_id(dataset=dataset)
        self._semantic_timebase_validation(dataset=dataset, element_content=element_content)
        self._semantic_preprocess_timing(dataset=dataset, element_content=element_content)
        self._semantic_collect_applicable_styles(dataset=dataset, style_type=style_type)
        self._semantic_push_styles(dataset=dataset)

    def _semantic_after_traversal(self, dataset, element_content=None):
        self._semantic_postprocess_timing(dataset=dataset, element_content=element_content)
        self._semantic_manage_timeline(dataset=dataset, element_content=element_content)
        self._semantic_pop_styles(dataset=dataset)

    def _semantic_before_copy(self, dataset, element_content=None):
        self._assert_in_segment(dataset=dataset, element_content=element_content)

    def _is_timed_leaf(self):
        if len(self.span):
            return False
        else:
            return True

    def _semantic_after_subtree_copy(self, copied_instance, dataset, element_content=None):
        copied_instance._assert_empty_container()
        self._semantic_copy_apply_leaf_timing(
            copied_instance=copied_instance, dataset=dataset, element_content=element_content)
        self._semantic_copy_verify_referenced_styles(dataset=dataset)

raw.span_type._SetSupersedingClass(span_type)


class br_type(SemanticValidationMixin, raw.br_type):

    def __copy__(self):
        return br_type()


raw.br_type._SetSupersedingClass(br_type)


class div_type(ContentContainerMixin, IDMixin, RegionedElementMixin, StyledElementMixin, TimingValidationMixin,
               SemanticValidationMixin, raw.div_type):

    _attr_en_pre = {
        (pyxb.namespace.ExpandedName(None, 'begin')).uriTuple(): TimingValidationMixin._pre_timing_set_attribute,
        (pyxb.namespace.ExpandedName(None, 'end')).uriTuple(): TimingValidationMixin._pre_timing_set_attribute
    }

    def _semantic_copy(self, dataset):
        copied_div = div_type(
            id=self.id,
            region=self._semantic_deconflicted_ids(attr_name='region', dataset=dataset),
            style=self._semantic_deconflicted_ids(attr_name='style', dataset=dataset),
            agent=self.agent,
            role=self.role,
            begin=self.begin,
            end=self.end,
            _strict_keywords=False
        )
        return copied_div

    def __copy__(self):
        copied_div = div_type(
            id=self.id,
            region=self.region,
            style=self.style,
            agent=self.agent,
            role=self.role,
            begin=self.begin,
            end=self.end,
            _strict_keywords=False
        )
        return copied_div

    def _semantic_before_traversal(self, dataset, element_content=None):
        self._semantic_register_id(dataset=dataset)
        self._semantic_timebase_validation(dataset=dataset, element_content=element_content)
        self._semantic_preprocess_timing(dataset=dataset, element_content=element_content)
        self._semantic_set_region(dataset=dataset, region_type=region_type)
        self._semantic_collect_applicable_styles(dataset=dataset, style_type=style_type)
        self._semantic_push_styles(dataset=dataset)

    def _semantic_after_traversal(self, dataset, element_content=None):
        self._semantic_postprocess_timing(dataset=dataset, element_content=element_content)
        self._semantic_unset_region(dataset=dataset)

    def _semantic_before_copy(self, dataset, element_content=None):
        self._assert_in_segment(dataset=dataset, element_content=element_content)

    def is_empty(self):
        if len(self.div):
            return False

        if len(self.p):
            return False

        return True

    def _semantic_after_subtree_copy(self, copied_instance, dataset, element_content=None):
        copied_instance._assert_empty_container()
        self._semantic_copy_apply_leaf_timing(
            copied_instance=copied_instance, dataset=dataset, element_content=element_content)
        self._semantic_copy_verify_referenced_styles(dataset=dataset)
        self._semantic_copy_verify_referenced_region(dataset=dataset)


raw.div_type._SetSupersedingClass(div_type)


class body_type(StyledElementMixin, BodyTimingValidationMixin, SemanticValidationMixin, raw.body_type):

    _attr_en_pre = {
        (pyxb.namespace.ExpandedName(None, 'begin')).uriTuple(): BodyTimingValidationMixin._pre_timing_set_attribute,
        (pyxb.namespace.ExpandedName(None, 'dur')).uriTuple(): BodyTimingValidationMixin._pre_timing_set_attribute,
        (pyxb.namespace.ExpandedName(None, 'end')).uriTuple(): BodyTimingValidationMixin._pre_timing_set_attribute
    }

    def _semantic_copy(self, dataset):
        copied_body = body_type(
            agent = self.agent,
            role = self.role,
            begin=self.begin,
            dur=self.dur,
            end=self.end,
            style=self._semantic_deconflicted_ids(attr_name='style', dataset=dataset),
            _strict_keywords=False
        )
        return copied_body

    def __copy__(self):
        copied_body = body_type(
            agent=self.agent,
            role=self.role,
            begin=self.begin,
            dur=self.dur,
            end=self.end,
            style=self.style,
            _strict_keywords=False
        )
        return copied_body

    @classmethod
    def _merge_deconflict_ids(cls, element, dest, ids):
        """
        Deconflict ids of body elements
        :param element:
        :return:
        """

        children = element.orderedContent()
        
        output = []

        for item in children:
            log.debug('processing child: {} of {}'.format(item.value, element))
            if isinstance(item, NonElementContent):
                copied_stuff = copy.copy(item.value)
                output.append(copied_stuff)
            elif isinstance(item, ElementContent):
                copied_elem = copy.copy(item.value)
                copied_elem._resetContent()
                cls._merge_deconflict_ids(item.value, copied_elem, ids)
                if isinstance(copied_elem, IDMixin):
                    if copied_elem.id is not None and copied_elem.id in ids:
                        next_try = copied_elem.id
                        while next_try in ids:
                            next_try = '{}.1'.format(next_try)
                        copied_elem.id = next_try
                    ids.add(copied_elem.id)
                output.append(copied_elem)

        for item in output:
            dest.append(item)

        return dest

    def merge(self, other_elem, dataset=None):
        # TODO: Sort out timing and styling merging rules
        merged_body = copy.copy(self)
        merged_body.begin = None
        merged_body.dur = None
        merged_body.end = None
        # The same recursive ID collision issue... DAMN!
        ids = dataset['ids']

        self._merge_deconflict_ids(element=self, dest=merged_body, ids=ids)
        self._merge_deconflict_ids(element=other_elem, dest=merged_body, ids=ids)

        return merged_body

    def _semantic_before_traversal(self, dataset, element_content=None):
        self._semantic_timebase_validation(dataset=dataset, element_content=element_content)
        self._semantic_preprocess_timing(dataset=dataset, element_content=element_content)
        self._semantic_collect_applicable_styles(dataset=dataset, style_type=style_type)
        self._semantic_push_styles(dataset=dataset)

    def _semantic_after_traversal(self, dataset, element_content=None):
        self._semantic_postprocess_timing(dataset=dataset, element_content=element_content)
        self._semantic_pop_styles(dataset=dataset)

    def _semantic_before_copy(self, dataset, element_content=None):
        self._assert_in_segment(dataset=dataset, element_content=element_content)

    def _semantic_after_subtree_copy(self, copied_instance, dataset, element_content=None):
        self._semantic_copy_apply_leaf_timing(
            copied_instance=copied_instance, dataset=dataset, element_content=element_content)
        self._semantic_copy_verify_referenced_styles(dataset=dataset)


raw.body_type._SetSupersedingClass(body_type)


class style_type(StyledElementMixin, IDMixin, SizingValidationMixin, SemanticValidationMixin, raw.style):

    # This helps us detecting infinite loops.
    _styling_lock = None
    # ordered styles cached
    _ordered_styles = None

    def __repr__(self):
        return u'<style ID: {id} at {addr}>'.format(
            id=self.id,
            addr=hex(id(self))
        )

    def _semantic_copy(self, dataset):
        copied_style = style_type(
            id=self.id,
            style=self.style,  # there is no ordering requirement in styling so too soon to deconflict here
            direction=self.direction,
            fontFamily=self.fontFamily,
            fontSize=self.fontSize,
            lineHeight=self.lineHeight,
            textAlign=self.textAlign,
            color=self.color,
            backgroundColor=self.backgroundColor,
            fontStyle=self.fontStyle,
            fontWeight=self.fontWeight,
            textDecoration=self.textDecoration,
            unicodeBidi=self.unicodeBidi,
            wrapOption=self.wrapOption,
            padding=self.padding,
            linePadding=self.linePadding,
            _strict_keywords=False
        )
        return copied_style

    @property
    def validated_styles(self):
        # The style element itself is not meant to implement this.
        raise NotImplementedError()

    def ordered_styles(self, dataset):
        """
        This function figures out the chain of styles.
        WARNING: Do not call this before the semantic validation of tt/head/styling is finished. Otherwise your style
        may not have been found yet!
        :param dataset: Semantic dataset
        :return: a list of styles applicable in order
        """

        if self._styling_lock.locked():
            raise SemanticValidationError(ERR_SEMANTIC_STYLE_CIRCLE.format(
                style=self.id
            ))

        with self._styling_lock:
            if self._ordered_styles is not None:
                return self._ordered_styles
            ordered_styles = [self]
            if self.style is not None:
                for style_id in self.style:
                    try:
                        style_elem = dataset['tt_element'].get_element_by_id(elem_id=style_id, elem_type=style_type)
                        cascading_styles = style_elem.ordered_styles(dataset=dataset)
                        for style_elem in cascading_styles:
                            if style_elem in ordered_styles:
                                continue
                            ordered_styles.append(style_elem)
                    except LookupError:
                        raise SemanticValidationError(ERR_SEMANTIC_STYLE_MISSING.format(
                            style=style_id
                        ))

            self._ordered_styles = ordered_styles
            return ordered_styles

    @classmethod
    def calculate_effective_style(cls, referenced_styles, inherited_styles, region_styles):
        """
        This function holds the styling semantics of containers considering direct reference, inheritance and
        containment variables
        :param referenced_styles: Directly referenced resolved styles
        :param inherited_styles: Inherited styling information from parent container
        :param region_styles: Default region styling information
        :return:
        """
        return cls()

    def _semantic_before_traversal(self, dataset, element_content=None):
        self._semantic_register_id(dataset=dataset)
        self._semantic_check_sizing_type(self.fontSize, dataset=dataset)
        self._semantic_check_sizing_type(self.lineHeight, dataset=dataset)
        # Init recursion loop detection lock
        self._styling_lock = threading.Lock()
        self._ordered_styles = None

    def _semantic_before_copy(self, dataset, element_content=None):
        if self not in dataset['affected_elements']:
            raise OutsideSegmentError()


raw.style._SetSupersedingClass(style_type)


class styling(SemanticValidationMixin, raw.styling):

    def __copy__(self):
        copied_styling = styling()
        return copied_styling

    def merge(self, other_elem, dataset):
        style_ids = dataset['ids']
        for item in self.orderedContent():
            style_ids.add(item.value.id)
        if other_elem:
            for item in other_elem.orderedContent():
                copied_style = copy.copy(item.value)
                if item.value.id in style_ids:
                    copied_style.id = '{}.1'.format(copied_style.id)
                self.append(copied_style)

        return self

    def _semantic_after_subtree_copy(self, copied_instance, dataset, element_content=None):
        # The styles are not ordered by inheritance so they need an extra step here
        # to get their style ID resolutions sorted
        for style_elem in \
                [
                    item.value
                    for item in self.orderedContent()
                    if isinstance(item, ElementContent) and isinstance(item.value, style_type)
                ]:
            style_elem_styles = style_elem._semantic_deconflicted_ids(attr_name='style', dataset=dataset)
            if style_elem_styles:
                style_elem.style = style_elem_styles


raw.styling._SetSupersedingClass(styling)


class region_type(IDMixin, StyledElementMixin, SizingValidationMixin, SemanticValidationMixin, raw.region):

    def _semantic_copy(self, dataset):
        copied_region = region_type(
            id=self.id,
            origin=self.origin,
            extent=self.extent,
            style=self._semantic_deconflicted_ids(attr_name='style', dataset=dataset),
            displayAlign=self.displayAlign,
            padding=self.padding,
            writingMode=self.writingMode,
            showBackground=self.showBackground,
            overflow=self.overflow
        )

        return copied_region

    def _semantic_before_traversal(self, dataset, element_content=None):
        self._semantic_register_id(dataset=dataset)
        self._semantic_check_sizing_type(self.origin, dataset=dataset)
        self._semantic_check_sizing_type(self.extent, dataset=dataset)
        self._semantic_collect_applicable_styles(dataset=dataset, style_type=style_type)

    def _semantic_before_copy(self, dataset, element_content=None):
        if self not in dataset['affected_elements']:
            raise OutsideSegmentError()


raw.region._SetSupersedingClass(region_type)


class layout(SemanticValidationMixin, raw.layout):

    def __copy__(self):
        copied_layout = layout()
        return copied_layout

    def merge(self, other_elem, dataset):
        region_ids = dataset['ids']
        for item in self.orderedContent():
            region_ids.add(item.value.id)
        if other_elem:
            for item in other_elem.orderedContent():
                copied_region = copy.copy(item.value)
                if copied_region.id in region_ids:
                    copied_region.id = '{}.1'.format(copied_region.id)
                    region_ids.add(copied_region.id)
                self.append(copied_region)
        return self


raw.layout._SetSupersedingClass(layout)

# EBU TT D classes
# ================

class d_tt_type(raw.d_tt_type):

    @classmethod
    def __check_bds(cls, bds):
        if bds:
            return bds
        else:
            return BindingDOMSupport(
                namespace_prefix_map=namespace_prefix_map
            )

    def toDOM(self, bds=None, parent=None, element_name=None):
        xml_dom = super(d_tt_type, self).toDOM(
            bds=self.__check_bds(bds),
            parent=parent,
            element_name=element_name
        )
        xml_dom.documentElement.tagName = 'tt:tt'
        return xml_dom

    def toxml(self, encoding=None, bds=None, root_only=False, element_name=None):
        dom = self.toDOM(self.__check_bds(bds), element_name=element_name)
        if root_only:
            dom = dom.documentElement
        return dom.toprettyxml(
            encoding=encoding,
            indent='  '
        )

    def _validateBinding_vx(self):
        if self.timeBase != 'media':
            raise SimpleTypeValueError(type(self.timeBase), self.timeBase)

        super(d_tt_type, self)._validateBinding_vx()


raw.d_tt_type._SetSupersedingClass(d_tt_type)


class d_layout_type(raw.d_layout_type):

    @classmethod
    def create_default_value(cls):
        instance = cls(
            d_region_type.create_default_value()
        )
        return instance

raw.d_layout_type._SetSupersedingClass(d_layout_type)


class d_region_type(raw.d_region_type):

    @classmethod
    def create_default_value(cls):
        instance = cls(
            id='region.default',
            origin='0% 0%',
            extent='100% 100%'
        )
        return instance

raw.d_region_type._SetSupersedingClass(d_region_type)


class d_styling_type(raw.d_styling_type):

    @classmethod
    def create_default_value(cls):
        instance = cls(
            d_style_type.create_default_value()
        )
        return instance

raw.d_styling_type._SetSupersedingClass(d_styling_type)


class d_style_type(raw.d_style_type):

    @classmethod
    def create_default_value(cls):
        instance = cls(
            id='style.default'
        )
        return instance

raw.d_style_type._SetSupersedingClass(d_style_type)
