"""Iteration-5 OTel Demo adapter with provider-neutral disabled tracing.

The v4 adapter is intentionally left executable and unchanged.  This subclass
keeps its deployment, workload, and native-enabled behavior, but makes the v5
meaning of a disabled tracing component precise: it installs no trace SDK
provider and no trace-context propagator.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .adapter import Adapter as AdapterV4


class Adapter(AdapterV4):
    """OTel Demo adapter for the iteration-5 tracing-mode semantics."""

    EXPERIMENT_PROTOCOL = "iteration-5"

    def _verify_native_file(self, path: Path) -> dict[str, Any]:
        verification = super()._verify_native_file(path)
        verification["mode_definition"] = "verified_resolved_sdk_configuration"
        verification["native_coverage_status"] = "observed"
        if self.mode == "full" and verification["mode_compliant"] is False:
            verification["mode_compliant"] = None
            verification["native_coverage_status"] = (
                "unknown_no_native_spans_observed"
                if verification["span_markers"] == 0
                else "unknown_product_catalog_unobserved"
            )
        return verification

    @staticmethod
    def _validate_native_verification(verification: dict[str, Any]) -> None:
        if verification.get("malformed_records", 0) > 0:
            raise RuntimeError(f"native trace audit input is malformed: {verification}")
        if verification.get("mode_compliant") is False:
            raise RuntimeError(f"native trace suppression check failed: {verification}")

    def native_mode_audit_spec(self) -> dict[str, Any]:
        disabled = (
            ["all application components"]
            if self.mode == "absent"
            else ["product-catalog-a", "product-catalog-b"]
            if self.mode == "partial"
            else []
        )
        return {
            "schema": "otel-demo-native-mode-audit-v5",
            "experiment_protocol": self.EXPERIMENT_PROTOCOL,
            "mode": self.mode,
            "disabled_trace_components": disabled,
            "disabled_trace_policy": {
                "application_trace_exports": 0,
                "application_sdk_trace_providers": 0,
                "application_trace_propagators": 0,
            },
            "context_scope": (
                "no claim that the process carries no trace-context object: an "
                "incoming carrier or the selected eBPF collector may provide one"
            ),
            "raw_checks": [
                "unfiltered native OTLP trace stream retained with hash",
                "service census contains no disabled component",
                "recorded source patch contains no disabled-path SDK provider or propagator",
                "resolved environment and mounted helper instrumentation match the mode",
            ],
            "classification": {
                "disabled_component_span": "technical_mode_violation",
                "audit_input_missing_or_corrupt": "technical_invalid",
                "healthy_ebpf_capture_without_application_span": "observed_unsupported_or_unknown",
            },
        }

    def _suppression_description(self) -> dict[str, Any]:
        description = super()._suppression_description()
        description.update(
            {
                "experiment_protocol": self.EXPERIMENT_PROTOCOL,
                "mode_semantics": (
                    "v5 tracing mode: disabled components install no application "
                    "trace exporter, SDK trace provider, or trace-context propagator"
                ),
                "source_guards": (
                    "checkout, currency, shipping, and product-catalog leave the "
                    "global no-op trace provider/propagator untouched when disabled; "
                    "enabled paths retain the pinned upstream provider/exporter setup"
                ),
                "propagation": (
                    "disabled components neither extract nor inject application SDK "
                    "trace context; enabled components retain their pinned propagation"
                ),
                "raw_mode_audit": self.native_mode_audit_spec(),
            }
        )
        return description

    def _patch_native_disable(self) -> dict[str, Any]:
        """Apply v4 guards, then replace context-creating disabled trace paths.

        Calling the historical implementation avoids duplicating unrelated
        exporter guards and dependency-download recording.  The resulting v5
        diff is regenerated from the pinned upstream checkout, so its manifest
        hashes the complete final source state rather than the intermediate v4
        patch.
        """
        base_record = super()._patch_native_disable()
        self._patch_checkout_context_neutral()
        self._patch_currency_context_neutral()
        self._patch_shipping_context_neutral()

        paths = [
            "src/checkout/main.go",
            "src/currency/src/server.cpp",
            "src/currency/src/tracer_common.h",
            "src/email/email_server.rb",
            "src/frontend/utils/telemetry/Instrumentation.js",
            "src/product-catalog/main.go",
            "src/shipping/src/telemetry_conf.rs",
            "src/checkout/Dockerfile",
            "src/product-catalog/Dockerfile",
        ]
        diff = self._run_stdout(
            ["git", "-C", str(self.source), "diff", "--", *paths]
        )
        required = (
            "return nil, otel.Tracer(\"checkout\")",
            "return nullptr; // v5: retain the global no-op provider and propagator",
            "return None; // v5: retain the global no-op provider and propagator",
        )
        if not diff.strip() or any(marker not in diff for marker in required):
            raise RuntimeError("v5 context-neutral native-disable patch is incomplete")

        old_patch = self.bundle / str(base_record["path"])
        if old_patch.exists():
            old_patch.unlink()
        patch_path = self.bundle / "native-disable-v5.patch"
        patch_path.write_text(diff, encoding="utf-8")
        return {
            **base_record,
            "path": patch_path.name,
            "sha256": hashlib.sha256(diff.encode("utf-8")).hexdigest(),
            "experiment_protocol": self.EXPERIMENT_PROTOCOL,
            "trace_context_policy": (
                "disabled application paths install no SDK trace provider or propagator; "
                "collector-provided or incoming context is outside this source guarantee"
            ),
            "services": sorted(set(base_record["services"]) | {"currency", "shipping"}),
        }

    def _patch_checkout_context_neutral(self) -> None:
        path = self.source / "src" / "checkout" / "main.go"
        text = path.read_text(encoding="utf-8")
        text = self._replace_once(
            text,
            "func initTracerProvider() *sdktrace.TracerProvider {\n"
            "\tif telemetrySDKDisabled() {\n"
            "\t\ttp := sdktrace.NewTracerProvider(sdktrace.WithSampler(sdktrace.NeverSample()))\n"
            "\t\totel.SetTracerProvider(tp)\n"
            "\t\totel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(propagation.TraceContext{}, propagation.Baggage{}))\n"
            "\t\treturn tp\n"
            "\t}\n",
            "func initTracerProvider() (*sdktrace.TracerProvider, trace.Tracer) {\n"
            "\tif telemetrySDKDisabled() {\n"
            "\t\treturn nil, otel.Tracer(\"checkout\")\n"
            "\t}\n",
            path,
        )
        text = self._replace_once(
            text,
            "\totel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(propagation.TraceContext{}, propagation.Baggage{}))\n"
            "\treturn tp\n}",
            "\totel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(propagation.TraceContext{}, propagation.Baggage{}))\n"
            "\treturn tp, tp.Tracer(\"checkout\")\n}",
            path,
        )
        text = self._replace_once(
            text,
            "\ttp := initTracerProvider()\n"
            "\tdefer func() {\n"
            "\t\tif err := tp.Shutdown(context.Background()); err != nil {\n"
            "\t\t\tlogger.Error(fmt.Sprintf(\"Error shutting down tracer provider: %v\", err))\n"
            "\t\t}\n"
            "\t}()",
            "\ttp, checkoutTracer := initTracerProvider()\n"
            "\tif tp != nil {\n"
            "\t\tdefer func() {\n"
            "\t\t\tif err := tp.Shutdown(context.Background()); err != nil {\n"
            "\t\t\t\tlogger.Error(fmt.Sprintf(\"Error shutting down tracer provider: %v\", err))\n"
            "\t\t\t}\n"
            "\t\t}()\n"
            "\t}",
            path,
        )
        text = self._replace_once(
            text, "\ttracer = tp.Tracer(\"checkout\")", "\ttracer = checkoutTracer", path
        )
        path.write_text(text, encoding="utf-8")

    def _patch_currency_context_neutral(self) -> None:
        tracer = self.source / "src" / "currency" / "src" / "tracer_common.h"
        text = tracer.read_text(encoding="utf-8")
        text = text.replace(
            '#include "opentelemetry/sdk/resource/resource.h"\n'
            '#include "opentelemetry/sdk/trace/samplers/always_off.h"\n',
            "",
            1,
        )
        old = """  std::vector<std::unique_ptr<opentelemetry::sdk::trace::SpanProcessor>> processors;
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
"""
        new = """  const char *sdk_disabled = std::getenv("OTEL_SDK_DISABLED");
  if (sdk_disabled != nullptr && std::strcmp(sdk_disabled, "true") == 0)
  {
    return nullptr; // v5: retain the global no-op provider and propagator
  }
  auto exporter = opentelemetry::exporter::otlp::OtlpGrpcExporterFactory::Create();
  auto processor =
      opentelemetry::sdk::trace::BatchSpanProcessorFactory::Create(std::move(exporter), {});
  std::vector<std::unique_ptr<opentelemetry::sdk::trace::SpanProcessor>> processors;
  processors.push_back(std::move(processor));
  auto context =
      opentelemetry::sdk::trace::TracerContextFactory::Create(std::move(processors));
"""
        text = self._replace_once(text, old, new, tracer)
        tracer.write_text(text, encoding="utf-8")

        server = self.source / "src" / "currency" / "src" / "server.cpp"
        text = server.read_text(encoding="utf-8")
        old = """  const bool tracer_shutdown =
      tracer_provider->Shutdown(remainingShutdownTimeout(server_shutdown.deadline));
  if (!tracer_shutdown) {
    std::cerr << "Tracer provider shutdown failed\\n";
  }
"""
        new = """  if (tracer_provider != nullptr) {
    const bool tracer_shutdown =
        tracer_provider->Shutdown(remainingShutdownTimeout(server_shutdown.deadline));
    if (!tracer_shutdown) {
      std::cerr << "Tracer provider shutdown failed\\n";
    }
  }
"""
        server.write_text(self._replace_once(text, old, new, server), encoding="utf-8")

    def _patch_shipping_context_neutral(self) -> None:
        path = self.source / "src" / "shipping" / "src" / "telemetry_conf.rs"
        text = path.read_text(encoding="utf-8")
        text = self._replace_once(
            text,
            "use opentelemetry_sdk::trace::{Sampler, SdkTracerProvider};",
            "use opentelemetry_sdk::trace::SdkTracerProvider;",
            path,
        )
        old = """fn init_tracer_provider() -> SdkTracerProvider {
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
"""
        new = """fn init_tracer_provider() -> Option<SdkTracerProvider> {
    let native_tracing_disabled =
        matches!(std::env::var("OTEL_SDK_DISABLED").as_deref(), Ok("true"));
    if native_tracing_disabled {
        return None; // v5: retain the global no-op provider and propagator
    }

    global::set_text_map_propagator(TraceContextPropagator::new());
    let tracer_provider = SdkTracerProvider::builder()
        .with_resource(get_resource())
        .with_batch_exporter(
            opentelemetry_otlp::SpanExporter::builder()
                .with_http()
                .with_protocol(Protocol::HttpBinary)
                .build()
                .expect("Failed to initialize tracing provider"),
        )
        .build();
    global::set_tracer_provider(tracer_provider.clone());
    Some(tracer_provider)
}
"""
        text = self._replace_once(text, old, new, path)
        text = self._replace_once(
            text,
            "    tracer_provider: SdkTracerProvider,",
            "    tracer_provider: Option<SdkTracerProvider>,",
            path,
        )
        text = self._replace_once(
            text,
            "        if let Err(e) = self.tracer_provider.shutdown() {\n"
            "            eprintln!(\"Failed to shutdown TracerProvider: {e}\");\n"
            "        }",
            "        if let Some(tracer_provider) = self.tracer_provider {\n"
            "            if let Err(e) = tracer_provider.shutdown() {\n"
            "                eprintln!(\"Failed to shutdown TracerProvider: {e}\");\n"
            "            }\n"
            "        }",
            path,
        )
        path.write_text(text, encoding="utf-8")


__all__ = ["Adapter"]
