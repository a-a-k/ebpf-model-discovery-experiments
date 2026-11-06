'use strict';

// Diagnostic observer only. No span, provider, propagator or header is written.
const fs = require('node:fs');
const http2 = require('node:http2');
const crypto = require('node:crypto');
const path = require('node:path');
const allowed = new Set(['traceparent', 'tracestate', 'baggage',
  'x-experiment-request-id', ':method', ':path', ':authority', 'content-type']);

function spanValue(span) {
  if (!span) return {present: false, spanContext: null, isRecording: null};
  try {
    const c = span.spanContext();
    return {present: true, spanContext: {traceId: c.traceId, spanId: c.spanId,
      traceFlags: c.traceFlags, isRemote: c.isRemote === undefined ? null : c.isRemote,
      traceState: c.traceState ? c.traceState.serialize() : null},
    isRecording: span.isRecording()};
  } catch (error) {
    return {present: true, spanContext: null, isRecording: null, readError: String(error)};
  }
}

function headerPairs(headers) {
  const values = Array.isArray(headers) ? Array.from({length: headers.length / 2},
    (_, i) => [headers[2*i], headers[2*i+1]]) : Object.entries(headers || {});
  return values.filter(([name]) => allowed.has(String(name).toLowerCase()))
    .map(([name, value]) => [name, Array.isArray(value) ? value.slice() : value]);
}

function httpModule() {
  try {
    const entry = require.resolve('@opentelemetry/instrumentation-http');
    let directory = path.dirname(entry);
    while (directory !== path.dirname(directory)) {
      const candidate = path.join(directory, 'package.json');
      if (fs.existsSync(candidate)) {
        const data = fs.readFileSync(candidate);
        const pkg = JSON.parse(data);
        if (pkg.name === '@opentelemetry/instrumentation-http') return {
          name: pkg.name, version: pkg.version, packagePath: candidate,
          packageSha256: crypto.createHash('sha256').update(data).digest('hex')};
      }
      directory = path.dirname(directory);
    }
    return {readError: 'resolved HTTP package manifest not found'};
  } catch (error) { return {readError: String(error)}; }
}

function createObserver(api, sink, h2 = http2, moduleReceipt = httpModule) {
  let sequence = 0, sessionSequence = 0, dispatchSequence = 0, installed = false;
  const instanceId = crypto.randomUUID();
  function emit(value) {
    try {
      sink(JSON.stringify({schema: 'context-witness-v6', pid: process.pid, instanceId,
        wallNs: (BigInt(Date.now()) * 1000000n).toString(),
        monotonicNs: process.hrtime.bigint().toString(), sequence: ++sequence, ...value}) + '\n');
    } catch (error) {
      // Reporting failure cannot replace application behavior or create a span.
      process.stderr.write('CONTEXT_WITNESS_V6_WRITE_FAILED ' + String(error) + '\n');
    }
  }
  function active() {
    try { return spanValue(api.trace.getSpan(api.context.active())); }
    catch (error) { return {present: null, spanContext: null, isRecording: null, readError: String(error)}; }
  }
  function readHeaders(value) {
    try { return headerPairs(value); }
    catch (error) { return {readError: String(error)}; }
  }
  function httpRequestHook(span, request) {
    try {
      emit({kind: 'http-request-hook', point: 'pinned HTTP instrumentation requestHook',
        requestType: request.constructor ? request.constructor.name : null,
        method: request.method || null, url: request.url || request.path || null,
        headers: readHeaders(request.rawHeaders || (request.getHeaders ? request.getHeaders() : request.headers)),
        passedSpan: spanValue(span), activeSpan: active(), headerScope: 'selected literal Node API values; not wire proof'});
    } catch (error) { emit({kind: 'http-request-hook-read-error', readError: String(error)}); }
  }
  function withHttpHook(options) {
    const old = options['@opentelemetry/instrumentation-http'] || {};
    const prior = old.requestHook;
    return {...options, '@opentelemetry/instrumentation-http': {...old,
      requestHook: function(...args) {
        const value = typeof prior === 'function' ? Reflect.apply(prior, this, args) : undefined;
        httpRequestHook(...args);
        return value;
      }}};
  }
  function installHttp2() {
    if (installed) throw new Error('context witness must be installed once');
    installed = true;
    const connect = h2.connect;
    h2.connect = function(...connectArgs) {
      const session = Reflect.apply(connect, this, connectArgs);
      const sessionId = ++sessionSequence;
      const request = session.request;
      session.on('connect', () => {
        let socket = {};
        try { const s = session.socket; socket = {localAddress: s.localAddress,
          localPort: s.localPort, remoteAddress: s.remoteAddress, remotePort: s.remotePort}; } catch (_) {}
        emit({kind: 'http2-session-connect', sessionId, socket});
      });
      session.request = function(...requestArgs) {
        const dispatchId = ++dispatchSequence;
        emit({kind: 'http2-dispatch', sessionId, dispatchId,
          point: 'session.request arguments before original method',
          headers: readHeaders(requestArgs[0]), activeSpan: active(),
          headersMutatedByObserver: false, headerScope: 'API arguments; wire evidence is independent'});
        const stream = Reflect.apply(request, this, requestArgs);
        const streamId = () => emit({kind: 'http2-stream-id', sessionId, dispatchId, streamId: stream.id});
        if (stream.id === undefined) stream.once('ready', streamId); else streamId();
        return stream;
      };
      return session;
    };
    emit({kind: 'observer-installed', sdkProviderInstalledByObserver: false,
      propagatorInstalledByObserver: false, spansCreatedByObserver: false,
      observerSha256: crypto.createHash('sha256').update(fs.readFileSync(__filename)).digest('hex'),
      nodeVersion: process.version, httpInstrumentation: moduleReceipt()});
  }
  return {httpRequestHook, withHttpHook, installHttp2};
}

let singleton;
function instance() {
  if (!singleton) {
    const path = process.env.CONTEXT_WITNESS_V6_OUT;
    if (!path) throw new Error('diagnostic witness output must be explicit');
    singleton = createObserver(require('@opentelemetry/api'), line => fs.appendFileSync(path, line));
  }
  return singleton;
}
module.exports = {createObserver, spanValue, headerPairs,
  withHttpHook: options => instance().withHttpHook(options),
  installHttp2: () => instance().installHttp2()};
