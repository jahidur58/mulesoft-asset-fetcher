# Download RAML or OpenAPI Specifications from Anypoint Exchange

This Python script automates the process of downloading RAML or OpenAPI specifications from the **MuleSoft Anypoint Exchange** for all REST APIs in a specific organization.

## Features
- Authenticate with Anypoint Platform using client credentials.
- Retrieve all REST APIs in a specified organization, iterating through paginated results.
- Download supported files (RAML, OpenAPI, etc.) for each REST API.
- Save downloaded files locally in a structured format.

## Prerequisites
Before running the script, make sure you have:
- **Python 3.x** installed.
- A MuleSoft Anypoint Platform account.
- Client ID and Client Secret for Anypoint authentication.
- The `requests` Python package installed. You can install it with:
  ```bash
  pip install requests
