# Splunk RBAC test harness — every target is idempotent and safe to re-run.
#
# Offline (no Splunk, no credentials):
#   make validate   catalog integrity and referential checks
#   make profile    profile the sample exports; refresh the remediation map
#   make fixtures   generate the synthetic coverage-fixture events
#   make build      render build/apps from the catalog
#   make redaction  verify no production identifier reaches a generated file
#   make coverage   render the RBAC coverage matrix
#
# Against the instance (needs config/.env):
#   make connect    confirm credentials and report the Splunk version
#   make capability-baseline  capture and diff the Splunk capability catalog
#   make deploy     push the generated apps (method from config/settings.yaml)
#   make seed       ingest the sample data into the governed indexes
#   make reseed     clean reload: purge, redeploy, seed (use after changes)
#   make teardown   remove generated apps, catalog indexes, and test users
#   make rebuild    teardown, then the whole chain end to end
#
# Phases 3-5 add: users, test-static, test-behavioral, test, capability-baseline.

PY := python3
EXPORTS := $(wildcard sample_data/*.csv)

.PHONY: help all offline validate profile fixtures build redaction \
        coverage capability-baseline connect deploy deploy-rest seed \
        reseed teardown rebuild clean

# Prints the header block above, so help cannot drift from it.
help:
	@awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' Makefile

# Everything that needs no Splunk and no credentials.
offline: validate fixtures profile build redaction coverage
	@echo "offline pipeline complete"

all: offline deploy seed
	@echo "full pipeline complete"

validate:
	$(PY) -m generators.loader

profile:
ifeq ($(strip $(EXPORTS)),)
	@echo "no sample_data/*.csv to profile — skipping"
else
	@for f in $(EXPORTS); do \
	    $(PY) -m tools.profile_sample_data "$$f" >/dev/null || exit 1; \
	done
	@$(PY) -m tools.resolve_mapping $(EXPORTS) | tail -5
endif

fixtures:
	$(PY) -m generators.make_fixtures

build:
	$(PY) -m generators.build

coverage:
	$(PY) -m tools.coverage_report

capability-baseline:
	$(PY) -m tools.capability_inventory --check-catalog

redaction:
	$(PY) -m tools.verify_redaction $(foreach f,$(EXPORTS),--csv $(f))

connect:
	$(PY) -m deploy.splunk_api

# Chooses rsync or REST from config/settings.yaml: a filesystem sync is the
# strategy's path, but it needs write access to an app directory owned by the
# splunk user, which is not always available (ADR-011).
deploy: build
	@method=$$($(PY) -c "import yaml;print(yaml.safe_load(open('config/settings.yaml'))['deployment']['method'])"); \
	if [ "$$method" = "rsync" ]; then bash deploy/deploy.sh; \
	else $(PY) -m deploy.deploy_rest --restart; fi

deploy-rest: build
	$(PY) -m deploy.deploy_rest --restart

seed:
	$(PY) -m deploy.seed_data

# Clean reload after new data arrives or a decision changes: purge, redeploy,
# then seed. Seeding is not incremental, so this is the safe way to reload.
reseed: teardown deploy seed
	@echo "clean reload complete"

teardown:
	bash deploy/teardown.sh --yes

# Reproducibility check: from a clean instance this must end green.
rebuild: teardown all
	@echo "rebuild from clean complete"

clean:
	rm -rf build reports/resolved_inventory.json reports/seed_state.json
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	@echo "generated output removed; catalog and records untouched"
