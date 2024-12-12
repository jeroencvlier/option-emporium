LATEST_TAG := $(shell git describe --tags --abbrev=0 2>/dev/null || echo 0.0.0)
NEW_TAG := $(shell echo $(LATEST_TAG) | awk -F. '{printf "%d.%d.%d", $$1, $$2, $$3+1}')

.PHONY: release 
release:
	poetry lock || { echo "Error: Poetry lock failed."; exit 1; }

	@if [ -z "$(LATEST_TAG)" ]; then \
		echo "No tags found. Initializing tag to 0.0.1"; \
		NEW_TAG=0.0.1; \
	else \
		echo "Latest tag: $(LATEST_TAG)"; \
		echo "New tag: $(NEW_TAG)"; \
	fi; \
	git add .; \
	git commit -m "Auto-commit: preparing for release $(NEW_TAG)"; \
	git push origin; \
	git tag $(NEW_TAG); \
	git push origin $(NEW_TAG);

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  release  - Increment the bug-fix version of the latest tag, commit changes, and push it."