/****************************************************************************
 * NH투자증권 종목마스터 — 국내 선물 > 주식선물
 *
 * @file      m_stkfut.mst
 * @url       https://www.nhplug.com/instruments/m_stkfut.mst
 * @record    97      // 레코드 크기(byte). 파일크기 % record == 0 이어야 함
 * @encoding  CP949
 * @padding   공백(0x20) 우측 · 레코드 끝 1바이트 LF(0x0A) · 파일 헤더 없음
 * @service   stkfut.c
 *
 * 파싱 주의: 반드시 'rb'(바이너리) 로 열 것. NUL 종료 문자열이 아니므로
 *           strlen 금지 — 길이 기반 슬라이싱 후 우측 공백 제거.
 ***************************************************************************/

#pragma pack(1)
typedef struct
{
    char sCode[9];                          /* @0    종목코드 <(K) + expcode[8]> */
    char sName[30];                         /* @9    종목명 <hname (30B로 절단)> | 원장 원본 hname[40] 을 30바이트로 잘라 기록 — 긴 종목명은 절단됨 */
    char sEngName[30];                      /* @39   영문종목명 <ename (30B로 절단)> */
    char sStockCode[6];                     /* @69   기초자산종목코드 <undershcode[6]> */
    char sStockName[20];                    /* @75   기초자산종목명 <underhname[20] 좌측정렬> */
    char sMarketType[1];                    /* @95   코스피/코스닥 구분 <under_kpgubun[1]> | 1:코스피 2:코스닥 3:ETF (원장 필드명 under_kpgubun) */
    char dummy[1];                          /* @96   레코드 종단자 (LF) <(LF)> */
}   STKFUT;   /* sizeof = 97 */
