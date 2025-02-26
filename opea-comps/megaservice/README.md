# OPEA MegaService

A basic implementation of the OPEA MegaService component. This service orchestrates the interaction between different microservices in the OPEA ecosystem, specifically managing the flow between embedding and LLM services.

## Prerequisites

- Python 3.9 or higher
- Poetry (Python package manager)
- Access to OPEA embedding and LLM services

## Configuration

The service can be configured using environment variables:

```bash
# Embedding Service Configuration
EMBEDDING_SERVICE_HOST_IP=0.0.0.0  # default
EMBEDDING_SERVICE_PORT=6000        # default

# LLM Service Configuration
LLM_SERVICE_HOST_IP=0.0.0.0       # default
LLM_SERVICE_PORT=9000             # default
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd megaservice
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Usage

1. Activate the Poetry virtual environment:
```bash
poetry shell
```

2. Run the MegaService:
```bash
python -m opea_megaservice.main
```

## Service Architecture

The MegaService orchestrates the following components:
- Embedding Service: Handles text embedding operations
- LLM Service: Processes language model requests

The service flow is configured as: Embedding Service → LLM Service

## Contributing

Please refer to the main OPEA project contribution guidelines.

## License

This project is part of the OPEA ecosystem. Please refer to the main project for license information.
