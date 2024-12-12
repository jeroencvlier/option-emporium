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
.DEFAULT_GOAL := help


.PHONY: release test auto-commit increment-version help

test:
	poetry run pytest -v --maxfail=1 --disable-warnings || { echo "Error: Tests failed."; exit 1; }

stage-release:
	poetry lock || { echo "Error: Poetry lock failed."; exit 1; }
	@if [ "$(LATEST_TAG)" = "0.0.0" ]; then \
		echo "No tags found. Initializing tag to 0.0.1"; \
		NEW_TAG=0.0.1; \
	else \
		echo "Latest tag: $(LATEST_TAG)"; \
		echo "New tag: $(NEW_TAG)"; \
	fi; \
	poetry version $(NEW_TAG) || { echo "Error: Poetry version failed."; exit 1; }
	git add .
	git commit -m "Auto Commit for poetry dependancies and auto release: $(NEW_TAG)"
	git tag -a $(NEW_TAG) -m "Release Tag: $(NEW_TAG)"
	git push origin main
	git push origin $(NEW_TAG);

release: test stage-release

help:
	@echo "Available targets:"
	@echo "  release           - Run tests, increment the bug-fix version of the latest tag, lock dependencies, commit changes, and push the tag."
	@echo "  test              - Run pytest with verbose output, stop after the first failure, and suppress warnings."
	@echo "  auto-commit       - Lock dependencies with Poetry, prepare the commit with the new version, and stage changes."
	@echo "  increment-version - Create and push the new version tag to the remote repository."