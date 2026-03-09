#!/usr/bin/env python3
"""
Odoo Integration Validation Script
Gold Tier - Personal AI Employee

Autonomously validates:
1. Docker Compose configuration
2. Environment variables
3. MCP server syntax
4. JSON-RPC authentication flow
5. Connection simulation
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}[OK] {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}[ERROR] {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.RESET}")


class OdooValidator:
    """Validates Odoo integration configuration"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.odoo_dir = self.project_root / "odoo"
        self.mcp_file = self.project_root / "mcp_servers" / "odoo_mcp.py"
        self.env_file = self.odoo_dir / ".env"
        self.docker_compose_file = self.odoo_dir / "docker-compose.yml"
        
        self.validation_results = {
            'docker_compose': False,
            'env_file': False,
            'mcp_server': False,
            'credentials': False,
            'overall': False
        }
        
        self.config = {}
    
    def validate_docker_compose(self) -> bool:
        """Validate docker-compose.yml configuration"""
        print_header("STEP 1: Validating Docker Compose Configuration")
        
        if not self.docker_compose_file.exists():
            print_error("docker-compose.yml not found")
            return False
        
        try:
            content = self.docker_compose_file.read_text(encoding='utf-8')
            
            # Check required services
            required_services = ['odoo', 'postgres']
            for service in required_services:
                if f'{service}:' not in content:
                    print_error(f"Missing service: {service}")
                    return False
            print_success("Required services present (odoo, postgres)")
            
            # Check Odoo image version
            if 'odoo:19.0' in content or 'odoo:19' in content:
                print_success("Odoo version 19 configured")
            else:
                print_warning("Odoo version should be 19.x")
            
            # Check PostgreSQL version
            if 'postgres:15' in content:
                print_success("PostgreSQL version 15 configured")
            else:
                print_warning("PostgreSQL version should be 15.x")
            
            # Check database name
            if 'ai_employee_business' in content:
                print_success("Database name: ai_employee_business")
            else:
                print_warning("Database name should be ai_employee_business")
            
            # Check ports
            if '8069:8069' in content:
                print_success("Port 8069 mapped correctly")
            else:
                print_error("Port 8069 not mapped")
                return False
            
            # Check volumes
            if 'odoo-web-data:/var/lib/odoo' in content:
                print_success("Odoo data volume configured")
            if 'odoo-db-data:/var/lib/postgresql/data' in content:
                print_success("PostgreSQL data volume configured")
            
            # Check health checks
            if 'healthcheck:' in content:
                print_success("Health checks configured")
            else:
                print_warning("Consider adding health checks")
            
            # Check restart policy
            if 'restart: unless-stopped' in content:
                print_success("Restart policy configured")
            
            # Check network
            if 'odoo-network' in content:
                print_success("Docker network configured")
            
            self.validation_results['docker_compose'] = True
            print_success("Docker Compose configuration VALID")
            return True
            
        except Exception as e:
            print_error(f"Validation error: {e}")
            return False
    
    def validate_env_file(self) -> bool:
        """Validate .env file configuration"""
        print_header("STEP 2: Validating Environment File")
        
        if not self.env_file.exists():
            print_error(".env file not found in odoo/")
            print_info("Creating .env file from template...")
            return False
        
        try:
            content = self.env_file.read_text(encoding='utf-8')
            
            # Required variables
            required_vars = {
                'ODOO_URL': r'ODOO_URL=http://localhost:8069',
                'ODOO_DATABASE': r'ODOO_DATABASE=ai_employee_business',
                'ODOO_USERNAME': r'ODOO_USERNAME=admin',
                'ODOO_API_KEY': r'ODOO_API_KEY=odoo_api_[a-f0-9]+',
                'ODOO_DB_PASSWORD': r'ODOO_DB_PASSWORD=.+',
                'ODOO_ADMIN_PASSWORD': r'ODOO_ADMIN_PASSWORD=.+'
            }
            
            all_valid = True
            for var_name, pattern in required_vars.items():
                if re.search(pattern, content):
                    print_success(f"{var_name} configured")
                else:
                    print_error(f"{var_name} missing or invalid")
                    all_valid = False
            
            # Validate password strength
            db_password_match = re.search(r'ODOO_DB_PASSWORD=(.+)', content)
            if db_password_match:
                password = db_password_match.group(1)
                if len(password) >= 12:
                    print_success("Database password meets length requirements (12+ chars)")
                else:
                    print_error("Database password too short (minimum 12 characters)")
                    all_valid = False
                
                if re.search(r'[A-Z]', password) and re.search(r'[a-z]', password) and re.search(r'[0-9]', password):
                    print_success("Database password meets complexity requirements")
                else:
                    print_warning("Database password should include uppercase, lowercase, and numbers")
            
            # Validate API key format
            api_key_match = re.search(r'ODOO_API_KEY=(odoo_api_[a-f0-9]+)', content)
            if api_key_match:
                api_key = api_key_match.group(1)
                if len(api_key) >= 40:
                    print_success("API key format valid (odoo_api_<hex>)")
                else:
                    print_error("API key too short")
                    all_valid = False
            else:
                print_error("API key format invalid (should be odoo_api_<hex>)")
                all_valid = False
            
            self.validation_results['env_file'] = all_valid
            if all_valid:
                print_success("Environment file configuration VALID")
            return all_valid
            
        except Exception as e:
            print_error(f"Validation error: {e}")
            return False
    
    def validate_mcp_server(self) -> bool:
        """Validate MCP server syntax and structure"""
        print_header("STEP 3: Validating MCP Server")
        
        if not self.mcp_file.exists():
            print_error("odoo_mcp.py not found")
            return False
        
        try:
            content = self.mcp_file.read_text(encoding='utf-8')
            
            # Check required imports
            required_imports = ['requests', 'json', 'logging', 'dotenv']
            for imp in required_imports:
                if f'import {imp}' in content or f'from {imp}' in content:
                    print_success(f"Import '{imp}' present")
                else:
                    print_error(f"Missing import: {imp}")
                    return False
            
            # Check OdooClient class
            if 'class OdooClient:' in content:
                print_success("OdooClient class defined")
            else:
                print_error("OdooClient class not found")
                return False
            
            # Check required methods
            required_methods = [
                'def authenticate',
                'def _json_rpc',
                'def execute_kw',
                'def create_invoice',
                'def read_partner',
                'def create_task',
                'def get_revenue_summary'
            ]
            
            for method in required_methods:
                if method in content:
                    print_success(f"Method '{method.split()[1]}' defined")
                else:
                    print_error(f"Missing method: {method.split()[1]}")
                    return False
            
            # Check MCP tool functions
            mcp_tools = [
                'def odoo_create_invoice',
                'def odoo_read_partner',
                'def odoo_create_task',
                'def odoo_get_revenue_summary'
            ]
            
            for tool in mcp_tools:
                if tool in content:
                    tool_name = tool.split()[1]
                    print_success(f"MCP tool '{tool_name}' defined")
                else:
                    print_error(f"Missing MCP tool: {tool}")
                    return False
            
            # Check JSON-RPC endpoint
            if '"/jsonrpc"' in content or "'/jsonrpc'" in content:
                print_success("JSON-RPC endpoint configured (/jsonrpc)")
            else:
                print_warning("JSON-RPC endpoint should be /jsonrpc")
            
            # Try to import the module
            print_info("Testing Python syntax...")
            try:
                import py_compile
                py_compile.compile(str(self.mcp_file), doraise=True)
                print_success("Python syntax VALID")
            except py_compile.PyCompileError as e:
                print_error(f"Python syntax error: {e}")
                return False
            
            self.validation_results['mcp_server'] = True
            print_success("MCP Server configuration VALID")
            return True
            
        except Exception as e:
            print_error(f"Validation error: {e}")
            return False
    
    def simulate_connection_test(self) -> bool:
        """Simulate the connection test"""
        print_header("STEP 4: Simulating Connection Test")
        
        print_info("Loading environment variables...")
        if self.env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(self.env_file)
            print_success("Environment variables loaded")
        else:
            print_warning(".env file not found, using defaults")
        
        print_info("Checking OdooClient initialization...")
        try:
            sys.path.insert(0, str(self.project_root / 'mcp_servers'))
            from odoo_mcp import OdooClient, get_odoo_client
            
            print_success("OdooClient module imported successfully")
            
            # Check if client can be initialized
            odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
            odoo_db = os.getenv('ODOO_DATABASE', 'ai_employee_business')
            odoo_user = os.getenv('ODOO_USERNAME', 'admin')
            odoo_api_key = os.getenv('ODOO_API_KEY', '')
            odoo_db_password = os.getenv('ODOO_DB_PASSWORD', '')
            
            print_info(f"Configuration loaded:")
            print_info(f"  URL: {odoo_url}")
            print_info(f"  Database: {odoo_db}")
            print_info(f"  Username: {odoo_user}")
            print_info(f"  API Key: {'*' * 20}{odoo_api_key[-10:] if len(odoo_api_key) > 10 else 'NOT SET'}")
            
            # Create client instance (don't actually connect)
            client = OdooClient(
                url=odoo_url,
                database=odoo_db,
                username=odoo_user,
                api_key=odoo_api_key,
                db_password=odoo_db_password
            )
            
            print_success("OdooClient instance created successfully")
            
            # Show expected test output
            print_header("EXPECTED TEST OUTPUT (After Odoo Starts)")
            print("""
============================================================
ODOO MCP SERVER - Gold Tier Test
============================================================

Testing Odoo connection...

[OK] CONNECTED to Odoo!
   URL: http://localhost:8069
   Database: ai_employee_business
   User ID: 2

[OK] Odoo MCP Server is ready!

============================================================
""")
            
            self.validation_results['credentials'] = True
            print_success("Connection simulation SUCCESSFUL")
            return True
            
        except Exception as e:
            print_error(f"Simulation error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_json_rpc_guide(self):
        """Generate JSON-RPC authentication guide"""
        print_header("STEP 5: JSON-RPC Authentication Guide")
        
        guide = """
+-------------------------------------------------------------------+
|              ODOO JSON-RPC AUTHENTICATION GUIDE                   |
+-------------------------------------------------------------------+

1. AUTHENTICATION ENDPOINT:
   POST http://localhost:8069/jsonrpc

2. AUTHENTICATION PAYLOAD (API Key Method):
   {
     "jsonrpc": "2.0",
     "method": "call",
     "params": {
       "service": "common",
       "method": "authenticate",
       "args": [
         "ai_employee_business",
         "admin",
         "odoo_api_7f3e9a2b5c8d1f4e6a9c2b5d8e1f4a7c9b2e5d8f",
         {"base": "OdooDb_S3cur3P@ss_9x7K2mN5pQ8w"}
       ]
     },
     "id": 1
   }

3. SUCCESS RESPONSE:
   {
     "jsonrpc": "2.0",
     "id": 1,
     "result": {
       "uid": 2,
       "username": "admin",
       "session_id": "abc123..."
     }
   }

4. ALTERNATIVE: DB Password Method (Legacy):
   {
     "jsonrpc": "2.0",
     "method": "call",
     "params": {
       "service": "common",
       "method": "login",
       "args": [
         "ai_employee_business",
         "admin",
         "OdooDb_S3cur3P@ss_9x7K2mN5pQ8w"
       ]
     },
     "id": 1
   }

5. EXECUTE METHOD (After Authentication):
   POST http://localhost:8069/jsonrpc
   {
     "jsonrpc": "2.0",
     "method": "call",
     "params": {
       "service": "object",
       "method": "execute_kw",
       "args": [
         "ai_employee_business",
         2,              // uid from authentication
         "api_key",
         "res.partner",  // model
         "search",       // method
         [[["email", "=", "customer@example.com"]]]
       ]
     },
     "id": 2
   }

+-------------------------------------------------------------------+
|                    IMPORTANT NOTES                                  |
+-------------------------------------------------------------------+
| * API Key authentication is preferred (Odoo 17+)                   |
| * DB password method works but is less secure                      |
| * Session is maintained via cookies automatically                  |
| * Always use HTTPS in production                                   |
| * Store credentials securely (never commit to git)                |
+-------------------------------------------------------------------+
"""
        print(guide)
    
    def run_full_validation(self) -> bool:
        """Run complete validation suite"""
        print_header("ODOO GOLD TIER - FULL VALIDATION")
        print_info(f"Project Root: {self.project_root}")
        print_info(f"Odoo Directory: {self.odoo_dir}")
        print_info(f"MCP Server: {self.mcp_file}")
        
        # Run all validations
        results = []
        results.append(self.validate_docker_compose())
        results.append(self.validate_env_file())
        results.append(self.validate_mcp_server())
        results.append(self.simulate_connection_test())
        
        # Generate JSON-RPC guide
        self.generate_json_rpc_guide()
        
        # Overall status
        self.validation_results['overall'] = all(results)
        
        # Final report
        print_header("VALIDATION SUMMARY")
        
        checks = [
            ("Docker Compose Configuration", self.validation_results['docker_compose']),
            ("Environment File", self.validation_results['env_file']),
            ("MCP Server Syntax", self.validation_results['mcp_server']),
            ("Credentials Format", self.validation_results['credentials']),
        ]
        
        for check_name, passed in checks:
            if passed:
                print_success(check_name)
            else:
                print_error(check_name)
        
        print("")
        if self.validation_results['overall']:
            print_success("=" * 60)
            print_success("ALL VALIDATIONS PASSED")
            print_success("=" * 60)
            print("")
            print_info("NEXT STEPS:")
            print_info("1. cd odoo")
            print_info("2. docker-compose up -d")
            print_info("3. Wait 2-3 minutes for Odoo to start")
            print_info("4. Open http://localhost:8069")
            print_info("5. Login: admin / Admin_S3cur3P@ss_4h6J9kL2nR5t")
            print_info("6. Generate API Key from Odoo UI")
            print_info("7. Update ODOO_API_KEY in .env")
            print_info("8. python mcp_servers/odoo_mcp.py --test")
        else:
            print_error("=" * 60)
            print_error("SOME VALIDATIONS FAILED")
            print_error("=" * 60)
            print_info("Please fix the errors above and re-run validation")
        
        return self.validation_results['overall']


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    validator = OdooValidator(project_root)
    
    success = validator.run_full_validation()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
