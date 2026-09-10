# Distributions

`distributions/` contains derived delivery artifacts. They are canonical for
their published payloads and may own payload-specific support contracts, but
not the underlying Playbook doctrine, provider runtime semantics, adapters, or
general tooling architecture.

Children may have different delivery shapes. [`starter/`](starter/) is an
adoption package; [`global-bootstrap/`](global-bootstrap/) is a copy-ready
router distribution with its supported local reconciliation checks. Follow each
child's boundary and link to the canonical owner for the guidance it consumes.
