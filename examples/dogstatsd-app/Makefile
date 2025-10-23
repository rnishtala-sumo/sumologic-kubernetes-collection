# DogStatsD Sample App Makefile

# Variables
IMAGE_NAME := dogstatsd-sample-app
IMAGE_TAG := latest
NAMESPACE := default

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  build         - Build the Docker image"
	@echo "  build-no-cache - Build the Docker image without cache"
	@echo "  load-kind     - Load image into kind cluster"
	@echo "  load-minikube - Load image into minikube"
	@echo "  load-microk8s - Load image into microk8s cluster"
	@echo "  push-microk8s - Push image to microk8s local registry"
	@echo "  deploy        - Deploy to Kubernetes"
	@echo "  deploy-local  - Build and load image, then deploy (for local dev)"
	@echo "  undeploy      - Remove from Kubernetes"
	@echo "  logs          - Show application logs"
	@echo "  status        - Show deployment status"
	@echo "  test          - Test the application locally"
	@echo "  clean         - Clean up Docker images"
	@echo "  clean-microk8s - Clean up images from microk8s registry"
	@echo "  clean-all     - Clean up all images and deployments"
	@echo "  local         - Full local development workflow (build + deploy + status)"
	@echo "  force-local   - Force rebuild and redeploy (no cache, for troubleshooting)"
	@echo "  dev           - Development workflow (deploy + logs)"

# Build the Docker image
.PHONY: build
build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "Image built: $(IMAGE_NAME):$(IMAGE_TAG)"

# Build the Docker image without cache (for troubleshooting)
.PHONY: build-no-cache
build-no-cache:
	docker build --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "Image built (no cache): $(IMAGE_NAME):$(IMAGE_TAG)"

# Load image into kind cluster (if using kind)
.PHONY: load-kind
load-kind: build
	@if command -v kind >/dev/null 2>&1; then \
		kind load docker-image $(IMAGE_NAME):$(IMAGE_TAG) || echo "Failed to load into kind cluster"; \
	else \
		echo "Kind not found, skipping image load"; \
	fi

# Load image into minikube (if using minikube)
.PHONY: load-minikube
load-minikube: build
	@if command -v minikube >/dev/null 2>&1; then \
		minikube image load $(IMAGE_NAME):$(IMAGE_TAG) || echo "Failed to load into minikube"; \
	else \
		echo "Minikube not found, skipping image load"; \
	fi

# Load image into microk8s cluster (if using microk8s)
.PHONY: load-microk8s
load-microk8s: build
	@if command -v microk8s >/dev/null 2>&1; then \
		echo "Loading image into microk8s cluster..."; \
		docker save $(IMAGE_NAME):$(IMAGE_TAG) | microk8s ctr image import - || echo "Failed to load into microk8s cluster"; \
	else \
		echo "MicroK8s not found, skipping image load"; \
	fi

# Push image to microk8s local registry
.PHONY: push-microk8s
push-microk8s: build
	@if command -v microk8s >/dev/null 2>&1; then \
		echo "Pushing image to microk8s local registry..."; \
		docker tag $(IMAGE_NAME):$(IMAGE_TAG) localhost:32000/$(IMAGE_NAME):$(IMAGE_TAG) && \
		docker push localhost:32000/$(IMAGE_NAME):$(IMAGE_TAG) || echo "Failed to push to microk8s registry"; \
	else \
		echo "MicroK8s not found, skipping registry push"; \
	fi

# Deploy to Kubernetes
.PHONY: deploy
deploy:
	kubectl apply -f kubernetes-manifests.yaml
	@echo "Deployed to namespace: $(NAMESPACE)"

# Deploy with local image loading (for local development)
.PHONY: deploy-local
deploy-local: load-kind load-minikube push-microk8s deploy

# Remove from Kubernetes
.PHONY: undeploy
undeploy:
	kubectl delete -f kubernetes-manifests.yaml --ignore-not-found=true
	@echo "Removed from namespace: $(NAMESPACE)"

# Show application logs
.PHONY: logs
logs:
	kubectl logs -l app=dogstatsd-sample-app -f --namespace=$(NAMESPACE)

# Show deployment status
.PHONY: status
status:
	kubectl get pods,svc -l app=dogstatsd-sample-app --namespace=$(NAMESPACE)

# Test the application locally
.PHONY: test
test:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Running application for 30 seconds..."
	timeout 30 python app.py || true
	@echo "Test completed"

# Clean up Docker images
.PHONY: clean
clean:
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG) || true
	@echo "Cleaned up Docker images"

# Clean up images from microk8s registry
.PHONY: clean-microk8s
clean-microk8s:
	@if command -v microk8s >/dev/null 2>&1; then \
		echo "Removing image from microk8s registry..."; \
		microk8s ctr images rm localhost:32000/$(IMAGE_NAME):$(IMAGE_TAG) || true; \
		microk8s ctr images rm $(IMAGE_NAME):$(IMAGE_TAG) || true; \
	else \
		echo "MicroK8s not found, skipping registry cleanup"; \
	fi

# Clean up all images (local Docker + microk8s)
.PHONY: clean-all
clean-all: undeploy clean clean-microk8s
	@echo "Cleaned up all images and deployments"

# Build and deploy in one command
.PHONY: all
all: build deploy status

# Build and deploy for local development
.PHONY: local
local: deploy-local status

# Force rebuild and redeploy (for troubleshooting)
.PHONY: force-local
force-local: build-no-cache push-microk8s undeploy deploy status

# Development workflow
.PHONY: dev
dev: deploy-local logs