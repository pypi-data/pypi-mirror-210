"""
Name : gm_assert_utils.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2023-05-20 16:46
Desc: 验证assert封装
"""
import pytest

EQUALTYPENOTICE = "两个值不相等，注意类型是否一致！！！"
NOTEQUALTYPENOTICE = "两个值相等，注意类型是否一致！！！"
INCLUDENOTICE = "第一个值不在第二个值内，请检查！"
NOINCLUDENOTICE = "第一个值在第二个值内，请检查！"
CODENOTICE = "请求期望CODE与返回CODE不一致，请检查！"

def gm_assert_equal(first_value, second_value, types):
    """验证是否相等"""
    try:
        first = _convert_type(first_value, to_type=types)
        second = _convert_type(second_value, to_type=types)
        assert first == second, EQUALTYPENOTICE
    except AssertionError as e:
        raise AssertionError(e)

def gm_assert_in(first_value, second_value, types):
    """验证第一个值包含在第二个值内"""
    try:
        first = _convert_type(first_value, to_type=types)
        second = _convert_type(second_value, to_type=types)
        assert first in second, INCLUDENOTICE
    except AssertionError as e:
        raise AssertionError(e)

def gm_assert_not_in(first_value, second_value, types):
    """验证第一个值不包含在第二个值内"""
    try:
        first = _convert_type(first_value, to_type=types)
        second = _convert_type(second_value, to_type=types)
        assert first not in second, NOINCLUDENOTICE
    except AssertionError as e:
        raise AssertionError(e)

def gm_assert_not_equal(first_value, second_value, types):
    """验证不相等"""
    try:
        first = _convert_type(first_value, to_type=types)
        second = _convert_type(second_value, to_type=types)
        assert first != second, NOTEQUALTYPENOTICE
    except AssertionError as e:
        raise AssertionError(e)

def gm_assert_response_code(first_value, second_value, types):
    """验证response的code值"""
    try:
        first = _convert_type(first_value, to_type=types)
        second = _convert_type(second_value, to_type=types)
        assert first == second, CODENOTICE
    except AssertionError as e:
        raise AssertionError(e)

def gm_assert_multiple_values_equal(values, types):
    """多数据验证相等"""
    assert len(values) > 1, "At least two values are needed"
    for i in range(1, len(values)):
        values[i] = _convert_type(values[i], to_type=types)
        assert values[i] == values[0], f"Value {values[i]} does not equal {values[0]}"

def _convert_type(value, to_type=str, default=None):
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default


if __name__ == '__main__':
    gm_assert_equal(2, '2', int)  # 将第1和第2个参数转换成int型比较
    gm_assert_multiple_values_equal([3, 3, '3'], int)
    gm_assert_not_in("hello", "hello world", str)
