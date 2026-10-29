from pathlib import Path

import pytest

from .adapter_v5 import Adapter


def _adapter(tmp_path: Path, mode: str = "absent") -> Adapter:
    context = type(
        "Context",
        (),
        {
            "mode": mode,
            "deployment_dir": tmp_path,
            "node_ip": lambda self, node: "192.0.2.10" if node == "a" else "192.0.2.11",
        },
    )()
    adapter = Adapter(context)
    adapter.source.mkdir(parents=True)
    return adapter


def test_checkout_disabled_path_uses_only_global_noop_tracer(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path)
    path = adapter.source / "src/checkout/main.go"
    path.parent.mkdir(parents=True)
    path.write_text(
        """func initTracerProvider() *sdktrace.TracerProvider {
\tif telemetrySDKDisabled() {
\t\ttp := sdktrace.NewTracerProvider(sdktrace.WithSampler(sdktrace.NeverSample()))
\t\totel.SetTracerProvider(tp)
\t\totel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(propagation.TraceContext{}, propagation.Baggage{}))
\t\treturn tp
\t}
\tctx := context.Background()
\t_ = ctx
\ttp := sdktrace.NewTracerProvider()
\totel.SetTracerProvider(tp)
\totel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(propagation.TraceContext{}, propagation.Baggage{}))
\treturn tp
}
func main() {
\ttp := initTracerProvider()
\tdefer func() {
\t\tif err := tp.Shutdown(context.Background()); err != nil {
\t\t\tlogger.Error(fmt.Sprintf("Error shutting down tracer provider: %v", err))
\t\t}
\t}()
\ttracer = tp.Tracer("checkout")
}
""",
        encoding="utf-8",
    )

    adapter._patch_checkout_context_neutral()
    result = path.read_text(encoding="utf-8")
    disabled = result[result.index("if telemetrySDKDisabled()") : result.index("\tctx :=")]
    assert 'return nil, otel.Tracer("checkout")' in disabled
    assert "NewTracerProvider" not in disabled
    assert "SetTracerProvider" not in disabled
    assert "SetTextMapPropagator" not in disabled
    assert "NeverSample" not in result
    assert "tp, checkoutTracer := initTracerProvider()" in result
    assert "if tp != nil" in result
    assert "tracer = checkoutTracer" in result
    # Native-enabled code retains its exporter/provider/propagator behavior.
    assert result.count("otel.SetTracerProvider(tp)") == 1
    assert result.count("otel.SetTextMapPropagator(") == 1


def test_currency_disabled_path_returns_before_sdk_or_propagator(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path)
    tracer = adapter.source / "src/currency/src/tracer_common.h"
    server = adapter.source / "src/currency/src/server.cpp"
    tracer.parent.mkdir(parents=True)
    tracer.write_text(
        """#include "opentelemetry/sdk/resource/resource.h"
#include "opentelemetry/sdk/trace/samplers/always_off.h"
std::shared_ptr<opentelemetry::sdk::trace::TracerProvider> initTracer()
{
  std::vector<std::unique_ptr<opentelemetry::sdk::trace::SpanProcessor>> processors;
  const char *sdk_disabled = std::getenv("OTEL_SDK_DISABLED");
  if (sdk_disabled == nullptr || std::strcmp(sdk_disabled, "true") != 0)
  {
    auto exporter = opentelemetry::exporter::otlp::OtlpGrpcExporterFactory::Create();
    auto processor =
        opentelemetry::sdk::trace::BatchSpanProcessorFactory::Create(std::move(exporter), {});
    processors.push_back(std::move(processor));
  }

  std::unique_ptr<opentelemetry::sdk::trace::TracerContext> context;
  if (sdk_disabled != nullptr && std::strcmp(sdk_disabled, "true") == 0)
  {
    context = opentelemetry::sdk::trace::TracerContextFactory::Create(
        std::move(processors),
        opentelemetry::sdk::resource::Resource::GetDefault(),
        std::unique_ptr<opentelemetry::sdk::trace::Sampler>(
            new opentelemetry::sdk::trace::AlwaysOffSampler));
  }
  else
  {
    context = opentelemetry::sdk::trace::TracerContextFactory::Create(std::move(processors));
  }
  std::shared_ptr<opentelemetry::sdk::trace::TracerProvider> provider = make(context);
  opentelemetry::trace::Provider::SetTracerProvider(provider);
  SetGlobalPropagator(HttpTraceContext());
  return provider;
}
""",
        encoding="utf-8",
    )
    server.write_text(
        """  const bool tracer_shutdown =
      tracer_provider->Shutdown(remainingShutdownTimeout(server_shutdown.deadline));
  if (!tracer_shutdown) {
    std::cerr << "Tracer provider shutdown failed\\n";
  }
""",
        encoding="utf-8",
    )

    adapter._patch_currency_context_neutral()
    result = tracer.read_text(encoding="utf-8")
    disabled_end = result.index("  auto exporter")
    disabled = result[:disabled_end]
    assert "return nullptr" in disabled
    assert "TracerContextFactory" not in disabled
    assert "SetTracerProvider" not in disabled
    assert "SetGlobalPropagator" not in disabled
    assert "AlwaysOff" not in result
    assert "if (tracer_provider != nullptr)" in server.read_text(encoding="utf-8")


def test_shipping_disabled_path_returns_before_sdk_or_propagator(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path)
    path = adapter.source / "src/shipping/src/telemetry_conf.rs"
    path.parent.mkdir(parents=True)
    path.write_text(
        """use opentelemetry_sdk::trace::{Sampler, SdkTracerProvider};
fn init_tracer_provider() -> SdkTracerProvider {
    global::set_text_map_propagator(TraceContextPropagator::new());

    let native_tracing_disabled =
        matches!(std::env::var("OTEL_SDK_DISABLED").as_deref(), Ok("true"));
    let tracer_provider = if native_tracing_disabled {
        SdkTracerProvider::builder()
            .with_resource(get_resource())
            .with_sampler(Sampler::AlwaysOff)
            .build()
    } else {
        SdkTracerProvider::builder()
            .with_resource(get_resource())
            .with_batch_exporter(
                opentelemetry_otlp::SpanExporter::builder()
                    .with_http()
                    .with_protocol(Protocol::HttpBinary)
                    .build()
                    .expect("Failed to initialize tracing provider"),
            )
            .build()
    };

    global::set_tracer_provider(tracer_provider.clone());
    tracer_provider
}
pub struct OtelGuard {
    tracer_provider: SdkTracerProvider,
}
impl OtelGuard {
    pub fn shutdown(self) {
        if let Err(e) = self.tracer_provider.shutdown() {
            eprintln!("Failed to shutdown TracerProvider: {e}");
        }
    }
}
""",
        encoding="utf-8",
    )

    adapter._patch_shipping_context_neutral()
    result = path.read_text(encoding="utf-8")
    disabled_end = result.index("    global::set_text_map_propagator")
    disabled = result[:disabled_end]
    assert "return None" in disabled
    assert "SdkTracerProvider::builder" not in disabled
    assert "set_tracer_provider" not in disabled
    assert "TraceContextPropagator::new" not in disabled
    assert "AlwaysOff" not in result
    assert "tracer_provider: Option<SdkTracerProvider>" in result
    assert "if let Some(tracer_provider)" in result
    # The native-enabled branch still installs the original exporter and context.
    assert "with_batch_exporter" in result
    assert "global::set_text_map_propagator(TraceContextPropagator::new())" in result


@pytest.mark.parametrize(
    ("mode", "disabled"),
    [
        ("absent", ["all application components"]),
        ("partial", ["product-catalog-a", "product-catalog-b"]),
        ("full", []),
    ],
)
def test_v5_mode_audit_is_explicit_without_renaming_v4(
    tmp_path: Path, mode: str, disabled: list[str]
) -> None:
    adapter = _adapter(tmp_path, mode)
    audit = adapter.native_mode_audit_spec()
    assert audit["schema"] == "otel-demo-native-mode-audit-v5"
    assert audit["experiment_protocol"] == "iteration-5"
    assert audit["disabled_trace_components"] == disabled
    assert all(value == 0 for value in audit["disabled_trace_policy"].values())
    description = adapter._suppression_description()
    assert description["experiment_protocol"] == "iteration-5"
    assert description["raw_mode_audit"] == audit
    assert "no application trace exporter" in description["mode_semantics"]
