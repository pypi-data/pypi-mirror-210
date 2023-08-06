import pytest

from aiobtclientrpc import _errors


@pytest.mark.parametrize(
    argnames='a, b, exp_equal',
    argvalues=(
        (_errors.Error('foo'), _errors.Error('foo'), True),
        (_errors.Error('foo'), _errors.Error('bar'), False),
        (_errors.Error('foo'), _errors.RPCError('foo'), True),
        (_errors.Error('foo'), _errors.RPCError('bar'), False),
        (_errors.Error('foo'), ValueError('foo'), NotImplemented),
        (_errors.Error('foo'), ValueError('bar'), NotImplemented),
    ),
    ids=lambda v: repr(v),
)
def test_Error_equality(a, b, exp_equal):
    equal = a.__eq__(b)
    assert equal is exp_equal


@pytest.mark.parametrize(
    argnames='msg, info, exp_repr',
    argvalues=(
        ('foo', None, "RPCError('foo', info=None)"),
        ('foo', 'more info', "RPCError('foo', info='more info')"),
        ('foo', {'arbitrary': 'object'}, "RPCError('foo', info={'arbitrary': 'object'})"),
    ),
    ids=lambda v: repr(v),
)
def test_RPCError(msg, info, exp_repr):
    if info is not None:
        exception = _errors.RPCError(msg, info=info)
    else:
        exception = _errors.RPCError(msg)
    assert repr(exception) == exp_repr


@pytest.mark.parametrize(
    argnames='a, b, exp_equal',
    argvalues=(
        (_errors.RPCError('foo'), _errors.RPCError('foo'), True),
        (_errors.RPCError('foo'), _errors.RPCError('bar'), False),
        (_errors.RPCError('foo', info='my info'), _errors.RPCError('foo', info='my info'), True),
        (_errors.RPCError('foo', info='my info'), _errors.RPCError('foo', info='your info'), False),
        (_errors.RPCError('foo'), _errors.Error('foo'), NotImplemented),
        (_errors.RPCError('foo'), _errors.Error('bar'), NotImplemented),
    ),
    ids=lambda v: repr(v),
)
def test_RPCError_equality(a, b, exp_equal):
    equal = a.__eq__(b)
    assert equal is exp_equal


rpc_exception_map = {
    r'^The environment is perfectly safe$': ValueError(r'RUN FOR YOUR LIVES!'),
    r'^The (\w+) fell (\w+)$': (ValueError, r'\1: I fell \2!'),
    r'^A (?P<what>\w+) hit the (?P<who>\w+)$': (ValueError, r'\g<who>: I was hit by a \g<what>!'),
    r'\{([^\}]*?)\}': (ValueError, r'<\1>'),
}

@pytest.mark.parametrize(
    argnames='rpc_error, exp_return_value',
    argvalues=(
        (_errors.RPCError('The environment is perfectly safe'), ValueError(r'RUN FOR YOUR LIVES!')),
        (_errors.RPCError('The environment is toppled over'), _errors.RPCError('The environment is toppled over')),

        (_errors.RPCError('The front fell off'), ValueError(r'front: I fell off!')),
        (_errors.RPCError('The bottom fell off'), ValueError(r'bottom: I fell off!')),
        (_errors.RPCError('The front escalated quickly'), _errors.RPCError('The front escalated quickly')),

        (_errors.RPCError('A wave hit the ship'), ValueError(r'ship: I was hit by a wave!')),
        (_errors.RPCError('A whale hit the blimp'), ValueError(r'blimp: I was hit by a whale!')),
        (_errors.RPCError('A whale punched the blimp'), _errors.RPCError('A whale punched the blimp')),

        (_errors.RPCError('Some {text with} braces'), ValueError(r'<text with>')),
        (_errors.RPCError('Some {text} with {braces}'), ValueError(r'<text>')),
    ),
    ids=lambda v: repr(v),
)
def test_RPCError_translate_finds_matching_exception_with_backreferences(rpc_error, exp_return_value):
    return_value = rpc_error.translate(rpc_exception_map)
    assert type(return_value) is type(exp_return_value)
    assert str(return_value) == str(exp_return_value)
