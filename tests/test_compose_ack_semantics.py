"""Document the historical ACK oracle using exact pinned application Lua.

Only Thrift transport/objects and nginx/tracing infrastructure are mocked.
This does not establish which branch any particular experimental request took.
"""
import hashlib
import json
from pathlib import Path

import pytest
from lupa import LuaRuntime


FIXTURE = Path(__file__).parent / "fixtures" / "deathstarbench-compose"


@pytest.mark.parametrize("reply,status,ack,decoded", [
    ("success", 200, True, False),
    ("service_exception", 200, True, True),
    ("application_exception", 500, False, False),
    ("transport_failure", 500, False, False),
])
def test_exact_pinned_compose_http_outcome(reply, status, ack, decoded):
    source = json.loads((FIXTURE / "SOURCE.json").read_text())
    for entry in source["files"]:
        body = (FIXTURE / entry["file"]).read_bytes()
        assert len(body) == entry["bytes"]
        assert hashlib.sha256(body).hexdigest() == entry["sha256"]
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.globals().reply_kind = reply
    lua.execute(r'''
        local Object = {}
        function Object:new(fields)
            return setmetatable(fields or {}, {__index=self})
        end
        local ServiceException = Object:new()
        function ServiceException:read(protocol)
            self.message = "MongoDB update failed"
            service_exception_decoded = true
        end
        local ApplicationException = Object:new()
        function ApplicationException:read(protocol)
            self.message = "application error"
        end
        package.loaded.Thrift = {
            TType={STOP=0, STRUCT=12, I64=10, I32=8, STRING=11, LIST=15, MAP=13},
            TMessageType={CALL=1, REPLY=2, EXCEPTION=3},
            __TObject=Object, __TClient=Object:new(), __TProcessor=Object:new(),
            TApplicationException=ApplicationException, ttype=type,
            ttable_size=function(t) local n=0; for _ in pairs(t) do n=n+1 end; return n end
        }
        package.loaded.social_network_ttypes = {ServiceException=ServiceException}
        local noop = function() end
        local trans = {flush=noop, close=function() transport_closed=true end}
        protocol = setmetatable({trans=trans}, {__index=function() return noop end})
        function protocol:readMessageBegin()
            if reply_kind == "transport_failure" then error("connection lost") end
            return "ComposePost", reply_kind == "application_exception" and 3 or 2, 0
        end
        function protocol:readFieldBegin()
            if reply_kind == "service_exception" and not rawget(self, "field_read") then
                self.field_read=true; return "se", 12, 1
            end
            return "", 0, 0
        end
        package.loaded.cjson = {decode=function() return {} end}
        local span = {context=function() return {} end, finish=noop}
        local tracer = {binary_extract=noop, start_span=function() return span end,
                        text_map_inject=noop}
        package.loaded.opentracing_bridge_tracer = {new_from_global=function() return tracer end}
        package.loaded.GenericObjectPool = {
            setMaxTotal=noop, returnConnection=noop,
            connection=function(_, client_class)
                return client_class:new{iprot=protocol, oprot=protocol, _seqid=0}
            end
        }
        body = ""; service_exception_decoded=false
        exit_signal = {}
        ngx = {
            var={request_id="123456789abcdef", opentracing_binary_context=""},
            req={read_body=noop, get_post_args=function()
                return {user_id="1", username="user", post_type="0", text="post"}
            end},
            HTTP_BAD_REQUEST=400, HTTP_OK=200, HTTP_INTERNAL_SERVER_ERROR=500, ERR=3,
            say=function(s) body=body..s end, log=noop,
            exit=function(code) error(exit_signal) end
        }
        real_pcall = pcall
        pcall = function(...)
            local ok, value = real_pcall(...)
            rpc_ok = ok
            return ok, value
        end
    ''')
    lua.globals().package.loaded.social_network_ComposePostService = lua.execute(
        (FIXTURE / "client.lua").read_bytes())
    handler = lua.execute((FIXTURE / "handler.lua").read_bytes())
    ok, signal = lua.globals().real_pcall(handler.ComposePost)
    assert not ok
    assert lua.eval("function(value) return value == exit_signal end")(signal)
    assert lua.globals().ngx.status == status
    assert ("Successfully upload post" in lua.globals().body) is ack
    assert bool(lua.globals().rpc_ok) is ack
    assert bool(lua.globals().service_exception_decoded) is decoded
