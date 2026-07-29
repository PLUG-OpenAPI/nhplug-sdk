/****************************************************************************
 * NH투자증권 종목마스터 — 국내 선물 > 지수선물
 *
 * @file      m_future.mst
 * @url       https://www.nhplug.com/instruments/m_future.mst
 * @record    30      // 레코드 크기(byte). 파일크기 % record == 0 이어야 함
 * @encoding  CP949
 * @padding   공백(0x20) 우측 · 레코드 끝 1바이트 LF(0x0A) · 파일 헤더 없음
 * @service   mfuture.c
 * @note      첫 레코드는 선물이 아니라 기초지수(K10111111 / KOSPI 200)
 *
 * 파싱 주의: 반드시 'rb'(바이너리) 로 열 것. NUL 종료 문자열이 아니므로
 *           strlen 금지 — 길이 기반 슬라이싱 후 우측 공백 제거.
 ***************************************************************************/

#pragma pack(1)
typedef struct
{
    char sCode[9];                          /* @0    종목코드 <code[9] (K 포함)> */
    char sName[20];                         /* @9    종목명 <name[12] + 공백8> */
    char dummy[1];                          /* @29   레코드 종단자 (LF) <(LF)> */
}   FUTURE;   /* sizeof = 30 */
