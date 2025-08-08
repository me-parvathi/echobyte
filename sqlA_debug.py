#!/usr/bin/env python3
"""
sqlalchemy_debug.py
Comprehensive debugging script for SQLAlchemy SQL Server connection issues
"""

import logging
import time
import socket
import subprocess
import sys
from pathlib import Path

import pyodbc
import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.engine import Engine


def setup_detailed_logging():
    """Enable maximum logging detail"""
    # SQLAlchemy engine logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Enable SQLAlchemy logging
    sa_logger = logging.getLogger('sqlalchemy.engine')
    sa_logger.setLevel(logging.INFO)
    
    # Enable pyodbc logging
    pyodbc_logger = logging.getLogger('pyodbc')
    pyodbc_logger.setLevel(logging.DEBUG)
    
    # Enable connection pool logging
    pool_logger = logging.getLogger('sqlalchemy.pool')
    pool_logger.setLevel(logging.DEBUG)
    
    return logging.getLogger(__name__)


def test_network_connectivity(host, port):
    """Test basic network connectivity"""
    logger = logging.getLogger(__name__)
    logger.info(f"=== Testing Network Connectivity to {host}:{port} ===")
    
    try:
        # Test socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        start_time = time.time()
        result = sock.connect_ex((host, port))
        connection_time = time.time() - start_time
        sock.close()
        
        if result == 0:
            logger.info(f"✅ Socket connection successful in {connection_time:.2f}s")
            return True
        else:
            logger.error(f"❌ Socket connection failed with error code: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ Socket connection exception: {e}")
        return False


def test_docker_container(container_name="echobyte-db"):
    """Check Docker container status"""
    logger = logging.getLogger(__name__)
    logger.info(f"=== Checking Docker Container: {container_name} ===")
    
    try:
        # Check if container is running
        result = subprocess.run(['docker', 'ps', '--filter', f'name={container_name}'], 
                              capture_output=True, text=True)
        if container_name in result.stdout:
            logger.info("✅ Container is running")
            
            # Get container details
            inspect_result = subprocess.run(['docker', 'inspect', container_name], 
                                          capture_output=True, text=True)
            logger.debug(f"Container inspect output: {inspect_result.stdout[:500]}...")
            
            # Check port mapping
            port_result = subprocess.run(['docker', 'port', container_name], 
                                       capture_output=True, text=True)
            logger.info(f"Port mappings: {port_result.stdout.strip()}")
            
            # Check container logs
            logs_result = subprocess.run(['docker', 'logs', '--tail', '50', container_name], 
                                       capture_output=True, text=True)
            logger.info(f"Recent container logs:\n{logs_result.stdout}")
            
            return True
        else:
            logger.error("❌ Container is not running")
            return False
    except Exception as e:
        logger.error(f"❌ Docker check failed: {e}")
        return False


def test_odbc_drivers():
    """Test available ODBC drivers"""
    logger = logging.getLogger(__name__)
    logger.info("=== Testing ODBC Drivers ===")
    
    try:
        drivers = pyodbc.drivers()
        logger.info(f"Available ODBC drivers: {drivers}")
        
        sql_server_drivers = [d for d in drivers if 'SQL Server' in d]
        if sql_server_drivers:
            logger.info(f"✅ SQL Server drivers found: {sql_server_drivers}")
            return sql_server_drivers
        else:
            logger.error("❌ No SQL Server ODBC drivers found")
            return []
    except Exception as e:
        logger.error(f"❌ Failed to get ODBC drivers: {e}")
        return []


def test_direct_pyodbc_connection(host, port, user, password, database):
    """Test direct pyodbc connection with detailed logging"""
    logger = logging.getLogger(__name__)
    logger.info("=== Testing Direct pyodbc Connection ===")
    
    drivers_to_test = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server"
    ]
    
    for driver in drivers_to_test:
        logger.info(f"Testing driver: {driver}")
        
        connection_strings = [
            # Basic connection
            f"DRIVER={{{driver}}};SERVER={host},{port};DATABASE={database};UID={user};PWD={password};TrustServerCertificate=yes;",
            # With encryption disabled
            f"DRIVER={{{driver}}};SERVER={host},{port};DATABASE={database};UID={user};PWD={password};TrustServerCertificate=yes;Encrypt=no;",
            # With extended timeouts
            f"DRIVER={{{driver}}};SERVER={host},{port};DATABASE={database};UID={user};PWD={password};TrustServerCertificate=yes;Encrypt=no;LoginTimeout=60;QueryTimeout=60;",
            # With TCP protocol
            f"DRIVER={{{driver}}};SERVER=tcp:{host},{port};DATABASE={database};UID={user};PWD={password};TrustServerCertificate=yes;Encrypt=no;LoginTimeout=60;",
        ]
        
        for i, conn_str in enumerate(connection_strings, 1):
            try:
                logger.info(f"  Attempt {i}: {conn_str}")
                start_time = time.time()
                
                conn = pyodbc.connect(conn_str, timeout=60)
                connection_time = time.time() - start_time
                
                logger.info(f"  ✅ Connection successful in {connection_time:.2f}s")
                
                # Test a simple query
                cursor = conn.cursor()
                cursor.execute("SELECT @@VERSION, GETDATE()")
                result = cursor.fetchone()
                logger.info(f"  Query result: {result[0][:100]}...")
                
                conn.close()
                return driver, conn_str
                
            except Exception as e:
                logger.error(f"  ❌ Connection failed: {e}")
                logger.debug(f"  Full error details:", exc_info=True)
    
    return None, None


def test_sqlalchemy_connection(host, port, user, password, database, working_driver=None):
    """Test SQLAlchemy connection with detailed logging"""
    logger = logging.getLogger(__name__)
    logger.info("=== Testing SQLAlchemy Connection ===")
    
    # Add SQLAlchemy event listeners for detailed logging
    @event.listens_for(Engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        logger.debug(f"Executing SQL: {statement}")
        logger.debug(f"Parameters: {parameters}")
    
    @event.listens_for(Engine, "connect")
    def receive_connect(dbapi_connection, connection_record):
        logger.info("SQLAlchemy connection established")
    
    @event.listens_for(Engine, "checkout")
    def receive_checkout(dbapi_connection, connection_record, connection_proxy):
        logger.debug("Connection checked out from pool")
    
    # Test different connection strings
    connection_strings = []
    
    if working_driver:
        # Use the working driver from pyodbc test
        connection_strings.append(
            f"mssql+pyodbc://{user}:{password}@{host},{port}/{database}"
            f"?driver={working_driver.replace(' ', '+')}"
            f"&TrustServerCertificate=yes&Encrypt=no&LoginTimeout=60"
        )
    
    # Add standard connection strings
    connection_strings.extend([
        f"mssql+pyodbc://{user}:{password}@{host},{port}/{database}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes",
        f"mssql+pyodbc://{user}:{password}@{host},{port}/{database}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=no",
        f"mssql+pyodbc://{user}:{password}@{host}:{port}/{database}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=no&LoginTimeout=60",
    ])
    
    for i, conn_str in enumerate(connection_strings, 1):
        try:
            logger.info(f"SQLAlchemy attempt {i}")
            logger.info(f"Connection string: {conn_str}")
            
            start_time = time.time()
            
            # Create engine with detailed logging
            engine = sa.create_engine(
                conn_str,
                echo=True,  # Log all SQL
                pool_timeout=60,
                pool_recycle=3600,
                connect_args={
                    "timeout": 60,
                    "login_timeout": 60
                }
            )
            
            # Test connection
            with engine.connect() as conn:
                connection_time = time.time() - start_time
                logger.info(f"✅ SQLAlchemy connection successful in {connection_time:.2f}s")
                
                # Test a query
                result = conn.execute(sa.text("SELECT @@VERSION, GETDATE()"))
                row = result.fetchone()
                logger.info(f"Query result: {row[0][:100]}...")
                
                return engine, conn_str
                
        except Exception as e:
            logger.error(f"❌ SQLAlchemy connection {i} failed: {e}")
            logger.debug("Full error details:", exc_info=True)
    
    return None, None


def main():
    """Main debugging function"""
    logger = setup_detailed_logging()
    logger.info("Starting comprehensive SQL Server connection debugging...")
    
    # Connection parameters
    host = "localhost"
    port = 1433
    user = "sa"
    password = "YourStrong!Passw0rd"
    database = "echobyte"
    
    logger.info(f"Target connection: {user}@{host}:{port}/{database}")
    
    # Step 1: Test network connectivity
    network_ok = test_network_connectivity(host, port)
    
    # Step 2: Check Docker container
    docker_ok = test_docker_container()
    
    # Step 3: Test ODBC drivers
    available_drivers = test_odbc_drivers()
    
    # Step 4: Test direct pyodbc connection
    working_driver, working_conn_str = test_direct_pyodbc_connection(host, port, user, password, database)
    
    # Step 5: Test SQLAlchemy connection
    if working_driver:
        logger.info(f"Using working driver for SQLAlchemy test: {working_driver}")
    
    engine, sqlalchemy_conn_str = test_sqlalchemy_connection(host, port, user, password, database, working_driver)
    
    # Summary
    logger.info("=== DEBUGGING SUMMARY ===")
    logger.info(f"Network connectivity: {'✅' if network_ok else '❌'}")
    logger.info(f"Docker container: {'✅' if docker_ok else '❌'}")
    logger.info(f"ODBC drivers available: {len(available_drivers)}")
    logger.info(f"Direct pyodbc connection: {'✅' if working_driver else '❌'}")
    logger.info(f"SQLAlchemy connection: {'✅' if engine else '❌'}")
    
    if working_conn_str:
        logger.info(f"Working pyodbc connection string: {working_conn_str}")
    
    if sqlalchemy_conn_str:
        logger.info(f"Working SQLAlchemy connection string: {sqlalchemy_conn_str}")
    
    if not engine:
        logger.error("❌ No working SQLAlchemy connection found. Check the logs above for details.")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)