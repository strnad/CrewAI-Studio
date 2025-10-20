"""
리소스 모니터링 모듈
CommonLogger와 통합된 백그라운드 리소스 모니터링
"""
import asyncio
import psutil
import subprocess
import json
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional
from pathlib import Path


class ResourceMonitor:
    def __init__(self, logger_instance):
        # Logger 인스턴스 주입
        self.logger = logger_instance
        
        # 설정값 import
        from .log_config import (
            RESOURCE_GPU_INDEX, RESOURCE_PM2_APP_NAME, RESOURCE_CACHE_DIR,
            RESOURCE_DAILY_REPORT_TIME, RESOURCE_THRESHOLD_ALERT,
            RESOURCE_GPU_THRESHOLD, RESOURCE_CPU_THRESHOLD, RESOURCE_RAM_THRESHOLD,
            RESOURCE_COLLECT_INTERVAL, RESOURCE_AGGREGATE_INTERVAL, 
            RESOURCE_THRESHOLD_CHECK_INTERVAL,
            RESOURCE_THRESHOLD_COOLDOWN_MINUTES
        )
        
        # 설정 변수들
        self.gpu_index = RESOURCE_GPU_INDEX
        self.pm2_app_name = RESOURCE_PM2_APP_NAME
        self.cache_dir = RESOURCE_CACHE_DIR
        self.daily_report_time = RESOURCE_DAILY_REPORT_TIME
        self.threshold_alert = RESOURCE_THRESHOLD_ALERT
        self.thresholds = {
            'gpu_memory': RESOURCE_GPU_THRESHOLD,
            'gpu_util': RESOURCE_GPU_THRESHOLD,
            'cpu_total': RESOURCE_CPU_THRESHOLD,
            'cpu_app': RESOURCE_CPU_THRESHOLD, 
            'ram': RESOURCE_RAM_THRESHOLD
        }
        self.collect_interval = RESOURCE_COLLECT_INTERVAL
        self.aggregate_interval = RESOURCE_AGGREGATE_INTERVAL
        self.threshold_check_interval = RESOURCE_THRESHOLD_CHECK_INTERVAL
        self.threshold_cooldown_minutes = RESOURCE_THRESHOLD_COOLDOWN_MINUTES
        
        # 상태 변수들
        self.is_running = False
        self.pm2_available = self._check_pm2_available()
        self.app_pid = None
        self.app_process = None
        self.minute_buffer = []  # 1분간의 초 단위 데이터
        self.minute_peaks = []   # 1분 단위 피크값 저장
        self.last_report_time = datetime.now()
        self.last_threshold_alerts = {}  # 중복 방지용 {리소스타입: 마지막알림시간}
        
        # 모니터링 모드 결정
        if self.pm2_available and self.pm2_app_name:
            self.monitoring_mode = "PM2"
            self._update_app_process()
        else:
            self.monitoring_mode = "SYSTEM"
            
        self.logger.info("리소스 모니터 초기화", 
                        mode=self.monitoring_mode,
                        pm2_app=self.pm2_app_name,
                        gpu_index=self.gpu_index)

    def _check_pm2_available(self) -> bool:
        """PM2 설치 여부 확인"""
        try:
            result = subprocess.run(["pm2", "--version"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, 
                                  text=True)
            return result.returncode == 0
        except:
            return False

    def _get_pm2_pid(self):
        """PM2 앱의 PID 가져오기"""
        if not self.pm2_available:
            return None
        
        try:
            result = subprocess.run(["pm2", "jlist"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, 
                                  text=True)
            pm2_list = json.loads(result.stdout)
            
            for app in pm2_list:
                if app.get("name") == self.pm2_app_name:
                    return app.get("pid")
            return None
        except Exception as e:
            self.logger.error("PM2 PID 찾기 실패", error=str(e))
            return None

    def _update_app_process(self):
        """PM2 앱 프로세스 업데이트"""
        if not self.pm2_available:
            return
        
        new_pid = self._get_pm2_pid()
        if new_pid and new_pid != self.app_pid:
            self.app_pid = new_pid
            try:
                self.app_process = psutil.Process(new_pid)
                self.logger.debug("PM2 프로세스 업데이트", 
                                pid=new_pid, 
                                app_name=self.pm2_app_name)
            except:
                self.app_process = None

    def _get_directory_size_fast(self, path: str) -> Dict:
        """du 명령어로 빠르게 디렉토리 크기 확인"""
        if not path:
            return {'exists': False, 'size_gb': 0, 'file_count': 0}
            
        try:
            # du -sb로 바이트 단위 크기 확인
            result = subprocess.run(
                ['du', '-sb', path], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                size_bytes = int(result.stdout.split()[0])
                
                # 파일 개수 확인
                count_result = subprocess.run(
                    ['find', path, '-type', 'f', '-printf', '.'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                file_count = len(count_result.stdout) if count_result.returncode == 0 else 0
                
                return {
                    'exists': True,
                    'size_gb': round(size_bytes / (1024**3), 2),
                    'file_count': file_count
                }
        except Exception as e:
            self.logger.debug("디렉토리 크기 확인 실패", path=path, error=str(e))
            
        return {'exists': False, 'size_gb': 0, 'file_count': 0}

    async def _get_stats_quick(self) -> Optional[Dict]:
        """GPU + CPU + RAM 상태를 빠르게 수집"""
        try:
            # GPU 상태 (nvidia-smi)
            gpu_cmd = [
                'nvidia-smi', 
                '--query-gpu=memory.used,memory.total,utilization.gpu',
                '--format=csv,noheader,nounits',
                f'--id={self.gpu_index}'
            ]
            
            gpu_result = subprocess.run(gpu_cmd, capture_output=True, text=True, timeout=3)
            gpu_stats = None
            
            if gpu_result.returncode == 0:
                values = gpu_result.stdout.strip().split(', ')
                if len(values) == 3:
                    memory_used = float(values[0]) / 1024  # MB to GB
                    memory_total = float(values[1]) / 1024
                    gpu_stats = {
                        'memory_used_gb': round(memory_used, 2),
                        'memory_total_gb': round(memory_total, 2),
                        'memory_percent': round((memory_used / memory_total) * 100, 1),
                        'utilization': float(values[2])
                    }

            # CPU와 RAM (psutil)
            cpu_percent_total = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()
            
            # PM2 앱 CPU 사용량
            app_cpu_percent = 0
            app_memory_mb = 0
            if self.monitoring_mode == "PM2" and self.app_process:
                try:
                    app_cpu_percent = self.app_process.cpu_percent(interval=0.1)
                    app_memory_mb = self.app_process.memory_info().rss / (1024 * 1024)
                except psutil.NoSuchProcess:
                    # 프로세스가 종료된 경우 재시도
                    self._update_app_process()
                    if self.app_process:
                        try:
                            app_cpu_percent = self.app_process.cpu_percent(interval=0.1)
                            app_memory_mb = self.app_process.memory_info().rss / (1024 * 1024)
                        except:
                            app_cpu_percent = 0
                            app_memory_mb = 0

            # 디렉토리 크기 (설정된 경우만)
            cache_stats = {'exists': False, 'size_gb': 0, 'file_count': 0}
            if self.cache_dir:
                cache_stats = self._get_directory_size_fast(self.cache_dir)

            return {
                'timestamp': datetime.now().isoformat(),
                'gpu': gpu_stats,
                'cpu_percent_total': round(cpu_percent_total, 1),
                'cpu_percent_app': round(app_cpu_percent, 1),
                'app_memory_mb': round(app_memory_mb, 1),
                'app_pid': self.app_pid,
                'ram_used_gb': round(ram.used / (1024**3), 2),
                'ram_total_gb': round(ram.total / (1024**3), 2),
                'ram_percent': round(ram.percent, 1),
                'cache_dir': cache_stats
            }
            
        except Exception as e:
            self.logger.error("Stats 수집 오류", error=str(e))
            return None

    def _check_thresholds(self, stats: Dict) -> bool:
        """임계값 초과 여부 확인 (중복 방지 포함)"""
        if not self.threshold_alert or not stats:
            return False
            
        violations = []
        current_time = datetime.now()
        cooldown_delta = timedelta(minutes=self.threshold_cooldown_minutes)
        
        # GPU 메모리 체크
        if stats.get('gpu') and stats['gpu']['memory_percent'] > self.thresholds['gpu_memory']:
            if self._should_alert('gpu_memory', current_time, cooldown_delta):
                violations.append(f"GPU메모리 {stats['gpu']['memory_percent']}%")
                self.last_threshold_alerts['gpu_memory'] = current_time
                
        # GPU 사용률 체크  
        if stats.get('gpu') and stats['gpu']['utilization'] > self.thresholds['gpu_util']:
            if self._should_alert('gpu_util', current_time, cooldown_delta):
                violations.append(f"GPU사용률 {stats['gpu']['utilization']}%")
                self.last_threshold_alerts['gpu_util'] = current_time
                
        # CPU 전체 체크
        if stats['cpu_percent_total'] > self.thresholds['cpu_total']:
            if self._should_alert('cpu_total', current_time, cooldown_delta):
                violations.append(f"CPU전체 {stats['cpu_percent_total']}%")
                self.last_threshold_alerts['cpu_total'] = current_time
                
        # CPU 앱 체크 (PM2 모드일 때만)
        if self.monitoring_mode == "PM2" and stats['cpu_percent_app'] > self.thresholds['cpu_app']:
            if self._should_alert('cpu_app', current_time, cooldown_delta):
                violations.append(f"CPU앱 {stats['cpu_percent_app']}%")
                self.last_threshold_alerts['cpu_app'] = current_time
                
        # RAM 체크
        if stats['ram_percent'] > self.thresholds['ram']:
            if self._should_alert('ram', current_time, cooldown_delta):
                violations.append(f"RAM {stats['ram_percent']}%")
                self.last_threshold_alerts['ram'] = current_time
                
        if violations:
            violations_str = ", ".join(violations)
            
            # Discord 전용 포맷으로 직접 전송 (독립적)
            discord_success = self.logger.discord.send_threshold_alert(violations_str, stats)
            
            # 로그 파일에는 간단하게 기록
            self.logger.warning("리소스 임계값 초과 감지", 
                            violations=violations_str,
                            cooldown_minutes=self.threshold_cooldown_minutes,
                            discord_sent=discord_success)
            
            return True
            
        return False

    def _should_alert(self, resource_type: str, current_time: datetime, cooldown_delta: timedelta) -> bool:
        """중복 알림 방지 체크"""
        last_alert = self.last_threshold_alerts.get(resource_type)
        if last_alert is None:
            return True  # 첫 번째 알림
        
        return (current_time - last_alert) >= cooldown_delta
    
    async def _one_second_collector(self):
        """1초마다 리소스 상태 수집"""
        self.logger.info("리소스 수집 시작", interval=f"{self.collect_interval}초")
        
        while self.is_running:
            try:
                stats = await self._get_stats_quick()
                if stats:
                    self.minute_buffer.append(stats)
                await asyncio.sleep(self.collect_interval)
            except Exception as e:
                self.logger.error("1초 수집 오류", error=str(e))
                await asyncio.sleep(self.collect_interval)

    async def _one_minute_aggregator(self):
        """N분마다 피크값 계산 및 저장"""
        while self.is_running:
            await asyncio.sleep(self.aggregate_interval)
            
            # aggregate_interval 분단위로 로깅 300 = 5분
            aggregate_name = f"{self.aggregate_interval // 60}분"
            
            if not self.minute_buffer:
                continue
                
            try:
                # N분간의 피크값 계산
                peak_stats = self._calculate_peak_stats()
                self.minute_peaks.append(peak_stats)
                
                self.logger.debug(f"{aggregate_name} 피크값 저장", **peak_stats)
                
                # 버퍼 클리어
                self.minute_buffer.clear()
                
            except Exception as e:
                self.logger.error(f"{aggregate_name} 집계 오류", error=str(e))

    def _calculate_peak_stats(self) -> Dict:
        """1분간 수집된 데이터에서 피크값 계산"""
        peak_stats = {
            'minute': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'gpu_memory_percent': 0,
            'gpu_utilization': 0,
            'cpu_percent_total': 0,
            'cpu_percent_app': 0,
            'ram_percent': 0,
            'app_memory_peak_mb': 0,
            'cache_dir_gb': 0,
            'cache_file_count': 0,
            'data_points': len(self.minute_buffer)
        }
        
        # 각 메트릭별 최대값 찾기
        for stat in self.minute_buffer:
            if stat.get('gpu'):
                peak_stats['gpu_memory_percent'] = max(
                    peak_stats['gpu_memory_percent'], 
                    stat['gpu']['memory_percent']
                )
                peak_stats['gpu_utilization'] = max(
                    peak_stats['gpu_utilization'], 
                    stat['gpu']['utilization']
                )
            
            peak_stats['cpu_percent_total'] = max(
                peak_stats['cpu_percent_total'], 
                stat['cpu_percent_total']
            )
            peak_stats['cpu_percent_app'] = max(
                peak_stats['cpu_percent_app'], 
                stat.get('cpu_percent_app', 0)
            )
            peak_stats['ram_percent'] = max(
                peak_stats['ram_percent'], 
                stat['ram_percent']
            )
            peak_stats['app_memory_peak_mb'] = max(
                peak_stats['app_memory_peak_mb'], 
                stat.get('app_memory_mb', 0)
            )
        
        # 디렉토리 크기는 마지막 값 사용
        if self.minute_buffer:
            last_stat = self.minute_buffer[-1]
            if 'cache_dir' in last_stat and last_stat['cache_dir']['exists']:
                peak_stats['cache_dir_gb'] = last_stat['cache_dir']['size_gb']
                peak_stats['cache_file_count'] = last_stat['cache_dir']['file_count']

        return peak_stats

    async def _threshold_monitor(self):
        """임계값 모니터링"""
        while self.is_running:
            try:
                if self.minute_buffer:
                    # 최근 수집된 데이터로 임계값 체크
                    latest_stats = self.minute_buffer[-1]
                    self._check_thresholds(latest_stats)
                    
                await asyncio.sleep(self.threshold_check_interval)
            except Exception as e:
                self.logger.error("임계값 모니터링 오류", error=str(e))
                await asyncio.sleep(self.threshold_check_interval)

    async def _daily_scheduler(self):
        """매일 지정된 시간에 일일 리포트 전송"""
        while self.is_running:
            try:
                now = datetime.now()
                target_time = time(hour=self.daily_report_time[0], 
                                 minute=self.daily_report_time[1])
                
                # 오늘의 목표 시간 계산
                target_datetime = datetime.combine(now.date(), target_time)
                
                # 이미 지났다면 내일로 설정
                if now >= target_datetime:
                    target_datetime += timedelta(days=1)
                
                # 대기 시간 계산
                wait_seconds = (target_datetime - now).total_seconds()
                self.logger.debug("일일 리포트 스케줄", 
                                next_report=target_datetime.strftime('%Y-%m-%d %H:%M'),
                                wait_hours=round(wait_seconds/3600, 1))
                
                # 지정된 시간까지 대기
                await asyncio.sleep(wait_seconds)
                
                # 일일 리포트 전송
                await self._send_daily_report()
                
                # 다음날을 위해 1분 대기 (중복 실행 방지)
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error("일일 스케줄러 오류", error=str(e))
                await asyncio.sleep(3600)  # 1시간 후 재시도

    async def _send_daily_report(self):
        """일일 리소스 리포트 생성 및 전송"""
        try:
            # Discord용 구조화된 데이터 생성
            report_data = self._generate_report_data()
            
            # Discord 직접 전송 (독립적)
            discord_success = self.logger.discord.send_daily_resource_report(report_data)
            if discord_success:
                self.logger.info("일일 리소스 리포트 Discord 전송 성공")
            else:
                self.logger.error("일일 리포트 Discord 전송 실패")
            
            # 로그 파일에도 기록 (간단한 형태)
            log_message = self._format_daily_report()
            self.logger.info("일일 리소스 리포트 완료", 
                            period=report_data['period'],
                            data_points=report_data['data_points'])
            
            # 리포트 발송 후 데이터 초기화
            self._clear_and_reset()
            
        except Exception as e:
            self.logger.error("일일 리포트 처리 실패", error=str(e))

    def _generate_report_data(self) -> dict:
        """Discord용 구조화된 리포트 데이터 생성"""
        if not self.minute_peaks:
            return {"period": "데이터 없음", "data_points": 0}
        
        # 전체 기간 계산
        period_start = self.last_report_time.strftime('%m-%d %H:%M')
        period_end = datetime.now().strftime('%m-%d %H:%M')
        duration_hours = round((datetime.now() - self.last_report_time).total_seconds() / 3600, 1)
        
        # 각 메트릭의 최대값과 시간 찾기
        gpu_memory_max = max(self.minute_peaks, key=lambda x: x['gpu_memory_percent'])
        gpu_util_max = max(self.minute_peaks, key=lambda x: x['gpu_utilization'])
        cpu_total_max = max(self.minute_peaks, key=lambda x: x['cpu_percent_total'])
        cpu_app_max = max(self.minute_peaks, key=lambda x: x['cpu_percent_app'])
        ram_max = max(self.minute_peaks, key=lambda x: x['ram_percent'])
        
        report_data = {
            'period': f"{period_start} ~ {period_end} ({duration_hours}시간)",
            'data_points': len(self.minute_peaks),
            'monitoring_mode': self.monitoring_mode,
            'gpu_index': self.gpu_index,
            
            # GPU 데이터
            'gpu_memory_percent': gpu_memory_max['gpu_memory_percent'],
            'gpu_memory_time': gpu_memory_max['minute'],
            'gpu_utilization': gpu_util_max['gpu_utilization'],
            'gpu_utilization_time': gpu_util_max['minute'],
            
            # CPU 데이터
            'cpu_percent_total': cpu_total_max['cpu_percent_total'],
            'cpu_total_time': cpu_total_max['minute'],
            'cpu_percent_app': cpu_app_max['cpu_percent_app'],
            'cpu_app_time': cpu_app_max['minute'],
            
            # RAM 데이터
            'ram_percent': ram_max['ram_percent'],
            'ram_time': ram_max['minute'],
        }
        
        # 앱 메모리 정보 (PM2 모드일 때)
        if self.monitoring_mode == "PM2":
            app_memory_max = max(self.minute_peaks, key=lambda x: x.get('app_memory_peak_mb', 0))
            report_data.update({
                'app_memory_peak_mb': app_memory_max.get('app_memory_peak_mb', 0),
                'app_memory_time': app_memory_max.get('minute', 'N/A')
            })
        
        # 디스크 정보 (설정된 경우)
        if self.minute_peaks and self.minute_peaks[-1].get('cache_dir_gb', 0) > 0:
            last_peak = self.minute_peaks[-1]
            first_peak = self.minute_peaks[0]
            
            report_data.update({
                'cache_dir_gb': last_peak['cache_dir_gb'],
                'cache_file_count': last_peak['cache_file_count'],
                'cache_size_change_gb': round(
                    last_peak.get('cache_dir_gb', 0) - first_peak.get('cache_dir_gb', 0), 2
                )
            })
        
        return report_data

    def _format_daily_report(self) -> str:
        """일일 리포트 메시지 포맷팅"""
        if not self.minute_peaks:
            return "수집된 데이터가 없습니다"
        
        # 전체 기간 피크값 계산
        period_start = self.last_report_time.strftime('%m-%d %H:%M')
        period_end = datetime.now().strftime('%m-%d %H:%M')
        duration_hours = round((datetime.now() - self.last_report_time).total_seconds() / 3600, 1)
        
        # 각 메트릭의 최대값 찾기
        gpu_memory_max = max(self.minute_peaks, key=lambda x: x['gpu_memory_percent'])
        gpu_util_max = max(self.minute_peaks, key=lambda x: x['gpu_utilization'])
        cpu_total_max = max(self.minute_peaks, key=lambda x: x['cpu_percent_total'])
        cpu_app_max = max(self.minute_peaks, key=lambda x: x['cpu_percent_app'])
        ram_max = max(self.minute_peaks, key=lambda x: x['ram_percent'])
        
        # 리포트 메시지 구성
        message = f"\n수집기간: {period_start} ~ {period_end} ({duration_hours}시간)\n"
        message += f"데이터포인트: {len(self.minute_peaks)}개 (1분 단위)\n"
        message += f"* GPU#{self.gpu_index} 메모리: {gpu_memory_max['gpu_memory_percent']}% [{gpu_memory_max['minute']}]\n"
        message += f"* GPU#{self.gpu_index} 사용률: {gpu_util_max['gpu_utilization']}% [{gpu_util_max['minute']}]\n"
        message += f"* CPU 전체: {cpu_total_max['cpu_percent_total']}% [{cpu_total_max['minute']}]\n"
        
        if self.monitoring_mode == "PM2":
            message += f"* CPU {self.pm2_app_name}: {cpu_app_max['cpu_percent_app']}% [{cpu_app_max['minute']}]\n"
        
        message += f"* RAM: {ram_max['ram_percent']}% [{ram_max['minute']}]\n"
        
        # 디스크 사용량 (마지막 데이터)
        if self.minute_peaks and self.minute_peaks[-1]['cache_dir_gb'] > 0:
            last_peak = self.minute_peaks[-1]
            message += f"* 디스크: {last_peak['cache_dir_gb']}GB ({last_peak['cache_file_count']:,}개 파일)"
        
        return message

    def _clear_and_reset(self):
        """리포트 발송 후 데이터 초기화"""
        self.minute_peaks.clear()
        self.minute_buffer.clear()
        self.last_report_time = datetime.now()
        self.logger.debug("리소스 모니터 리셋 완료")

    async def start_monitoring(self):
        """백그라운드 모니터링 시작"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # PM2 모드일 때 초기 프로세스 업데이트
        if self.monitoring_mode == "PM2":
            self._update_app_process()
        
        self.logger.info("리소스 모니터링 시작", 
                        mode=self.monitoring_mode,
                        collect_interval=self.collect_interval,
                        threshold_alert=self.threshold_alert,
                        daily_report=f"{self.daily_report_time[0]:02d}:{self.daily_report_time[1]:02d}")
        
        # 백그라운드 태스크들 시작
        await asyncio.gather(
            self._one_second_collector(),
            self._one_minute_aggregator(),
            self._threshold_monitor(),
            self._daily_scheduler()
        )