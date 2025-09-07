# AppDynamics Connection Test Files

This directory contains test files for testing AppDynamics OAuth2 authentication and SSL verification.

## Test Files

### 1. `test_appdynamics_simple.py`
**Simple connection test with direct credentials**

```bash
python test_appdynamics_simple.py
```

**Features:**
- Quick connection test
- Direct credential passing
- SSL verification disabled
- Shows available applications

**Usage:**
1. Update `CLIENT_SECRET` in the file with your actual secret
2. Run the test
3. Or set environment variables:
   ```bash
   export APPDYNAMICS_BASE_URL='https://your-controller.saas.appdynamics.com'
   export APPDYNAMICS_CLIENT_ID='your_client_id'
   export APPDYNAMICS_CLIENT_SECRET='your_client_secret'
   ```

### 2. `test_appdynamics_config.py`
**Configuration management test**

```bash
python test_appdynamics_config.py
```

**Features:**
- Tests configuration creation and saving
- Tests configuration loading and validation
- Tests client creation with loaded configuration
- Validates SSL verification settings

### 3. `test_appdynamics_connection.py`
**Comprehensive test suite with multiple test methods**

```bash
python test_appdynamics_connection.py
```

**Features:**
- Multiple test scenarios (direct, environment, config file)
- Rich console output with tables and panels
- Project-specific testing
- Server discovery
- Comprehensive error reporting

## Configuration Methods

### Method 1: Direct Configuration
Update the credentials directly in the test files:

```python
BASE_URL = "https://chubbinaholdingsinc-prod.saas.appdynamics.com"
CLIENT_ID = "sci_mp_read"
CLIENT_SECRET = "your_actual_client_secret"
```

### Method 2: Environment Variables
Set environment variables:

```bash
export APPDYNAMICS_BASE_URL='https://chubbinaholdingsinc-prod.saas.appdynamics.com'
export APPDYNAMICS_CLIENT_ID='sci_mp_read'
export APPDYNAMICS_CLIENT_SECRET='your_actual_client_secret'
```

### Method 3: Configuration File
Use the CLI to create a configuration file:

```bash
lumos-cli appdynamics config
```

Then test with the configuration file.

## Test Scenarios

### 1. OAuth2 Authentication Test
- Tests client credentials flow
- Validates access token retrieval
- Checks token caching and refresh

### 2. SSL Verification Test
- Confirms SSL verification is disabled
- Tests with self-signed certificates
- Validates warning suppression

### 3. API Connection Test
- Tests connection to AppDynamics controller
- Retrieves application list
- Validates API response format

### 4. Project-Specific Test
- Tests specific project/application lookup
- Retrieves server information
- Validates project permissions

## Expected Output

### Successful Connection
```
🔧 Testing AppDynamics connection...
   URL: https://chubbinaholdingsinc-prod.saas.appdynamics.com
   Client ID: sci_mp_read
   SSL Verification: Disabled
✅ Connection successful!
✅ Found 5 applications
   1. SCI Markpet Place PROD Azure (ID: 12345)
   2. SCI Market Place PROD (ID: 67890)
   ...
```

### Failed Connection
```
❌ Connection failed!
Please check:
  • Controller URL is correct
  • Client ID and Client Secret are valid
  • OAuth2 credentials have proper permissions
  • Network connectivity to AppDynamics
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check client ID and secret
   - Verify OAuth2 credentials have proper permissions
   - Ensure credentials are not expired

2. **SSL Certificate Errors**
   - SSL verification is disabled by default
   - Check if `urllib3.disable_warnings()` is working
   - Verify `session.verify = False` is set

3. **Connection Timeout**
   - Check network connectivity
   - Verify controller URL is accessible
   - Check firewall settings

4. **No Applications Found**
   - Verify OAuth2 credentials have application access
   - Check if applications exist in the controller
   - Verify project names are correct

### Debug Mode

Enable debug logging by setting environment variable:

```bash
export LUMOS_DEBUG=true
python test_appdynamics_simple.py
```

This will show detailed OAuth2 token requests and API calls.

## Security Notes

- Never commit real credentials to version control
- Use environment variables for production testing
- Store configuration files with proper permissions (600)
- Rotate credentials regularly

## Integration with Lumos CLI

These test files use the same AppDynamics client as the main Lumos CLI:

- `AppDynamicsClient` - OAuth2 authentication and API calls
- `AppDynamicsConfig` - Configuration data structure
- `AppDynamicsConfigManager` - Configuration file management

The test files validate that the integration works correctly before using it in the main CLI.
