from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from app.api import deps
from app.models import SystemSettings
from app.config import get_settings
import shutil
import platform
import subprocess
import os

router = APIRouter()

@router.post("/diagnosis/check")
async def check_system_status(
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_admin_user)
):
    results = {
        "health_checks": [],
        "config_audit": [],
        "limit_matrix": {}
    }

    # 1. Health Checks
    # ----------------
    
    # DB Check
    try:
        await db.execute(text("SELECT 1"))
        results["health_checks"].append({
            "name": "Database", 
            "status": "pass", 
            "message": "Connection successful",
            "message_key": "admin.systemStatus.dbSuccess",
            "name_key": "admin.systemStatus.names.database"
        })
    except Exception as e:
        results["health_checks"].append({
            "name": "Database", 
            "status": "fail", 
            "message": str(e),
            "message_key": "admin.systemStatus.dbFail",
            "message_params": {"error": str(e)},
            "name_key": "admin.systemStatus.names.database"
        })

    # FFmpeg Check
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        # Try running ffmpeg -version
        try:
            cmd = [ffmpeg_path, "-version"]
            # Minimal output capture
            if platform.system() == 'Windows':
                 # prevent window popup on windows
                 si = subprocess.STARTUPINFO()
                 si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                 subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=si, check=True)
            else:
                 subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
            results["health_checks"].append({
                "name": "FFmpeg", 
                "status": "pass", 
                "message": f"Installed at {ffmpeg_path}",
                "message_key": "admin.systemStatus.ffmpegInstalled",
                "message_params": {"path": ffmpeg_path},
                "name_key": "admin.systemStatus.names.ffmpeg"
            })
        except Exception as e:
             results["health_checks"].append({
                 "name": "FFmpeg", 
                 "status": "fail", 
                 "message": f"Found but execution failed: {str(e)}",
                 "message_key": "admin.systemStatus.ffmpegFail",
                 "message_params": {"error": str(e)},
                 "name_key": "admin.systemStatus.names.ffmpeg"
             })
    else:
        results["health_checks"].append({
            "name": "FFmpeg", 
            "status": "fail", 
            "message": "Not found in PATH",
            "message_key": "admin.systemStatus.ffmpegNotFound",
            "name_key": "admin.systemStatus.names.ffmpeg"
        })

    # Storage Check
    # Instantiates the configured storage backend (Local, S3, OSS, COS) and tests write capability
    try:
        from app.services.storage import get_storage_backend_async
        storage = await get_storage_backend_async()
        
        # Determine test filename
        import uuid
        test_filename = f"diagnosis_test_{uuid.uuid4().hex[:8]}.txt"
        test_content = b"health_check"
        
        # Test Save
        # Local storage saves to uploads/..., cloud saves to configured prefix
        # We'll use a specific diagnosis prefix if possible, but base save usually handles it.
        # save() signature: content, filename, date_path=None
        # We pass None for date_path to keep it in root or default folder
        saved_path = await storage.save(test_content, test_filename, date_path="diagnosis")
        
        # Test Delete
        try:
            # We need to determine the filename to delete. 
            # save() returns filepath relative to storage root (e.g. diagnosis/2025/...), 
            # but delete() usually takes exactly that.
            
            # Note: Some backends might return full URL or different format, 
            # ideally delete/save are symmetric.
            # LocalStorage.save returns relative path.
            # S3CompatibleStorage.save returns key (path).
            
            await storage.delete(saved_path)
            
            msg_key = "admin.systemStatus.storageSuccess"
            msg = f"Write/Delete test successful on {storage.storage_type.upper()}"
            status = "pass"
            params = {"type": storage.storage_type.upper()}
            
        except Exception as delete_err:
             msg_key = "admin.systemStatus.storageWriteOnly" # New key needed? Or reuse fail with detail
             msg = f"Write specific success, but Delete failed: {delete_err}"
             status = "warning" # Partial success
             params = {"error": str(delete_err)}
        
        results["health_checks"].append({
            "name": f"{storage.storage_type.upper()} Storage", 
            "status": status, 
            "message": msg,
            "message_key": msg_key,
            "message_params": params,
            "name_key": "admin.systemStatus.names.storage",
            "name_params": {"type": storage.storage_type.upper()}
        })

    except Exception as e:
        # Fallback to identify what type we tried
        try:
            from app.config import get_settings
            st_type = get_settings().storage_type
        except:
            st_type = "UNKNOWN"
            
        results["health_checks"].append({
            "name": f"{st_type.upper()} Storage", 
            "status": "fail", 
            "message": f"Storage check failed: {str(e)}",
            "message_key": "admin.systemStatus.storageFail",
            "message_params": {"error": str(e), "type": st_type.upper()},
            "name_key": "admin.systemStatus.names.storage",
            "name_params": {"type": st_type.upper()}
        })


    # 2. Limit Matrix & Config Audit
    # ----------------------------
    
    # helper to check hierarchy
    def audit_hierarchy(guest, user, vip, metric_name, type_name):
        audit_logs = []
        if guest > user:
             audit_logs.append({
                 "level": "warning", 
                 "message": f"[{type_name}] Guest {metric_name} ({guest}) is greater than User ({user})",
                 "message_key": "admin.systemStatus.auditGuestUser",
                 "message_params": {"type": type_name, "metric": metric_name, "guest": guest, "user": user}
             })
        if user > vip:
             audit_logs.append({
                 "level": "warning", 
                 "message": f"[{type_name}] User {metric_name} ({user}) is greater than VIP ({vip})",
                 "message_key": "admin.systemStatus.auditUserVip",
                 "message_params": {"type": type_name, "metric": metric_name, "user": user, "vip": vip}
             })
        return audit_logs

    # Load all settings
    settings_result = await db.execute(select(SystemSettings))
    all_settings = settings_result.scalars().all()
    settings_map = {s.key: s.value for s in all_settings}
    
    # Helper to safe get int
    def get_int(key, default=0):
        try:
            return int(settings_map.get(key, default))
        except:
            return default

    # Matrix Data Construction
    matrix = {
        "image": {
            "size": {"guest": get_int("upload_max_size_guest"), "user": get_int("upload_max_size_user"), "vip": get_int("upload_max_size_vip", 50*1024*1024)}, # VIP default fallback
            "rate_hour": {"guest": get_int("security_rate_limit_guest_per_hour"), "user": get_int("security_rate_limit_user_per_hour"), "vip": get_int("security_rate_limit_vip_per_hour")}
        },
        "video": {
            "size": {"guest": get_int("upload_video_max_size_guest"), "user": get_int("upload_video_max_size_user"), "vip": get_int("upload_video_max_size_vip")},
            "rate_hour": {"guest": get_int("security_rate_limit_guest_video_per_hour"), "user": get_int("security_rate_limit_user_video_per_hour"), "vip": get_int("security_rate_limit_vip_video_per_hour")}
        },
        "file": {
             # Note: Using assumed keys based on previous analysis. If implementation plan used different keys, update here.
             # Earlier we noted that 'upload_file_max_size_guest' might not be in init.sql but logic in Home.vue assumes it.
             # We will read what is there.
            "size": {"guest": get_int("upload_file_max_size_guest"), "user": get_int("upload_file_max_size_user"), "vip": get_int("upload_file_max_size_vip")},
            "rate_hour": {"guest": get_int("security_rate_limit_guest_file_per_hour"), "user": get_int("security_rate_limit_user_file_per_hour"), "vip": get_int("security_rate_limit_vip_file_per_hour")}
        }
    }
    
    results["limit_matrix"] = matrix

    # Run Logic Audits
    # Image Size
    results["config_audit"].extend(audit_hierarchy(matrix["image"]["size"]["guest"], matrix["image"]["size"]["user"], matrix["image"]["size"]["vip"], "Upload Size", "Image"))
    # Image Rate
    results["config_audit"].extend(audit_hierarchy(matrix["image"]["rate_hour"]["guest"], matrix["image"]["rate_hour"]["user"], matrix["image"]["rate_hour"]["vip"], "Rate Limit", "Image"))
    
    # Video Size
    results["config_audit"].extend(audit_hierarchy(matrix["video"]["size"]["guest"], matrix["video"]["size"]["user"], matrix["video"]["size"]["vip"], "Upload Size", "Video"))
    # Video Rate
    results["config_audit"].extend(audit_hierarchy(matrix["video"]["rate_hour"]["guest"], matrix["video"]["rate_hour"]["user"], matrix["video"]["rate_hour"]["vip"], "Rate Limit", "Video"))
    
    # File Size
    results["config_audit"].extend(audit_hierarchy(matrix["file"]["size"]["guest"], matrix["file"]["size"]["user"], matrix["file"]["size"]["vip"], "Upload Size", "File"))
    # File Rate
    results["config_audit"].extend(audit_hierarchy(matrix["file"]["rate_hour"]["guest"], matrix["file"]["rate_hour"]["user"], matrix["file"]["rate_hour"]["vip"], "Rate Limit", "File"))

    # Check for empty or zero limits where they shouldn't be
    for type_name, metrics in matrix.items():
        for metric, roles in metrics.items():
            for role, val in roles.items():
                if val == 0:
                     # 0 might mean unlimited or disabled? Usually it's a misconfiguration for size unless explicitly intended.
                     # We'll log an info/warning.
                     results["config_audit"].append({
                         "level": "info", 
                         "message": f"[{type_name}] {role} {metric} is set to 0 (Configured? or Missing?)",
                         "message_key": "admin.systemStatus.auditZero",
                         "message_params": {"type": type_name, "role": role, "metric": metric}
                     })

    return results
