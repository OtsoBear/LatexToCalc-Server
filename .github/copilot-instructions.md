# LatexToCalc-Server Copilot Instructions

## Architecture Overview

This is a Flask-based LaTeX translation service that converts LaTeX mathematical expressions into calculator-friendly formats (primarily TI-Nspire CX CAS). The service processes complex LaTeX expressions through a multi-stage translation pipeline and serves them via a RESTful API.

**Core Architecture Components:**
- **Flask Server** (`python/src/server.py`): Main web application handling HTTP requests
- **Translation Engine** (`python/src/translatelatex.py`): Core LaTeX parsing and transformation logic (1853 lines)
- **Nginx Reverse Proxy** (`nginx/server.conf`): SSL termination and request routing
- **Production Deployment** (`python/src/start.sh`): Automated setup with Gunicorn
- **Chrome Extension Integration**: Consumes the `/translate` endpoint for real-time translation

## Key Components

### Translation Engine (`translatelatex.py`)

**Core Class: `LatexToCalcEngine`**
- Contains 8 major dictionaries for different LaTeX element types
- Handles calculator-specific output formatting (TI-Nspire vs Scientific)
- Processes nested expressions using recursive regex patterns

**Translation Pipeline Architecture:**
The main `translate()` function follows this exact sequence:
1. **Preprocessing**: `\\operatorname` cleanup, symbol replacement
2. **Greek Letters**: Unicode conversion (`\\alpha` → `α`)
3. **Constants**: Physics constants (`_Gc`, `_Na`, etc.) if enabled
4. **Tag Application**: Nested structure parsing (`applyTags()`)
5. **Units Processing**: SI prefixes and unit conversion (2-phase)
6. **Mathematical Functions**: Sum, product, integrals, limits
7. **Combinations/Permutations**: `nCr`, `nPr` functions
8. **Derivatives**: `{d}/{dx}` pattern recognition
9. **Fractions**: `\\frac{a}{b}` → `((a)/(b))`
10. **Logarithms**: Base-specific formatting by calculator type
11. **Subscripts**: Unicode subscript conversion
12. **Square Roots**: `\\sqrt` and `\\sqrt[n]` handling
13. **Systems**: `\\begin{cases}` matrix notation
14. **Vectors/Matrices**: Complex nested processing
15. **Final Cleanup**: Identifier removal, multiplication insertion

**Calculator Mode Differences:**
- **TI-Nspire Mode** (`TI_on=True`): `log(arg,base)`, `nCr(n,r)`, `root(x,n)`
- **Scientific Mode** (`SC_on=False`): `log(base;arg)`, semicolon separators
- **Units**: TI uses `⁃prefix』unit` system, Scientific uses full names

**Feature Flags:**
- `constants_on`: Physics constants replacement
- `coulomb_on`: Coulomb constant (`k` → `_Cc`)
- `e_on`: Euler's number handling (`e` → `@e`)
- `i_on`: Imaginary unit handling (`i` → `@i`)
- `g_on`: Gravitational constant handling (`g` → `_g`)

### Server Architecture (`server.py`)

**Logging System:**
- **Dual Logging**: Separate `app.log` and `error.log` files
- **Performance Metrics**: Request timing logged in milliseconds
- **IP Tracking**: Extracts real IP from `X-Real-IP` and `X-Forwarded-For` headers
- **Settings Tracking**: Active flags logged as abbreviations (TI, SC, CO, CL, E, I, G)

**Request Handling:**
- **Timeout Protection**: 30-second SIGALRM timeout for complex expressions
- **Expression Length Limit**: 10 billion characters (intentionally high)
- **Multi-Method Endpoints**: `/translate` handles POST (API), GET (HTML), OPTIONS (CORS)
- **Error Responses**: JSON format with appropriate HTTP status codes

**Security & Performance:**
- **CORS Enabled**: For Chrome extension integration
- **Request Validation**: JSON parsing and expression validation
- **Memory Protection**: Timeout prevents infinite loops
- **Load Balancing**: Gunicorn with 4 workers in production

## Development Workflows

### Local Development Setup
```bash
cd python/src
./start.sh  # Auto-creates venv, installs deps, starts with Gunicorn on port 5002
```

**What `start.sh` does:**
1. Checks for Python3, pip, and venv availability
2. Creates virtual environment at `../venv` if missing
3. Installs dependencies from `../requirements.txt`
4. Starts Gunicorn with 4 workers on `0.0.0.0:5002`
5. Handles cross-platform package manager detection (apt, yum, dnf, pacman, brew)

### Testing & Quality Assurance

**Unit Testing:**
```bash
pytest python/tests/  # Parameterized tests with expected translations
```

**Test Structure:**
- Tests use `FIXED_PARAMS` dictionary with all boolean flags set to known values
- Test cases are tuples: `(input_latex, expected_output)`
- Add new test cases to `test_cases` list in `test_translatelatex.py`

**Code Quality:**
```bash
flake8 python/src/    # Linting (see .github/workflows/Tests.yml)
```

**CI/CD Pipeline:**
- GitHub Actions runs on push/PR to main branch
- Tests Python 3.10 environment
- Runs both pytest and flake8 validation
- Linting checks: E9,F63,F7,F82 errors + complexity/line length warnings

### Production Deployment

**Nginx Configuration:**
- Serves on ports 80 (redirect) and 443 (SSL)
- SSL certificates via Let's Encrypt
- Proxies to `127.0.0.1:5002` with proper headers
- Handles CORS preflight requests at nginx level

**Gunicorn Configuration:**
- 4 worker processes
- `--limit-request-line 16384` for long expressions
- Binds to `0.0.0.0:5002`
- Module: `server:app`

## Project-Specific Patterns

### Translation Dictionary Structure

**Symbol Dictionaries:**
- `symbols`: Basic operators and symbols (`\\times` → `*ΦcrossΦ`)
- `greek_letters`: LaTeX commands to Unicode (`\\alpha` → `α`)
- `constantsDict`: Physics constants with unit handling (`_Gc`, `_Na`)
- `prefixes`: SI prefix expansions (`k` → `10^3`)
- `units`: Unit abbreviations and conversions
- `arrows`: Directional symbols (`\\rightarrow` → `→`)

**Unit Handling:**
- **TI Format**: `⁃prefix』unit` (e.g., `⁃k』m` for kilometers)
- **Scientific Format**: Full names (e.g., `(kilo meter)`)
- **Two-Phase Processing**: `translateUnits1()` and `translateUnits2()`

### Tag System for Nested Expressions

**Tag Types:**
- `£number£` for `{}` braces
- `$number$` for `()` parentheses  
- `` `number` `` for `[]` brackets
- `§number§` for integral boundaries
- `Ɛnumber Ɛ` for matrix structures
- `「」` for matrix begin/end markers

**Recursive Processing:**
Uses `regex` module with recursive patterns:
```python
result = regex.search(r'(?<rec>\{(?:[^{}]++|(?&rec))*\})', expression)
```

### Calculator-Specific Formatting

**Function Syntax Differences:**
- **TI-Nspire**: `log(arg,base)`, `nCr(n,r)`, `root(x,n)`, `lim(func,var,val)`
- **Scientific**: `log(base;arg)`, semicolon separators, `(x)^(1/(n))` for roots

**Special Characters:**
- **TI Units**: `⁃` (bullet), `』` (corner bracket)
- **Subscripts**: Unicode subscript digits `₀₁₂₃₄₅₆₇₈₉`
- **Vector Notation**: `𝕚` (i), `𝕛` (j), `ӄ` (k)

### Complex Translation Patterns

**Trigonometric Functions:**
- Handles power notation: `\sin^2(x)` → `(sin(x))^(2)`
- Supports nested expressions: `\sin^{\frac{a}{b}}(x)`
- Processes compound arguments: `\sin(x^2)`

**Integral Processing:**
- Definite integrals: `\int_a^b f(x)dx` → `∫((f(x)),(x),(a),(b))`
- Indefinite integrals: `\int f(x)dx` → `∫((f(x)),(x))`
- Handles complex bounds and integrands

**Vector Operations:**
- Dot products: `\bar{a} \cdot \bar{b}` → `dotP((a),(b))`
- Cross products: `\bar{a} \times \bar{b}` → `crossP((a),(b))`
- Matrix notation: `\begin{matrix}...\end{matrix}` → `[[row1],[row2]]`

### Error Handling Patterns

**Timeout Protection:**
```python
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout
try:
    result = translate(expression, **settings)
finally:
    signal.alarm(0)  # Cancel timeout
```

**Logging Standards:**
- **Success**: `IP | expression | result | time_ms | Active Settings: flags`
- **Error**: `IP | expression | Error: message | time_ms`
- **Timeout**: `IP | expression | TIMEOUT | time_ms`

**Response Format:**
- **Success**: `{'result': translated_expression}`
- **Error**: `{'error': 'descriptive_message'}` with appropriate HTTP status
- **Timeout**: HTTP 408 with timeout message

## Common Modifications

### Adding New LaTeX Commands

**1. Basic Symbol Translation:**
```python
# Add to symbols dictionary in LatexToCalcEngine.__init__()
self.symbols = {
    "\\newcommand": "replacement_text",
    # ... existing symbols
}
```

**2. Complex Function Translation:**
```python
# Create new translation method
def translateNewFeature(self, expression):
    # Pattern matching and replacement logic
    pattern = r'\\newcommand\{(.+)\}'
    matches = re.findall(pattern, expression)
    for match in matches:
        # Process and replace
        pass
    return expression

# Add to translation pipeline in translate() function
expression = engine.translateNewFeature(expression)
```

**3. Update Test Cases:**
```python
# Add to test_cases list in test_translatelatex.py
test_cases = [
    (r"\\newcommand{arg}", "expected_output"),
    # ... existing test cases
]
```

### Server Configuration Changes

**Environment Variables:**
- Port: Default 5002 (configurable in `start.sh`)
- Workers: 4 Gunicorn workers (configurable in `start.sh`)
- Timeout: 30 seconds (hardcoded in `server.py`)

**Logging Configuration:**
```python
# Modify logging setup in server.py
log_handler = logging.FileHandler('logs/app.log')
error_log_handler = logging.FileHandler('logs/error.log')
```

**Adding New Endpoints:**
```python
@app.route('/new-endpoint', methods=['POST'])
def new_endpoint():
    # Extract IP for logging
    real_ip = request.headers.get('X-Real-IP')
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        real_ip = forwarded_for.split(',')[0]
    
    # Process request with timeout protection
    start_time = time()
    try:
        # Your logic here
        pass
    except Exception as e:
        app_logger.error(f"{real_ip} | Error: {str(e)}")
        return jsonify({'error': 'Error message'}), 500
```

### Performance Optimization

**Expression Complexity:**
- **Length Limit**: 10 billion characters (intentionally high, can be adjusted)
- **Timeout**: 30 seconds via SIGALRM (prevents infinite loops)
- **Memory**: No explicit limits, relies on system constraints

**Regex Optimization:**
- Use `re.compile()` for frequently used patterns
- Avoid greedy quantifiers in complex expressions
- Consider caching compiled regex patterns

**Translation Pipeline:**
- Order matters: Simple replacements before complex parsing
- Early returns for expressions not containing relevant patterns
- Batch processing for multiple similar patterns

### Database Integration (Future)

**Current State**: No database, stateless translations
**Potential Additions:**
- Translation caching for common expressions
- Usage analytics and popular expressions
- User preferences and custom dictionaries

### Security Considerations

**Input Validation:**
- Expression length limits prevent DoS attacks
- Timeout protection prevents resource exhaustion
- No code evaluation - purely string manipulation

**CORS Configuration:**
- Wildcard origin (`*`) for Chrome extension
- Specific headers allowed: `Content-Type`
- Methods: `POST`, `GET`, `OPTIONS`

**SSL/TLS:**
- Nginx handles SSL termination
- Let's Encrypt certificates with auto-renewal
- HTTP redirects to HTTPS

## Advanced Features

### Multi-Variable Handling

**Automatic Multiplication Insertion:**
```python
# Pattern for adjacent variables: xy → x*y
pattern_xyzabc = re.compile(fr'({"|".join(characters)})+')
expression = pattern_xyzabc.sub(multiplyVariables, expression)
```

**Subscript Processing:**
- Unicode subscripts: `₀₁₂₃₄₅₆₇₈₉`
- Greek subscripts handled specially
- Removes subscripts that don't translate to calculator format

### Physics Constants Integration

**Constant Replacements:**
- `_Gc`: Gravitational constant
- `_Na`: Avogadro's number
- `_c`: Speed of light
- `_h`: Planck's constant
- `_k`: Boltzmann constant

**Unit-Aware Constants:**
- Automatic unit conversion based on calculator mode
- Prefix handling for metric units
- Temperature unit conversions (K, °C)

### Matrix and Vector Operations

**Matrix Notation:**
```latex
\begin{matrix}
a & b \\
c & d
\end{matrix}
```
Becomes: `[[a,b],[c,d]]`

**Vector Operations:**
- Dot product: `dotP([a,b],[c,d])`
- Cross product: `crossP([a,b,c],[d,e,f])`
- Unit vectors: `𝕚` → `[1,0,0]`, `𝕛` → `[0,1,0]`, `ӄ` → `[0,0,1]`

### Calculus Operations

**Derivatives:**
- `\frac{d}{dx}` notation supported
- `D(f)` shorthand for derivatives
- Partial derivatives with subscripts

**Integrals:**
- Definite: `∫((f(x)),(x),(a),(b))`
- Indefinite: `∫((f(x)),(x))`
- Multiple integrals with nested bounds

**Limits:**
- Standard: `lim(f(x),x,a)`
- Directional: `lim(f(x),x,∞,1)` for right limit
- Left limit: `lim(f(x),x,a,-1)`

## Performance Considerations

### Memory Management
- No persistent state between requests
- Garbage collection relies on Python's automatic management
- Large expressions may require significant memory during processing

### Scaling Considerations
- Stateless design allows horizontal scaling
- Nginx load balancing for multiple instances
- Database integration would require session management

### Monitoring and Debugging
- Log analysis for performance bottlenecks
- Error tracking through dual logging system
- Request timing for optimization opportunities

## Integration Points

### Chrome Extension Integration
- **Endpoint**: `POST /translate`
- **Headers**: `Content-Type: application/json`
- **Request**: `{"expression": "latex_string", "TI_on": true, ...}`
- **Response**: `{"result": "translated_expression"}` or `{"error": "message"}`

### External API Usage
- RESTful design allows integration with other tools
- JSON request/response format
- CORS enabled for web applications

### Deployment Infrastructure
- **Nginx**: Reverse proxy and SSL termination
- **Gunicorn**: WSGI server with process management
- **systemd**: Service management (if configured)
- **Let's Encrypt**: Automated SSL certificate management

### Monitoring and Logging
- **Application Logs**: `python/src/logs/app.log`
- **Error Logs**: `python/src/logs/error.log`
- **Nginx Logs**: System-dependent location
- **Performance Metrics**: Request timing in milliseconds

## Troubleshooting Common Issues

### Translation Errors
- Check regex patterns for new LaTeX commands
- Verify translation order in pipeline
- Test with minimal examples first

### Performance Issues
- Monitor request timing in logs
- Check for regex catastrophic backtracking
- Consider expression complexity limits

### Deployment Problems
- Verify nginx configuration
- Check SSL certificate validity
- Ensure proper port forwarding
- Validate Gunicorn worker health
