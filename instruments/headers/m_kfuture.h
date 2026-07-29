/****************************************************************************
 * NH투자증권 종목마스터 — 국내 선물 > KRX300선물
 *
 * @file      m_kfuture.mst
 * @url       https://www.nhplug.com/instruments/m_kfuture.mst
 * @record    50      // 레코드 크기(byte). 파일크기 % record == 0 이어야 함
 * @encoding  CP949
 * @padding   공백(0x20) 우측 · 레코드 끝 1바이트 LF(0x0A) · 파일 헤더 없음
 * @service   kfuture.c
 *
 * 파싱 주의: 반드시 'rb'(바이너리) 로 열 것. NUL 종료 문자열이 아니므로
 *           strlen 금지 — 길이 기반 슬라이싱 후 우측 공백 제거.
 ***************************************************************************/

#pragma pack(1)
typedef struct
{
    char sCode[9];                          /* @0    종목코드 <(K) + expcode[8]> */
    char sName[40];                         /* @9    종목명 <hname[40]> */
    char dummy[1];                          /* @49   레코드 종단자 (LF) <(LF)> */
}   KFUTURE;   /* sizeof = 50 */
