LATEST_TAG := $(shell git describe --tags --abbrev=0 2>/dev/null || echo 0.0.0)

# Function to calculate the next available tag
define NEXT_AVAILABLE_TAG
$(shell \
    latest=$(LATEST_TAG); \
    while git tag | grep -q "^$${latest}$$"; do \
        latest=$$(echo $${latest} | awk -F. '{printf "%d.%d.%d", $$1, $$2, $$3+1}'); \
    done; \
    echo $${latest} \
)
endef

NEW_TAG := $(call NEXT_AVAILABLE_TAG)

.PHONY: release commit-prep increment-version test

test:
	poetry run pytest -v --maxfail=1 --disable-warnings || { echo "Error: Tests failed."; exit 1; }

commit: test
	poetry lock || { echo "Error: Poetry lock failed."; exit 1; }
	@if [ "$(LATEST_TAG)" = "0.0.0" ]; then \
		echo "No tags found. Initializing tag to 0.0.1"; \
		NEW_TAG=0.0.1; \
	else \
		echo "Latest tag: $(LATEST_TAG)"; \
		echo "New tag: $(NEW_TAG)"; \
	fi; \
	git add .; \
	git commit -m "Auto-commit: preparing for release $(NEW_TAG)"; 
# \
# git push origin; \

increment-version: 
	git tag $(NEW_TAG); \
	git push origin $(NEW_TAG);

release: test commit-prep increment-version

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  release  - Increment the bug-fix version of the latest tag, run poetry lock, commit changes, and push it."
