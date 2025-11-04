"""
Database backup and restore endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import subprocess
import os
from datetime import datetime
from pathlib import Path

from app.core.database import get_db
from app.core.auth import require_auth, require_role
from app.models.user import User, UserRole
from app.core.config import settings

router = APIRouter()

# Backup directory - use /tmp/backups for local development, /app/backups for Docker
BACKUP_DIR = Path("/app/backups") if os.path.exists("/app") else Path("/tmp/backups")
BACKUP_DIR.mkdir(exist_ok=True, parents=True)


@router.get("/info")
def get_database_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Get database information and statistics"""
    
    
    try:
        # Get database size
        result = db.execute(text("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as db_size,
                   pg_database_size(current_database()) as db_size_bytes
        """))
        db_info = result.fetchone()
        
        # Get table sizes
        result = db.execute(text("""
            SELECT 
                schemaname as schema,
                tablename as table_name,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """))
        tables = [dict(row._mapping) for row in result.fetchall()]  # type: ignore
        
        # Get row counts
        table_counts = {}
        for table in tables:
            result = db.execute(text(f"SELECT COUNT(*) as count FROM {table['table_name']}"))
            count = result.scalar()
            table_counts[table['table_name']] = count
        
        # List available backups
        backups = []
        if BACKUP_DIR.exists():
            for backup_file in sorted(BACKUP_DIR.glob("*.sql"), reverse=True):
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "size": stat.st_size,
                    "size_pretty": f"{stat.st_size / (1024*1024):.2f} MB",
                    "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
        
        return {
            "database_name": settings.POSTGRES_DB,
            "database_size": db_info.db_size if db_info else "Unknown",
            "database_size_bytes": db_info.db_size_bytes if db_info else 0,
            "tables": tables,
            "table_counts": table_counts,
            "total_tables": len(tables),
            "available_backups": backups,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database info: {str(e)}"
        )


@router.post("/backup/full")
def create_full_backup(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Create a complete database backup"""
    
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"full_backup_{timestamp}.sql"
    backup_path = BACKUP_DIR / backup_filename
    
    try:
        # Run pg_dump to create backup
        cmd = [
            "pg_dump",
            "-h", settings.POSTGRES_SERVER,
            "-p", str(settings.POSTGRES_PORT),
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-F", "p",  # Plain SQL format
            "-f", str(backup_path),
        ]
        
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            raise Exception(f"pg_dump failed: {result.stderr}")
        
        # Get backup size
        backup_size = backup_path.stat().st_size
        
        return {
            "success": True,
            "message": "Full database backup created successfully",
            "backup_filename": backup_filename,
            "backup_size": backup_size,
            "backup_size_pretty": f"{backup_size / (1024*1024):.2f} MB",
            "created_at": datetime.now().isoformat(),
        }
    except subprocess.TimeoutExpired:
        if backup_path.exists():
            backup_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Backup operation timed out"
        )
    except Exception as e:
        if backup_path.exists():
            backup_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create backup: {str(e)}"
        )


@router.post("/backup/selective")
def create_selective_backup(
    tables: List[str],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Create a selective backup of specific tables"""
    
    
    if not tables:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one table must be specified"
        )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tables_str = "_".join(tables[:3])  # Use first 3 table names in filename
    if len(tables) > 3:
        tables_str += f"_and_{len(tables)-3}_more"
    backup_filename = f"selective_backup_{tables_str}_{timestamp}.sql"
    backup_path = BACKUP_DIR / backup_filename
    
    try:
        # Verify tables exist
        result = db.execute(text("""
            SELECT tablename FROM pg_tables WHERE schemaname = 'public'
        """))
        available_tables = [row.tablename for row in result.fetchall()]
        
        invalid_tables = [t for t in tables if t not in available_tables]
        if invalid_tables:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tables: {', '.join(invalid_tables)}"
            )
        
        # Run pg_dump with table selection
        cmd = [
            "pg_dump",
            "-h", settings.POSTGRES_SERVER,
            "-p", str(settings.POSTGRES_PORT),
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-F", "p",  # Plain SQL format
        ]
        
        # Add each table
        for table in tables:
            cmd.extend(["-t", table])
        
        cmd.extend(["-f", str(backup_path)])
        
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            raise Exception(f"pg_dump failed: {result.stderr}")
        
        backup_size = backup_path.stat().st_size
        
        return {
            "success": True,
            "message": f"Selective backup created for {len(tables)} tables",
            "backup_filename": backup_filename,
            "tables": tables,
            "backup_size": backup_size,
            "backup_size_pretty": f"{backup_size / (1024*1024):.2f} MB",
            "created_at": datetime.now().isoformat(),
        }
    except subprocess.TimeoutExpired:
        if backup_path.exists():
            backup_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Backup operation timed out"
        )
    except HTTPException:
        raise
    except Exception as e:
        if backup_path.exists():
            backup_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create selective backup: {str(e)}"
        )


@router.get("/backup/download/{filename}")
def download_backup(
    filename: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Download a backup file"""
    
    
    # Security: Only allow SQL files and prevent path traversal
    if not filename.endswith(".sql") or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )
    
    backup_path = BACKUP_DIR / filename
    
    if not backup_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup file not found"
        )
    
    return FileResponse(
        path=str(backup_path),
        filename=filename,
        media_type="application/sql"
    )


@router.delete("/backup/{filename}")
def delete_backup(
    filename: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Delete a backup file"""
    
    
    # Security: Only allow SQL files and prevent path traversal
    if not filename.endswith(".sql") or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )
    
    backup_path = BACKUP_DIR / filename
    
    if not backup_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup file not found"
        )
    
    try:
        backup_path.unlink()
        return {
            "success": True,
            "message": f"Backup {filename} deleted successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete backup: {str(e)}"
        )


@router.post("/restore/{filename}")
def restore_from_backup(
    filename: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Restore database from backup file (CAUTION: This will overwrite existing data)"""
    
    
    # Security: Only allow SQL files and prevent path traversal
    if not filename.endswith(".sql") or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )
    
    backup_path = BACKUP_DIR / filename
    
    if not backup_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup file not found"
        )
    
    try:
        # Run psql to restore backup
        cmd = [
            "psql",
            "-h", settings.POSTGRES_SERVER,
            "-p", str(settings.POSTGRES_PORT),
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-f", str(backup_path),
        ]
        
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for restore
        )
        
        if result.returncode != 0:
            raise Exception(f"psql restore failed: {result.stderr}")
        
        return {
            "success": True,
            "message": f"Database restored successfully from {filename}",
            "restored_at": datetime.now().isoformat(),
            "warnings": result.stderr if result.stderr else None,
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Restore operation timed out"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restore from backup: {str(e)}"
        )


@router.get("/tables")
def list_tables(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """List all database tables"""
    
    
    try:
        result = db.execute(text("""
            SELECT 
                tablename as name,
                pg_size_pretty(pg_total_relation_size('public.'||tablename)) as size
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """))
        
        tables = [dict(row._mapping) for row in result.fetchall()]  # type: ignore
        
        # Get row counts
        for table in tables:
            result = db.execute(text(f"SELECT COUNT(*) as count FROM {table['name']}"))
            table['row_count'] = result.scalar()
        
        return {
            "tables": tables,
            "total_count": len(tables),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tables: {str(e)}"
        )
