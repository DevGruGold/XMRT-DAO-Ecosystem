# n8n Integration for XMRT DAO Ecosystem

## Overview

This document provides comprehensive information about the n8n workflow automation integration added to the XMRT DAO Ecosystem. The integration enables visual workflow management, AI agent orchestration, and external service automation while maintaining the existing Flask-based architecture.

## What is n8n?

n8n is an open-source workflow automation tool that allows you to connect different services and automate processes through a visual interface. It provides a node-based editor where you can create complex workflows by connecting various services, APIs, and data sources.

## Integration Architecture

### Service Layer Design

The n8n integration follows a non-invasive approach that adds new capabilities without modifying existing core services:

```
XMRT Flask Application
├── Existing Services (unchanged)
│   ├── EnhancedSupportXMRService
│   ├── MESHNETService
│   ├── ElizaAgentService
│   ├── HealthService
│   ├── SpeechService
│   ├── MemoryService
│   └── AutonomyService
└── New n8n Integration Layer
    ├── N8NService
    ├── WorkflowManager
    ├── N8NAPIClient
    └── WorkflowExecutor
```

### Key Components

#### N8NService
The main service class that manages n8n integration:
- Handles communication with n8n instance
- Manages workflow execution and monitoring
- Provides status and health checking
- Integrates with existing XMRT services

#### N8NAPIClient
HTTP client for communicating with n8n REST API:
- Workflow management operations
- Execution monitoring
- Health checks
- Asynchronous operations

#### WorkflowManager
Manages workflow definitions and execution history:
- Stores workflows in memory service
- Tracks execution status
- Provides workflow metadata

## New API Endpoints

The integration adds the following REST API endpoints under `/api/n8n/`:

### Service Management
- `GET /api/n8n/status` - Get n8n service status
- `GET /api/n8n/health` - Health check for n8n service
- `GET /api/n8n/capabilities` - Get available capabilities

### Workflow Management
- `GET /api/n8n/workflows` - List all workflows
- `GET /api/n8n/workflows/{id}` - Get workflow details
- `POST /api/n8n/workflows/{id}/execute` - Execute workflow

### Execution Monitoring
- `GET /api/n8n/executions` - List recent executions
- `GET /api/n8n/executions/{id}` - Get execution status

### Service Integration
- `GET /api/n8n/services/mining/capabilities` - Mining service integration
- `GET /api/n8n/services/meshnet/capabilities` - Meshnet service integration
- `GET /api/n8n/services/agent/capabilities` - Eliza agent integration

### Demo and Testing
- `POST /api/n8n/integration/demo` - Create demo workflow

## Installation and Setup

### Prerequisites

1. **Python Dependencies**: All required packages are included in `requirements.txt`
2. **n8n Instance**: Either local Docker installation or external n8n service
3. **Redis**: For workflow state persistence (already included in XMRT)

### Local Development Setup

#### Option 1: Using Docker Compose (Recommended)

1. Start n8n and Redis services:
```bash
docker-compose -f docker-compose.n8n.yml up -d
```

2. Access n8n interface at `http://localhost:5678`
   - Username: `admin`
   - Password: `xmrt-n8n-2024`

3. Start XMRT application:
```bash
python3 app.py
```

#### Option 2: External n8n Instance

1. Set environment variables:
```bash
export N8N_URL=https://your-n8n-instance.com
export N8N_API_KEY=your-api-key
```

2. Start XMRT application:
```bash
python3 app.py
```

### Production Deployment

#### Environment Variables

Configure the following environment variables for production:

```bash
# n8n Configuration
N8N_URL=https://your-n8n-instance.com
N8N_API_KEY=your-secure-api-key

# Existing XMRT variables
SECRET_KEY=your-production-secret-key
# ... other existing variables
```

#### Deployment Steps

1. **Deploy n8n Instance**: Set up n8n on your preferred platform
2. **Configure API Access**: Generate API key in n8n settings
3. **Update Environment**: Set N8N_URL and N8N_API_KEY
4. **Deploy XMRT**: Deploy with updated environment variables
5. **Verify Integration**: Test n8n endpoints and functionality

## Usage Examples

### Basic Workflow Execution

```python
import requests

# Execute a workflow
response = requests.post('http://localhost:5000/api/n8n/workflows/workflow-id/execute', 
                        json={'input_data': {'message': 'Hello World'}})

execution_id = response.json()['data']['execution_id']

# Check execution status
status_response = requests.get(f'http://localhost:5000/api/n8n/executions/{execution_id}')
print(status_response.json())
```

### Integration with Eliza Agent

```python
# Create a workflow that interacts with Eliza
workflow_data = {
    "input_data": {
        "command": "get mining status",
        "user_id": "user123"
    }
}

response = requests.post('http://localhost:5000/api/n8n/workflows/eliza-integration/execute',
                        json=workflow_data)
```

### Service Status Monitoring

```python
# Check n8n service health
health_response = requests.get('http://localhost:5000/api/n8n/health')
print(f"n8n Health: {health_response.json()['healthy']}")

# Get service capabilities
capabilities_response = requests.get('http://localhost:5000/api/n8n/capabilities')
print(f"Capabilities: {capabilities_response.json()['data']}")
```

## Workflow Examples

### Example 1: Mining Status Monitor

This workflow monitors mining status and sends alerts:

```json
{
  "name": "Mining Status Monitor",
  "nodes": [
    {
      "id": "trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "rule": {
          "interval": [{"field": "minutes", "value": 5}]
        }
      }
    },
    {
      "id": "get_mining_status",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:5000/api/dashboard",
        "method": "GET"
      }
    },
    {
      "id": "check_hashrate",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{$json.hashrate}}",
              "operation": "smaller",
              "value2": 1000
            }
          ]
        }
      }
    }
  ]
}
```

### Example 2: Eliza Agent Automation

This workflow automates Eliza agent interactions:

```json
{
  "name": "Eliza Automation",
  "nodes": [
    {
      "id": "webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "eliza-trigger"
      }
    },
    {
      "id": "process_command",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:5000/api/chat",
        "method": "POST",
        "body": {
          "message": "={{$json.command}}"
        }
      }
    },
    {
      "id": "store_response",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:5000/api/memory/store",
        "method": "POST",
        "body": {
          "content": "={{$json.reply}}",
          "context": "automated_response"
        }
      }
    }
  ]
}
```

## Security Considerations

### API Security

1. **Authentication**: Use API keys for n8n access
2. **Rate Limiting**: Implement rate limiting on workflow execution
3. **Input Validation**: Validate all workflow inputs
4. **Audit Logging**: Log all workflow operations

### Network Security

1. **Service Isolation**: Run n8n in isolated container
2. **Encrypted Communication**: Use HTTPS for all API calls
3. **Access Control**: Limit network access to required services
4. **Regular Updates**: Keep n8n and dependencies updated

### Data Protection

1. **Sensitive Data**: Avoid storing sensitive data in workflows
2. **Encryption**: Encrypt workflow data at rest
3. **Access Logs**: Monitor access to workflow data
4. **Backup Security**: Secure workflow backups

## Monitoring and Troubleshooting

### Health Checks

The integration provides comprehensive health monitoring:

```bash
# Check overall n8n service health
curl http://localhost:5000/api/n8n/health

# Get detailed service status
curl http://localhost:5000/api/n8n/status

# Check individual service capabilities
curl http://localhost:5000/api/n8n/services/mining/capabilities
```

### Common Issues

#### n8n Connection Failed
- **Symptom**: "n8n service not healthy" in logs
- **Solution**: Verify n8n is running and accessible
- **Check**: `curl http://localhost:5678/healthz`

#### Workflow Execution Timeout
- **Symptom**: Workflows hang or timeout
- **Solution**: Check n8n logs and increase timeout values
- **Check**: n8n execution logs in interface

#### Memory Service Errors
- **Symptom**: Workflow storage failures
- **Solution**: Verify memory service is initialized
- **Check**: Memory service logs and Redis connectivity

### Logging

The integration provides detailed logging at multiple levels:

```python
# Enable debug logging
import logging
logging.getLogger('src.services.n8n_service').setLevel(logging.DEBUG)
```

Log locations:
- **Application Logs**: Standard Flask application logs
- **n8n Logs**: n8n container logs (if using Docker)
- **Workflow Logs**: Stored in n8n execution history

## Performance Considerations

### Resource Management

1. **Memory Usage**: Monitor workflow memory consumption
2. **CPU Usage**: Limit concurrent workflow executions
3. **Network Bandwidth**: Optimize API call frequency
4. **Storage**: Regular cleanup of old execution data

### Optimization Strategies

1. **Workflow Design**: Design efficient workflows
2. **Caching**: Cache frequently accessed data
3. **Batch Processing**: Group related operations
4. **Async Operations**: Use asynchronous execution where possible

### Scaling Considerations

1. **Horizontal Scaling**: Scale n8n instances for high load
2. **Load Balancing**: Distribute workflow execution
3. **Database Optimization**: Optimize workflow storage
4. **Resource Limits**: Set appropriate resource limits

## Future Enhancements

### Planned Features

1. **Advanced Agent Orchestration**: Multi-agent workflow support
2. **External Integrations**: Pre-built connectors for common services
3. **Workflow Templates**: Library of common XMRT workflows
4. **Real-time Monitoring**: Enhanced monitoring and alerting
5. **Workflow Versioning**: Version control for workflows

### Integration Opportunities

1. **Blockchain Integration**: Direct blockchain interaction workflows
2. **Social Media Automation**: Automated social media management
3. **Data Pipeline Management**: ETL workflows for data processing
4. **External API Integration**: Seamless third-party service integration

## Support and Maintenance

### Regular Maintenance Tasks

1. **Update Dependencies**: Keep n8n and Python packages updated
2. **Clean Execution History**: Remove old workflow executions
3. **Monitor Performance**: Regular performance analysis
4. **Security Audits**: Periodic security reviews

### Backup and Recovery

1. **Workflow Backup**: Regular backup of workflow definitions
2. **Execution History**: Backup important execution data
3. **Configuration Backup**: Backup n8n configuration
4. **Recovery Testing**: Regular recovery procedure testing

## Conclusion

The n8n integration provides powerful workflow automation capabilities to the XMRT DAO Ecosystem while maintaining system stability and security. The non-invasive integration approach ensures that existing functionality remains unaffected while adding significant new capabilities for automation and orchestration.

The integration is designed to be production-ready with comprehensive error handling, monitoring, and security features. It provides a solid foundation for future enhancements and can scale to meet growing automation needs.

For additional support or questions about the n8n integration, refer to the XMRT project documentation or contact the development team.

