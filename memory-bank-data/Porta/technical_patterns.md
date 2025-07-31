# Technical Patterns and Best Practices

## FastAPI Development Patterns

### Endpoint Structure
```python
@app.post("/endpoint_name")
def endpoint_function(req: RequestModel):
    try:
        # Security checks
        # Business logic
        # Response formatting
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

### Security Patterns
1. **Path Validation**
   - Check for `..` patterns
   - Restrict system directories (`/etc`, `/dev`, `/proc`)
   - Validate file/directory existence

2. **Input Validation**
   - Use Pydantic models for request validation
   - Provide sensible defaults
   - Type checking and conversion

3. **Error Handling**
   - Appropriate HTTP status codes
   - Detailed error messages
   - Comprehensive logging

### Logging Patterns
```python
logger.info(f"Operation: {operation_details}")
logger.error(f"Error in operation: {error_details}")
```

## Server Management

### Uvicorn CLI Usage
```bash
# Development with auto-reload
uvicorn porta:app --host 0.0.0.0 --port 8000 --reload

# Production
uvicorn porta:app --host 0.0.0.0 --port 8000
```

### Process Management
- Use PID files for process tracking
- Graceful shutdown handling
- Port conflict resolution

## File Operations Patterns

### Reading Files
- Always specify encoding (`utf-8`)
- Handle encoding errors gracefully
- Check file existence and permissions

### Writing Files
- Create directories if needed
- Atomic write operations
- Proper error handling

### Directory Operations
- Filter hidden files appropriately
- Sort results logically
- Provide meaningful metadata

## Error Handling Strategy

### HTTP Status Codes
- **400 Bad Request**: Invalid input, security violations
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: System errors, permissions

### Exception Types
- **PermissionError**: Access denied
- **UnicodeDecodeError**: Encoding issues
- **TimeoutExpired**: Long-running operations
- **FileNotFoundError**: Missing resources

## Development Workflow

### Code Quality
- Comprehensive error handling
- Detailed logging
- Security-first approach
- Human-readable responses

### Testing Strategy
- Test happy path scenarios
- Test error conditions
- Test security boundaries
- Verify logging output

### Documentation
- Update API documentation
- Provide usage examples
- Document error scenarios
- Keep README current