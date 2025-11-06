# Supabase Session Pooler Setup Guide

This guide helps you configure Supabase session pooler for optimal performance with the AI Resume Analyzer.

## Why Use Session Pooler?

Session pooler provides several benefits for production applications:

- **Better Connection Management**: Automatic connection pooling and load balancing
- **Improved Performance**: Reduced connection overhead and faster queries
- **Serverless Optimization**: Perfect for serverless deployments and auto-scaling
- **Built-in Resilience**: Automatic retry and failover mechanisms
- **Cost Efficiency**: Reduced database connection costs

## Quick Setup

### Option 1: Automatic Setup (Recommended)

Run the interactive setup script:

```bash
python setup_supabase_pooler.py
```

This script will:
1. Guide you through the configuration process
2. Generate the correct URLs automatically
3. Update your `.env` file
4. Test the connection

### Option 2: Manual Setup

1. **Get your Supabase project reference ID**:
   - Go to [Supabase Dashboard](https://supabase.com/dashboard)
   - Select your project
   - Go to Settings > General
   - Copy the "Reference ID"

2. **Get your session pooler details**:
   - Go to Settings > Database
   - Find "Connection pooling" section
   - Note the individual connection parameters

3. **Update your `.env` file**:

```bash
# Direct connection (fallback)
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# Session pooler configuration (recommended)
SUPABASE_DB_HOST=aws-1-eu-west-1.pooler.supabase.com
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres.ljetrhxwcklhwivtmwmu
SUPABASE_DB_PASSWORD=your_database_password_here
USE_SESSION_POOLER=true

# Connection string format (alternative)
DATABASE_URL=postgresql://postgres.ljetrhxwcklhwivtmwmu:your_password@aws-1-eu-west-1.pooler.supabase.com:5432/postgres
```

3. **Test the connection**:

```bash
python -c "from database import test_database_connection; print(test_database_connection())"
```

## Configuration Options

### Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SUPABASE_URL` | Direct Supabase URL | Yes (fallback) | `https://abc123.supabase.co` |
| `SUPABASE_KEY` | Supabase anon/service key | Yes | `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...` |
| `SUPABASE_DB_HOST` | Session pooler host | No | `aws-1-eu-west-1.pooler.supabase.com` |
| `SUPABASE_DB_PORT` | Database port | No | `5432` |
| `SUPABASE_DB_NAME` | Database name | No | `postgres` |
| `SUPABASE_DB_USER` | Database user | No | `postgres.ljetrhxwcklhwivtmwmu` |
| `SUPABASE_DB_PASSWORD` | Database password | No | `your_db_password` |
| `DATABASE_URL` | Full connection string | No | `postgresql://postgres.user:pass@host:5432/postgres` |
| `USE_SESSION_POOLER` | Enable session pooler | No | `true` or `false` |

### Connection Configuration

**Direct Connection:**
```
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=your_anon_key
```

**Session Pooler (Individual Parameters):**
```
SUPABASE_DB_HOST=aws-1-eu-west-1.pooler.supabase.com
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres.ljetrhxwcklhwivtmwmu
SUPABASE_DB_PASSWORD=your_password
USE_SESSION_POOLER=true
```

**Session Pooler (Connection String):**
```
DATABASE_URL=postgresql://postgres.ljetrhxwcklhwivtmwmu:your_password@aws-1-eu-west-1.pooler.supabase.com:5432/postgres
```

## Connection Behavior

The application uses the following connection priority:

1. **Session Pooler** (if `USE_SESSION_POOLER=true` and `SUPABASE_POOLER_URL` is set)
2. **Direct Connection** (fallback using `SUPABASE_URL`)

If session pooler fails to initialize, the application automatically falls back to direct connection.

## Verification

### Check Configuration

```bash
# Run the setup script
python setup_supabase_pooler.py

# Or check manually
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('USE_SESSION_POOLER:', os.getenv('USE_SESSION_POOLER'))
print('SUPABASE_POOLER_URL:', os.getenv('SUPABASE_POOLER_URL', 'Not set'))
"
```

### Test Connection

```bash
# Test with the run script (includes connection test)
./run.sh

# Or test directly
python -c "
from database import test_database_connection
result = test_database_connection()
print('Status:', result['status'])
print('Connection Type:', result.get('connection_type', 'unknown'))
"
```

## Troubleshooting

### Common Issues

**1. Session pooler URL not working**
- Verify your project reference ID is correct
- Check if your Supabase project has pooler enabled
- Try the direct connection as fallback

**2. Connection timeouts**
- Session pooler may have different timeout settings
- Check your internet connection
- Verify API key permissions

**3. Authentication errors**
- Ensure your API key has the correct permissions
- Check if RLS (Row Level Security) policies are configured correctly

### Debug Commands

```bash
# Check environment variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
for key in ['SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_POOLER_URL', 'USE_SESSION_POOLER']:
    value = os.getenv(key, 'Not set')
    print(f'{key}: {value[:20]}...' if len(value) > 20 else f'{key}: {value}')
"

# Test both connection types
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

# Test direct connection
os.environ['USE_SESSION_POOLER'] = 'false'
from database import test_database_connection
print('Direct connection:', test_database_connection())

# Test pooler connection
os.environ['USE_SESSION_POOLER'] = 'true'
print('Pooler connection:', test_database_connection())
"
```

## Production Recommendations

For production deployments:

1. **Always use session pooler** (`USE_SESSION_POOLER=true`)
2. **Set connection timeouts** appropriately for your use case
3. **Monitor connection metrics** in Supabase dashboard
4. **Use service role key** for server-side operations
5. **Configure RLS policies** for data security

## Support

If you encounter issues:

1. Run `python setup_supabase_pooler.py` for interactive troubleshooting
2. Check the [Supabase documentation](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
3. Verify your project settings in the Supabase dashboard
4. Test with direct connection first, then enable pooler

---

**Note**: Session pooler is recommended for production use but not required for development. The application will work with either connection method.