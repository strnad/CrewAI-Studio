"""
Discord 알림 모듈 - 범용 알림 처리
"""
import requests
from typing import Optional
from datetime import datetime, timezone, timedelta

from .log_config import LogLevel, DISCORD_WEBHOOK_URL

# 한국시간 타임존 정의
KST = timezone(timedelta(hours=9))

class DiscordNotifier:
    """Discord 웹훅 알림 전송 - 범용 처리"""
    
    def __init__(self):
        self.webhook_url = DISCORD_WEBHOOK_URL
        
    def should_notify_log(self, level: LogLevel) -> bool:
        """로깅 알림 전송 여부 확인"""
        from .log_config import DISCORD_LOG_ALERTS, DISCORD_LOG_LEVELS
        return DISCORD_LOG_ALERTS and level in DISCORD_LOG_LEVELS and bool(self.webhook_url)
    
    def send(self, message: str, level: LogLevel, **kwargs):
        """일반 로그 Discord 전송"""
        if not self.should_notify_log(level):
            return False
            
        try:
            # 색상 설정
            colors = {
                LogLevel.ERROR: 0xFF0000,      # 빨간색
                LogLevel.CRITICAL: 0x9B59B6,   # 보라색
                LogLevel.WARNING: 0xFFFF00,    # 노란색
            }                                    
            
            # 임베드 생성
            embed = {
                "description": message,
                "color": colors.get(level, 0x000000),
                "fields": []
            }
            
            # kwargs를 필드로 추가 (exc_info 제외)
            for key, value in kwargs.items():
                if key != "exc_info" and value:
                    embed["fields"].append({
                        "name": key,
                        "value": str(value)[:1024],  # Discord 제한
                        "inline": True
                    })
            
            # exc_info가 있으면 별도 필드로
            if "exc_info" in kwargs and kwargs["exc_info"]:
                embed["fields"].append({
                    "name": "Stack Trace",
                    "value": f"```{kwargs['exc_info'][:1000]}```",
                    "inline": False
                })
            
            payload = {
                "embeds": [embed]
            }
            
            # 전송
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=2
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            # Discord 전송 실패는 조용히 무시
            # 로깅 시스템이 Discord 때문에 멈추면 안됨
            return False
        
    def send_daily_resource_report(self, report_data: dict):
        """일일 리소스 리포트 Discord 전송 (구조화된 포맷)"""
        from .log_config import DISCORD_RESOURCE_DAILY
        
        if not DISCORD_RESOURCE_DAILY or not self.webhook_url:
            return False
            
        try:
            # 임베드 생성 - 리소스 리포트 전용 스타일
            embed = {
                "title": "일일 리소스 모니터링 리포트",
                "description": f"**수집기간**: {report_data['period']}\n**데이터포인트**: {report_data['data_points']}개 (1분 단위)",
                "color": 0x00FF00,  # 녹색
                "fields": [],
                "timestamp": datetime.now(KST).isoformat(),
                "footer": {
                    "text": f"리소스 모니터링 | 모드: {report_data.get('monitoring_mode', 'SYSTEM')}"
                }
            }
            
            # GPU 정보
            if report_data.get('gpu_memory_percent', 0) > 0:
                gpu_field = f"**메모리**: {report_data['gpu_memory_percent']}% [{report_data['gpu_memory_time']}]\n"
                gpu_field += f"**사용률**: {report_data['gpu_utilization']}% [{report_data['gpu_utilization_time']}]"
                embed["fields"].append({
                    "name": f"GPU #{report_data.get('gpu_index', 0)}",
                    "value": gpu_field,
                    "inline": True
                })
            
            # CPU 정보
            cpu_field = f"**전체**: {report_data['cpu_percent_total']}% [{report_data['cpu_total_time']}]"
            if report_data.get('monitoring_mode') == 'PM2' and report_data.get('cpu_percent_app', 0) > 0:
                cpu_field += f"\n**앱**: {report_data['cpu_percent_app']}% [{report_data['cpu_app_time']}]"
            
            embed["fields"].append({
                "name": "CPU",
                "value": cpu_field,
                "inline": True
            })
            
            # RAM 정보
            ram_field = f"**전체**: {report_data['ram_percent']}% [{report_data['ram_time']}]"
            if report_data.get('monitoring_mode') == 'PM2' and report_data.get('app_memory_peak_mb', 0) > 0:
                app_memory_gb = report_data['app_memory_peak_mb'] / 1024
                ram_field += f"\n**앱**: {app_memory_gb:.1f}GB ({report_data['app_memory_peak_mb']:.0f}MB)"
            
            embed["fields"].append({
                "name": "RAM",
                "value": ram_field,
                "inline": True
            })
            
            # 디스크 정보 (있는 경우만)
            if report_data.get('cache_dir_gb', 0) > 0:
                disk_field = f"{report_data['cache_dir_gb']}GB ({report_data['cache_file_count']:,}개 파일)"
                if report_data.get('cache_size_change_gb', 0) != 0:
                    change_str = f"+{report_data['cache_size_change_gb']}" if report_data['cache_size_change_gb'] > 0 else str(report_data['cache_size_change_gb'])
                    disk_field += f"\n**24시간 변화**: {change_str}GB"
                
                embed["fields"].append({
                    "name": "디스크",
                    "value": disk_field,
                    "inline": False
                })
            
            payload = {
                "embeds": [embed]
            }
            
            # 전송
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            return True
        
        except Exception as e:
            # 전송 실패시 조용히 무시하되, 로깅은 유지
            return False

    def send_threshold_alert(self, violations: str, stats: dict):
        """리소스 임계값 초과 알림 (상세 정보 포함)"""
        from .log_config import DISCORD_RESOURCE_THRESHOLD
        
        if not DISCORD_RESOURCE_THRESHOLD or not self.webhook_url:
            return False
            
        try:
            # 현재 리소스 상태 필드 생성
            fields = []
            
            # GPU 정보
            if stats.get('gpu'):
                gpu_value = f"메모리: {stats['gpu']['memory_percent']}%\n"
                gpu_value += f"사용률: {stats['gpu']['utilization']}%"
                fields.append({
                    "name": "GPU 현황",
                    "value": gpu_value,
                    "inline": True
                })
            
            # CPU 정보
            cpu_value = f"전체: {stats['cpu_percent_total']}%"
            if stats.get('cpu_percent_app', 0) > 0:
                cpu_value += f"\n앱: {stats['cpu_percent_app']}%"
            fields.append({
                "name": "CPU 현황", 
                "value": cpu_value,
                "inline": True
            })
            
            # RAM 정보
            ram_value = f"사용률: {stats['ram_percent']}%"
            if stats.get('app_memory_mb', 0) > 0:
                ram_value += f"\n앱 메모리: {stats['app_memory_mb']:.0f}MB"
            fields.append({
                "name": "RAM 현황",
                "value": ram_value, 
                "inline": True
            })
            
            embed = {
                "title": "리소스 임계값 초과 경고",
                "description": f"**위반 항목**: {violations}\n\n시스템 리소스가 임계값을 초과했습니다.",
                "color": 0xFF0000,  # 빨간색
                "fields": fields,
                "timestamp": datetime.now(KST).isoformat(),
                "footer": {
                    "text": f"다음 알림까지 {stats.get('cooldown_minutes', 60)}분 대기"
                }
            }
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=3
            )
            response.raise_for_status()
            return True
            
        except Exception:
            return False