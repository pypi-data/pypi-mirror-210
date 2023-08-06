# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.
import pathlib
from collections import ChainMap
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from leaf_focus import utils


# TODO
# @given(value=st.datetimes())
# def test_fuzz_parse_date(value):
#     value_str = value.strftime("%a %b %d %H:%M:%S %Y")
#     assert utils.parse_date(value=value_str)


@given(name=st.text(), value=st.text(), expected=st.builds(list))
def test_fuzz_validate(name, value, expected):
    if value not in expected:
        with pytest.raises(utils.LeafFocusError):
            utils.validate(name=name, value=value, expected=expected)
    else:
        utils.validate(name=name, value=value, expected=expected)


@given(name=st.text(), value=st.builds(pathlib.Path), must_exist=st.booleans())
def test_fuzz_validate_path(name, value, must_exist):
    assert utils.validate_path(name=name, value=value, must_exist=must_exist)


@given(
    input_file=st.builds(Path),
    output_type=st.text(),
    output_path=st.builds(Path),
    additional=st.one_of(
        st.none(),
        st.lists(st.text()),
        st.sets(st.text()),
        st.frozensets(st.text()),
        st.dictionaries(keys=st.text(), values=st.text()),
        st.dictionaries(keys=st.text(), values=st.none()).map(dict.keys),
        st.dictionaries(keys=st.integers(), values=st.text()).map(dict.values),
        st.dictionaries(keys=st.text(), values=st.text()).map(ChainMap),
    ),
)
def test_fuzz_output_root(input_file, output_type, output_path, additional):
    assert utils.output_root(
        input_file=input_file,
        output_type=output_type,
        output_path=output_path,
        additional=additional,
    )


# TODO
# @given(element=st.builds(ET))
# def test_fuzz_xml_to_element(element):
#     utils.xml_to_element(element=element)


@given(value=st.text())
def test_fuzz_xml_tag_ns(value):
    name_space, name = utils.xml_tag_ns(value=value)
    assert name_space is not None
    assert name is not None
