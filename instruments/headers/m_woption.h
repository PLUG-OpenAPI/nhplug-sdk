/****************************************************************************
 * NH투자증권 종목마스터 — 국내 옵션 > 코스피200위클리옵션
 *
 * @file      m_woption.mst
 * @url       https://www.nhplug.com/instruments/m_woption.mst
 * @record    74      // 레코드 크기(byte). 파일크기 % record == 0 이어야 함
 * @encoding  CP949
 * @padding   공백(0x20) 우측 · 레코드 끝 1바이트 LF(0x0A) · 파일 헤더 없음
 * @service   optksp.c 내부
 * @note      woption.c 없음. 만기 = YYMMWW(주차)
 *
 * 파싱 주의: 반드시 'rb'(바이너리) 로 열 것. NUL 종료 문자열이 아니므로
 *           strlen 금지 — 길이 기반 슬라이싱 후 우측 공백 제거.
 ***************************************************************************/

#pragma pack(1)
typedef struct
{
    char sCode[9];                          /* @0    종목코드 <(K) + expcode[8]> */
    char sCallPut[2];                       /* @9    콜/풋 구분 <리터럴 "콜"/"풋"> | CP949 한글 2바이트 — "콜"(C4 DD) / "풋"(C7 B2). ASCII C/P 아님 */
    char sMonth[6];                         /* @11   년월(월물) <lastmonth (%06d)> | YYMMWW (년·월·주차). ※ 일자 아님 — 날짜로 파싱하면 존재하지 않는 일자가 나옴 */
    char sPrice[5];                         /* @17   행사가격 <(int)(actprice*100)> | ※ 실제 행사가 × 100 (0 좌측패딩). 예 82500 → 825.00. 반드시 /100 할 것 */
    char eATM[1];                           /* @22   ATM 구분 <atmgubun[1]> | 1:ATM 2:ITM 3:OTM */
    char dummy[51];                         /* @23   예비(50) + 레코드 종단자 <buffer 공백50 + (LF)> */
}   WOPTION;   /* sizeof = 74 */
