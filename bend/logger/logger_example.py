#!/usr/bin/env python3
"""
CommonLogger 사용 예시
5분 만에 이해하는 실용적인 예제들
"""

# 1. 기본 import
from logger import get_logger

def basic_usage():
    """기본 사용법"""
    print("=== 1. 기본 사용법 ===")
    
    logger = get_logger()
    
    # 로그 레벨별 사용
    logger.debug("디버깅 정보 - 개발시에만 보임")
    logger.info("일반 정보 - 서버 시작, 완료 등")
    logger.warning("주의 필요 - 메모리 부족, 재시도 등") 
    logger.error("에러 발생 - 하지만 서비스는 계속")
    logger.critical("심각한 오류 - 서비스 중단 위험")
    
    # 추가 정보와 함께 로깅
    logger.info("사용자 로그인 성공", 
               user_id="admin", 
               ip="192.168.1.100", 
               login_time="14:30:25")

def context_management():
    """컨텍스트 관리 - 추적 ID 사용"""
    print("\n=== 2. 컨텍스트 관리 (추적 ID) ===")
    
    logger = get_logger()
    
    # 방법 1: 전역 컨텍스트 설정
    logger.set_context(service="user-service", version="v2.1.0")
    logger.info("서비스 시작")      # service, version 자동 포함
    logger.info("DB 연결 완료")     # 모든 로그에 자동 포함
    
    # 방법 2: 임시 컨텍스트 (with 문 - 추천!)
    with logger.context(trace_id="req_001", user_id="john_doe"):
        logger.info("요청 처리 시작")
        logger.info("데이터 검증 완료")
        logger.info("응답 전송 완료")  # 모든 로그에 trace_id, user_id 자동 포함
    
    # with 문 밖에서는 전역 컨텍스트만 적용
    logger.info("다른 작업 진행")  # service, version만 포함
    
    # 컨텍스트 초기화
    logger.clear_context()
    logger.info("컨텍스트 초기화 후")  # 추가 정보 없음

def exception_handling():
    """예외 처리"""
    print("\n=== 3. 예외 처리 ===")
    
    logger = get_logger()
    
    try:
        # 일부러 에러 발생
        result = 10 / 0
    except ZeroDivisionError as e:
        # 스택 트레이스까지 자동 로깅
        logger.exception("나눗셈 계산 오류", 
                        operation="division",
                        numerator=10, 
                        denominator=0)

def web_api_example():
    """웹 API 서버 시나리오"""
    print("\n=== 4. 실제 사용 예시: 웹 API ===")
    
    logger = get_logger()
    
    def process_user_request(user_id, action):
        # 요청별 고유 ID로 추적
        import uuid
        request_id = str(uuid.uuid4())[:8]
        
        with logger.context(request_id=request_id, user_id=user_id):
            logger.info("요청 수신", action=action, method="POST")
            
            # 처리 과정 로깅
            logger.debug("입력 데이터 검증 시작")
            
            if action == "delete" and user_id == "admin":
                logger.warning("관리자 계정 삭제 시도", 
                             security_alert=True,
                             action_blocked=True)
                return False
            
            if action == "create":
                logger.info("사용자 생성 완료", duration_ms=150)
                return True
            else:
                logger.error("알 수 없는 작업 요청", action=action)
                return False
    
    # 여러 요청 시뮬레이션
    process_user_request("user123", "create")
    process_user_request("admin", "delete") 
    process_user_request("user456", "unknown")

def batch_job_example():
    """배치 작업 시나리오"""
    print("\n=== 5. 실제 사용 예시: 배치 작업 ===")
    
    logger = get_logger()
    
    # 배치 작업 시작
    from datetime import datetime
    batch_id = f"daily_sync_{datetime.now().strftime('%Y%m%d_%H%M')}"
    
    logger.set_context(batch_id=batch_id, job_type="user_sync")
    
    logger.info("배치 작업 시작", total_users=1000, estimated_time="10분")
    
    # 작업 진행률 로깅
    for progress in [25, 50, 75, 100]:
        logger.info("진행률 업데이트", 
                   progress_percent=progress,
                   processed_count=progress * 10,
                   status="processing")
        
        # 50% 지점에서 문제 발생 시뮬레이션
        if progress == 50:
            logger.warning("외부 API 응답 지연", 
                         api_endpoint="/external/users",
                         response_time_ms=5000,
                         retry_scheduled=True)
    
    logger.info("배치 작업 완료", 
               success_count=980,
               failed_count=20, 
               total_duration="8분 32초")
    
    logger.clear_context()

def performance_tip():
    """성능 최적화 팁"""
    print("\n=== 6. 성능 최적화 팁 ===")
    
    logger = get_logger()
    
    # 비용이 높은 로깅은 레벨 체크 후 실행
    if logger.is_enabled_for("DEBUG"):
        # 무거운 연산은 DEBUG 레벨이 활성화되어 있을 때만
        expensive_data = {"user_list": ["user1", "user2"] * 100}
        detailed_stats = f"총 {len(expensive_data['user_list'])}명 처리"
        
        logger.debug("상세 처리 정보", 
                    user_data=expensive_data,
                    stats=detailed_stats)
    else:
        # DEBUG가 비활성화되어 있으면 간단하게
        logger.info("사용자 처리 완료")

if __name__ == "__main__":
    print("🚀 CommonLogger 사용 예제")
    print("=" * 50)
    
    # 중요: 먼저 logger/log_config.py 에서 설정을 확인하세요!
    print("📝 시작 전 체크리스트:")
    print("1. logger/log_config.py에서 PROJECT_ROOT 경로 설정")
    print("2. OUTPUT_MODE를 STDOUT 또는 FILE로 선택")
    print("3. GLOBAL_LOG_LEVEL 확인 (DEBUG/INFO/WARNING/ERROR/CRITICAL)")
    print("4. Discord 알림이 필요하면 DISCORD_ENABLED=True, 웹훅 URL 설정")
    print("=" * 50)
    
    # 예제 실행
    basic_usage()
    context_management()
    exception_handling()
    web_api_example()
    batch_job_example()
    performance_tip()
    
    print("\n" + "=" * 50)
    print("🎉 모든 예제 완료!")
    print("💡 팁: 실제 프로젝트에서는 trace_id를 사용한 컨텍스트 관리를 적극 활용하세요")
    print("📁 FILE 모드 사용시 logs/ 디렉토리를 확인해보세요")
    print("🔔 Discord 알림이 활성화되어 있다면 ERROR, CRITICAL 메시지를 확인하세요")