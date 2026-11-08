# Allocation of runtime treatments

Each logical block fixes application, SDK mode and repetition and contains the
no-agent, OBI, Coroot and DeepFlow treatments. Capture and validation orders are
independently randomized and recorded in the block plan.

Petclinic/full/9 and OTel/full/9 contain eight physically paired cases. Within
each phase, their four treatments run sequentially on the same physical worker,
using fresh guest overlays and application state. Capture and validation still
use separate deployments and workers.

The other 100 cases use separate physical workers for the treatments. Each
capture has fresh guest kernels and a clean application deployment. Model
processing uses the exact closed capture. Validation starts only after all four
models in the block are frozen and published, and uses four fresh deployments.

The blueprint, logical identities, fixtures, routing, operations, scenario law
and permitted semantic information are common across treatments. Physical host
identity and phase resource observations remain explicit. Separate workers do
not provide physical pairing for overhead or individual runtime-causality claims.

Failed technical prefixes and their costs remain recorded separately from the
fixed canonical case selection. No short qualification, auxiliary diagnostic or
outcome-selected replacement supplies a scientific case.
