<h1 align="center">LatexToCalc-Server</h1>



### <div align="center">A translation engine and webserver for translating LaTeX into a format usable by most calculators, eg. <img src="https://schoolstore.fi/wp-content/uploads/2019/02/ti-nspirecx_cas_ss_icon_lo.png" alt="TI-Nspire CX CAS" width="15" height="15" style="vertical-align: bottom;">TI-Nspire CX CAS.</div>

---
[![Server-Status](https://img.shields.io/website?url=https%3A%2F%2Fotso.veistera.com&up_message=online&down_message=offline&style=flat&label=server
)](https://otso.veistera.com)

### Frontend Repository: [LatexToCalc Chrome Extension](https://github.com/OtsoBear/LatexToCalc)

### Installation

1. Clone the repository.
2. Customize the `server.conf` file for Nginx, or remove it if not needed.
3. Execute the `start.sh` script to automate the setup of a virtual environment and install dependencies.

### Overview
This Flask-based web application serves as a powerful API for translating ${\LaTeX}$ 
 expressions into calculator-friendly formats. For instance, the expression $\frac{3}{2}$, or `\frac{3}{2}`  translates to `((3)/(2))`, streamlining input for popular calculator interfaces.

### Technical Highlights

- **Flask Framework**: Utilizes Flask to build an Aaynchronous and lightweight web application architecture, designed to provide a REST API with low-latency interactions.
  
- **Advanced Logging Mechanism**: Implements a dual logging system with separate log files for general and error logs, enhancing traceability and debugging. Logs include timestamps and performance statistic for improved context.

- **Automated Dependency Management**: The `start.sh` script seamlessly manages the creation of a virtual environment and installation of required packages from `requirements.txt`. It intelligently prompts for missing components like Python and `pip`, ensuring a smooth setup process.

- **Multi-Endpoint Architecture**: Supports both browser and HTTP POST requests, with dedicated endpoints for each. The `/translate` endpoint processes JSON payloads for LaTeX translations and logs performance metrics, while also serving a user-friendly translation page for interactive use.

- **Parallel Processing**: Uses Gunicorn to run multiple worker processes, allowing for concurrent handling of translation requests and optimizing response times under load.

### Continuous Integration (CI)
- **GitHub Actions automatically runs unit tests whenever changes are pushed to GitHub. This ensures that the codebase remains functional and reliable while quickly identifying any issues introduced by recent changes.** The most recent status of those tests is right here:
[![Tests](https://github.com/OtsoBear/LatexToCalc-Server/actions/workflows/Tests.yml/badge.svg?branch=main&event=push)](https://github.com/OtsoBear/LatexToCalc-Server/actions/workflows/Tests.yml)

### REST API Endpoints

This API uses the REST (Representational State Transfer) architecture for handling LaTeX translation requests through structured HTTP methods like POST and OPTIONS.

- **Translation Endpoint (`/translate`)**:
  - **POST**: Accepts LaTeX formulas from the associated Chrome Extension and provides customization options for the output. It logs execution time and the original request for performance tracking.
  - **OPTIONS**: Manages CORS preflight requests, ensuring proper permissions before processing more complex interactions.

### Non-RESTful Routes

- **Index Route (`/`)**: Serves the main HTML interface for user interactions, providing a front-end page for accessing the service.

### Error Management

The application includes error handling to provide helpful messages when issues arise, along with sorted logging to capture details for later review, contributing to a smooth user experience.

### Execution Flow

Nginx functions as a reverse proxy, routing incoming traffic to the Flask application. The Flask app processes requests through the local `translateLatex` module and returns complete responses, ensuring efficient resource utilization and scalability.

--- 
